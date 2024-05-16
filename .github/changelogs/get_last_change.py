# get_latest_change.py
import argparse

from changelog import Changelog


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    changelog = Changelog(args.filename)
    latest_change = changelog.get_latest_change()

    print(latest_change)


if __name__ == '__main__':
    main()
