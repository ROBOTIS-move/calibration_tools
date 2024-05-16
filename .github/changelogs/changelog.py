# changelog.py
import datetime
import re


class Changelog:

    def __init__(self, filename):
        self.filename = filename
        self.header = []
        self.changes = []
        self.read_file()

    def parse_version(self, version):
        match = re.match(r'(\d+)\.(\d+)\.(\d+)(?:-rc(\d+))?', version)
        if match:
            major, minor, patch, rc_num = match.groups()
            return int(major), int(minor), int(patch), int(rc_num) if rc_num else 0
        else:
            return 0, 0, 0, 0

    def read_file(self):
        with open(self.filename, 'r') as file:
            lines = file.readlines()
        self.header = lines[:3]
        changes = lines[3:]
        i = 0
        while i < len(changes):
            line = changes[i].strip()
            if line:  # skip empty lines
                version_date = line.replace(' ', '').split('(')
                version = version_date[0]
                date = version_date[1][:-1] if len(version_date) > 1 else None
                i += 2
                change_list = []
                while i < len(changes) and changes[i].strip().startswith(('* ', '- ')):
                    change_list.append(changes[i].strip()[2:])
                    i += 1
                self.changes.append((version, date, change_list))
            i += 1
        self.changes.sort(key=lambda change: self.parse_version(change[0]), reverse=True)

    def add_change(self, new_version, new_changes):
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        for i, (version, _, change_list) in enumerate(self.changes):
            if version == new_version:
                change_list.extend(new_changes)
                self.changes[i] = (new_version, date_str, change_list)
                break
        else:
            self.changes.append((new_version, date_str, new_changes))
        self.changes.sort(key=lambda change: self.parse_version(change[0]), reverse=True)

    def merge_changes(self):
        merged_changes = []
        for change in self.changes:
            merged_changes.extend(change[2])
        return merged_changes

    def get_changes(self):
        return self.changes

    def get_latest_version(self):
        return self.changes[0][0] if self.changes else None

    def get_latest_change(self):
        if self.changes:
            change = self.changes[0]
            change_str = f'{change[0]} ({change[1]})\n------------------\n'
            for item in change[2]:
                change_str += f'* {item}\n'
            return change_str
        else:
            return None

    def write_file(self):
        with open(self.filename, 'w') as file:
            file.writelines(self.header)
            for change in self.changes:
                file.write(f'{change[0]} ({change[1]})\n------------------\n')
                for item in change[2]:
                    file.write(f'* {item}\n')
                file.write('\n')

    def reset_file(self):
        with open(self.filename, 'w') as file:
            file.writelines(self.header)

    def get_changes_in_version_range(self, start_version, end_version):
        start_version_tuple = self.parse_version(start_version)
        end_version_tuple = self.parse_version(end_version)

        changes_in_range = []
        for version, date, change_list in self.changes:
            version_tuple = self.parse_version(version)
            if start_version_tuple <= version_tuple <= end_version_tuple:
                changes_in_range.append((version, date, change_list))

        return changes_in_range

    def get_change_by_version(self, version):
        for change in self.changes:
            if change[0] == version:
                return change

        return None
