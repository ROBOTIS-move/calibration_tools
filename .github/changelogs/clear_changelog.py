# clear_changelog.py
import argparse

from changelog import Changelog


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source_file')
    args = parser.parse_args()

    changelog = Changelog(args.source_file)
    changelog.reset_file()


if __name__ == '__main__':
    main()
