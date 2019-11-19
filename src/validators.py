import datetime
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set


class Meta:
    class Field:
        DOC_ID: str = "doc_id"
        YEAR_PUBLISHED: str = "year_published"
        DATE_BUILT: str = "date_built"
        LOCATION_NAME: str = "location_name"
        LOCATION_LATLONG: str = "location_latlong"
        DATE_COLLECTED: str = "date_collected"
        DATE_PUBLISHED: str = "date_published"
        URI: str = "uri"

    REQUIRED_FIELDS = {Field.DOC_ID}
    OPTIONAL_FIELDS: Set[str] = {Field.YEAR_PUBLISHED, Field.DATE_BUILT,
                                 Field.LOCATION_NAME, Field.LOCATION_LATLONG,
                                 Field.DATE_COLLECTED}
    PREFERRED_FIELDS: Set[str] = {Field.DATE_PUBLISHED, Field.URI}
    ALL_FIELDS = REQUIRED_FIELDS.union(OPTIONAL_FIELDS).union(PREFERRED_FIELDS)


@dataclass
class TestReport:
    test_name: str
    passed: bool = True
    fail_messages: List[str] = field(default_factory=list)

    def __iadd__(self, o):
        self.passed = self.passed and o.passed
        if not o.passed and len(o.fail_messages) > 0:
            self.fail_messages += o.fail_messages
        return self


def check_correct_prefix(p: Path) -> TestReport:
    namespace = p.name
    t = TestReport(test_name="Content files prefix")
    for child in p.iterdir():
        if child.suffix == "":
            if not child.name.startswith(namespace):
                t.passed = False
                msg = "The name of file {} should start with the namespace {}".format(
                    child, namespace)
                t.fail_messages.append(msg)
    return t


def check_auxiliary_files(p: Path) -> TestReport:
    namespace = p.name
    t = TestReport(test_name="Auxiliary files")
    auxiliary_files = [namespace + ".jsonl", "LICENSE"]
    for a in auxiliary_files:
        meta_path = p / a
        if not meta_path.exists():
            t.passed = False
            msg = "File {} does not exist".format(a)
            t.fail_messages.append(msg)
    return t


def check_set(file_set, error_msg) -> TestReport:
    t = TestReport(test_name="")
    if len(file_set) > 0:
        t.passed = False
        for f in file_set:
            t.fail_messages.append(error_msg.format(f))
    return t


def check_all_files_in_metadata(p: Path) -> TestReport:
    namespace = p.name
    t = TestReport(test_name="Test files manifest")
    actual_doc_ids: Set[str] = set()
    expected_doc_ids: Set[str] = set()
    for child in p.iterdir():
        if child.suffix == "":
            actual_doc_ids.add(child.name)
    meta_file = p / (namespace + ".jsonl")
    with meta_file.open("r") as in_meta:
        for line in in_meta:
            current_meta = json.loads(line)
            doc_id = current_meta[Meta.Field.DOC_ID]
            expected_doc_ids.add(doc_id)

    undeclared = actual_doc_ids - expected_doc_ids
    nonexistent = expected_doc_ids - actual_doc_ids
    shared = actual_doc_ids.intersection(expected_doc_ids)
    t.passed += len(shared)
    msg_undeclared = "File {} not declared in meta file"
    msg_nonexistent = "File {} declared in meta file, but does not exist"

    t += check_set(undeclared, msg_undeclared)
    t += check_set(nonexistent, msg_nonexistent)

    return t


import re

matcher_Z = re.compile("[A-Z]{3}")  # tz name
matcher_z = re.compile("[+-]\d{4}")  # tz offset
matcher_year = re.compile("\s([\d]{4})")  # find year
msg_year = "Year {} is higher than current year {} in meta date: {}"
msg_missing_Z = "Missing timezone as string from meta date: {}"
msg_missing_z = "Missing timezone as offset from meta date: {}"
msg_missing_Y = "Missing year in meta date: {}"


def check_datetime(s: str) -> TestReport:
    # Time zone checks are done by regular expression since danish locale is
    # inconsistent across OS'es (Linux vs macOS)

    t = TestReport(test_name="")
    if s is not None:
        m = matcher_Z.search(s)
        if m is None:
            t.passed = False
            t.fail_messages.append(msg_missing_Z.format(s))
        m = matcher_z.search(s)
        if m is None:
            t.passed = False
            t.fail_messages.append(msg_missing_z.format(s))
        m = matcher_year.search(s)
        if m is None:
            t.passed = False
            t.fail_messages.append(msg_missing_Y.format(s))
        else:
            current_year: int = int(datetime.datetime.now().strftime("%Y"))
            year = m.group(1)
            year = int(year)
            if year > current_year:
                t.passed = False
                t.fail_messages.append(msg_year.format(year, current_year, s))
    return t


def check_metadata_fields(p: Path) -> TestReport:
    current_year: int = int(datetime.datetime.now().strftime("%Y"))
    namespace = p.name
    t = TestReport(test_name="Fields in metadata")
    meta_file = p / (namespace + ".jsonl")
    with meta_file.open("r") as in_meta:
        for line in in_meta:
            current_meta = json.loads(line)
            doc_id = current_meta[Meta.Field.DOC_ID]
            keys = set(current_meta.keys())
            missing_required = Meta.REQUIRED_FIELDS - keys
            required_msg = "Metadata missing field {{}} for doc_id = {d}"
            t += check_set(missing_required, required_msg.format(d=doc_id))

            illegal_fields = keys - Meta.ALL_FIELDS
            illegal_msg = "Metadata contains undocumented field {{}} for doc_id = {d}"
            t += check_set(illegal_fields, illegal_msg.format(d=doc_id))

            # Check year published
            year_published = current_meta.get(Meta.Field.YEAR_PUBLISHED, None)
            if year_published is not None:
                year_published = int(year_published)
                if year_published > current_year:
                    t.passed = False
                    t.fail_messages.append("{}: {} is in the future!".format(
                        Meta.Field.YEAR_PUBLISHED, year_published))

            # Check all dates for correct content
            date_built = current_meta.get(Meta.Field.DATE_BUILT, None)
            t += check_datetime(date_built)

            date_collected = current_meta.get(Meta.Field.DATE_COLLECTED, None)
            t += check_datetime(date_collected)

            date_published = current_meta.get(Meta.Field.DATE_PUBLISHED, None)
            t += check_datetime(date_published)

    return t


tests = [check_correct_prefix, check_auxiliary_files,
         check_all_files_in_metadata, check_metadata_fields]
