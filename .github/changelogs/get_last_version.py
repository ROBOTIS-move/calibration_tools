# get_latest_version.py
import argparse

from changelog import Changelog


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    changelog = Changelog(args.filename)
    latest_version = changelog.get_latest_version()

    print(latest_version)


if __name__ == '__main__':
    main()
