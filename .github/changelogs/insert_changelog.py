# insert_changelog.py
import argparse
import re

from changelog import Changelog


def parse_changes(text):
    match = re.search(r'### ChangeLogs(.*?)(###|$)', text, re.DOTALL)
    print(match)
    if match:
        changes = match.group(1)
        items = re.findall(r'[\*\-]\s*(.*?)(?=\r?\n)', changes)
        print(items)
        return [item.strip() for item in items]  # remove leading and trailing whitespace
    else:
        return []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('new_version')
    parser.add_argument('file_name')
    parser.add_argument('change_text')
    parser.add_argument('author')
    parser.add_argument('pr_url')
    args = parser.parse_args()

    changelog = Changelog(args.file_name)
    changes = parse_changes(args.change_text)
    changes = [f'{change} by @{args.author} in {args.pr_url}' for change in changes]
    changelog.add_change(args.new_version, changes)
    changelog.write_file()


if __name__ == '__main__':
    main()
