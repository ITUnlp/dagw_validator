import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set


@dataclass
class TestReport:
    test_name: str
    passed: int = 0
    failed: int = 0
    fail_messages: List[str] = field(default_factory=list)

    def __iadd__(self, o):
        self.passed += o.passed
        self.failed += o.failed
        if o.failed > 0:
            self.fail_messages += o.fail_messages
        return self


def check_correct_prefix(p: Path) -> TestReport:
    namespace = p.name
    t = TestReport(test_name="Content files prefix")
    for child in p.iterdir():
        if child.suffix == "":
            if child.name.startswith(namespace):
                t.passed += 1
            else:
                t.failed += 1
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
        if meta_path.exists():
            t.passed += 1
        else:
            t.failed += 1
            msg = "File {} does not exist".format(a)
            t.fail_messages.append(msg)
    return t


def check_set(file_set, error_msg):
    t = TestReport(test_name="")
    if len(file_set) > 0:
        t.failed += len(file_set)
        for f in file_set:
            t.fail_messages.append(error_msg.format(f))
    return t


def check_all_files_in_metadata(p: Path) -> TestReport:
    namespace = p.name
    t = TestReport(test_name="Content files prefix")
    actual_doc_ids: Set[str] = set()
    expected_doc_ids: Set[str] = set()
    for child in p.iterdir():
        if child.suffix == "":
            actual_doc_ids.add(child.name)
    meta_file = p / (namespace + ".jsonl")
    with meta_file.open("r") as in_meta:
        for line in in_meta:
            current_meta = json.loads(line)
            doc_id = current_meta["doc_id"]
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


def check_metadata_fields(p: Path) -> TestReport:
    namespace = p.name
    t = TestReport(test_name="Fields in metadata")
    meta_file = p / (namespace + ".jsonl")
    required_fields = {"doc_id"}
    optional_fields = {"year_published", "date_built", "location_name",
                       "location_latlong", "date_collected"}
    preferred_fields = {"date_published", "uri"}
    all_fields = required_fields.union(optional_fields).union(preferred_fields)
    with meta_file.open("r") as in_meta:
        for line in in_meta:
            current_meta = json.loads(line)
            doc_id = current_meta["doc_id"]
            keys = set(current_meta.keys())
            missing_required = required_fields - keys
            required_msg = "Metadata missing field {{}} for doc_id = {d}"
            t += check_set(missing_required, required_msg.format(d=doc_id))

            illegal_fields = keys - all_fields
            illegal_msg = "Metadata contains undocumented field {{}} for doc_id = {d}"
            t += check_set(illegal_fields, illegal_msg.format(d=doc_id))

    return t


tests = [check_correct_prefix, check_auxiliary_files,
         check_all_files_in_metadata, check_metadata_fields]
