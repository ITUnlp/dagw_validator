import argparse
import logging
import sys
from pathlib import Path
from typing import List

from src.validators import tests, TestReport


class ParserWithUsage(argparse.ArgumentParser):
    """ A custom parser that writes error messages followed by command line usage documentation."""

    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                        level=logging.INFO,
                        datefmt='%m/%d/%Y %H:%M:%S')
    parser = ParserWithUsage()
    parser.description = "Validates a specific section of DKGW"
    parser.add_argument("--input",
                        help="Path to directory containing the section",
                        required=True)

    args = parser.parse_args()
    logging.info("STARTED")
    path: Path = Path(args.input)
    logging.info("Validating section" + path.name)
    results: List[TestReport] = [func(path) for func in tests]

    tests_passed: List[TestReport] = [t for t in results if t.passed is True]
    tests_failed: List[TestReport] = [t for t in results if t.passed is False]
    total_tests: int = len(tests_failed) + len(tests_passed)
    logging.info(
        "Passed {} of {} tests: {}".format(len(tests_passed), total_tests,
                                           [t.test_name for t in
                                            tests_passed]))
    logging.info(
        "Failed {} of {} tests: {}".format(len(tests_failed), total_tests,
                                           [t.test_name for t in
                                            tests_failed]))

    for t in results:
        for m in t.fail_messages:
            logging.error(m)

    logging.info("DONE")


if __name__ == "__main__":
    main()
