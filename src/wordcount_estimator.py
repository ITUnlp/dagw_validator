"""
Estimates the number of works in DKGW.
"""
import argparse
from dataclasses import dataclass, field
import logging
from pathlib import Path
import sys
from typing import Dict, Optional, Union


class ParserWithUsage(argparse.ArgumentParser):
    """ A custom parser that writes error messages followed by command line usage documentation."""

    def error(self, message) -> None:
        """
        Prints error message and help.
        :param message: error message to print
        """
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


@dataclass()
class Stats:
    goal: int
    count_by_section: Dict[str, int] = field(default_factory=dict)
    total_words: int = 0

    def get_percentage_of_goal(self, section: Union[str, None]) -> Optional[float]:
        """
        Calculates the percentage of final goal for the given section.
        :param section: section to analise if None, returns total
        :return: percentage of goal
        """
        if section is not None and section not in self.count_by_section:
            return None
        else:
            if section is None:
                count = self.total_words
            else:
                count = self.count_by_section[section]
            return count * 100 / self.goal

    def add_to_section(self, section: str, count: int) -> None:
        """
        Adds count to section
        :param section: section name
        :param count: count
        """
        assert count >= 0
        if section not in self.count_by_section:
            self.count_by_section[section] = count
        else:
            self.count_by_section[section] += count
        self.total_words += count


def main():
    """
    Main method
    """
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO,
                        datefmt='%m/%d/%Y %H:%M:%S')
    parser = ParserWithUsage()
    parser.description = "Estimates the number of words in DKGW"
    parser.add_argument("input", help="Path to DKGW directory", type=Path)

    args = parser.parse_args()
    logging.info("STARTED")
    path: Path = Path(args.input)
    goal = 1_000_000_000
    goal_as_str = "{:,}".format(goal).replace(",", " ")

    stats = Stats(goal=goal)
    section_path = path / "sektioner"
    for section in section_path.iterdir():
        if section.is_dir() and not section.name.startswith("."):
            namespace = section.name
            logging.info(f"Counting in section {namespace}")
            for file in section.glob(f"{namespace}_*"):
                ext = file.suffix
                if len(ext) == 0:
                    try:
                        with file.open("r", encoding="utf8") as content_file:
                            content = content_file.read()
                            tokens = content.split(" ")
                            stats.add_to_section(namespace, len(tokens))
                    except UnicodeDecodeError:
                        logging.error(f"File {file} is not UTF-8 encoded")
            percentage_of_goal = stats.get_percentage_of_goal(namespace)
            logging.info(f"\tSection: {percentage_of_goal:.2f}")
            total_percentage_of_goal = stats.get_percentage_of_goal(None)
            logging.info(f"\tTotal: {total_percentage_of_goal:.2f}")

    logging.info("#### Word count by section ####")
    msg = "{} –– words: {} –– % of goal: {:.2f}"
    for section, section_count in stats.count_by_section.items():
        section_of_goal = stats.get_percentage_of_goal(section)
        word_count_str = f"{section_count:,}".replace(",", " ")
        logging.info(msg.format(section, word_count_str, section_of_goal))

    total_wc_str = f"{stats.total_words:,}".replace(",", " ")
    logging.info("#### TOTAL ####")
    logging.info(f"Estimated word count: {total_wc_str}")

    percentage_of_goal = stats.get_percentage_of_goal(None)
    logging.info(f"That is: {percentage_of_goal:.2f}% of the {goal_as_str} word goal")
    logging.info("DONE")


if __name__ == "__main__":
    main()
