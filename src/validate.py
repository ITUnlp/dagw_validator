import argparse
import logging
import sys
from pathlib import Path

from src.validators import check_correct_prefix, tests


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
    path = Path(args.input)

    results = []
    for t in tests:
        r = t(path)
        results.append(r)

    total_passed = sum([t.passed for t in results])
    total_failed = sum([t.failed for t in results])
    error_msg = []
    for t in results:
        error_msg += t.fail_messages
    total_tests = total_failed + total_passed
    logging.info("Tests passed: {} of {}".format(total_passed, total_tests))
    logging.info("Tests failed: {} of {}".format(total_failed, total_tests))
    for m in error_msg:
        logging.error(m)
    logging.info("DONE")


if __name__ == "__main__":
    main()
