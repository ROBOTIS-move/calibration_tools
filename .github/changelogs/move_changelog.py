# move_changelog.py
import argparse

from changelog import Changelog


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('new_version')
    parser.add_argument('source_file')
    parser.add_argument('target_file')
    args = parser.parse_args()

    changelog = Changelog(args.target_file)
    changelog_pre = Changelog(args.source_file)

    merged_changes = changelog_pre.merge_changes()
    changelog.add_change(args.new_version, merged_changes)
    changelog.write_file()
    changelog_pre.reset_file()


if __name__ == '__main__':
    main()
