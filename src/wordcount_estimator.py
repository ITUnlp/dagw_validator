import argparse
import logging
import sys
from pathlib import Path
from typing import Dict


class ParserWithUsage(argparse.ArgumentParser):
    """ A custom parser that writes error messages followed by command line usage documentation."""

    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                        level=logging.INFO,
                        datefmt='%Y%m%d %H:%M:%S')
    parser = ParserWithUsage()
    parser.description = "Estimates the number of words in DKGW"
    parser.add_argument("input",
                        help="Path to DKGW directory")

    args = parser.parse_args()
    logging.info("STARTED")
    path: Path = Path(args.input)
    goal = 1_000_000_000
    goal_as_str = "{:,}".format(goal).replace(",", " ")

    word_count: Dict[str, float] = {}
    section_path = path / "sektioner"
    for section in section_path.iterdir():
        if section.is_dir() and not section.name.startswith("."):
            namespace = section.name
            logging.info("Counting in section {}".format(namespace))
            section_word_count = 0
            for file in section.glob("{}_*".format(namespace)):
                ext = file.suffix
                if len(ext) == 0:
                    with file.open("r", encoding="utf8") as content_file:
                        content = content_file.read()
                        tokens = content.split(" ")
                        section_word_count += len(tokens)

            word_count[namespace] = section_word_count

    logging.info("#### Word count by section ####")
    msg = "{} –– words: {} –– % of goal: {:.2f}"
    total_wc = 0
    for section, wc in word_count.items():
        total_wc += wc
        section_of_goal = wc / goal * 100
        word_count_str = "{:,}".format(wc).replace(",", " ")
        logging.info(msg.format(section, word_count_str, section_of_goal))

    total_wc_str = "{:,}".format(total_wc).replace(",", " ")
    logging.info("#### TOTAL ####")
    logging.info("Estimated word count: {}".format(total_wc_str))

    percentage_of_goal = total_wc / goal * 100
    logging.info(
        "That is: {:.2f}% of the {} word goal".format(percentage_of_goal, goal_as_str))
    logging.info("DONE")


if __name__ == "__main__":
    main()
