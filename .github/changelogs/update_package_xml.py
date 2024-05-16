# update_package_xml.py
import fnmatch
import os
import sys
import xml.etree.ElementTree as ET


def update_version(file_path, new_version):
    new_version = new_version.split('-')[0]  # remove rc version
    tree = ET.parse(file_path)
    root = tree.getroot()
    version = root.find('version')
    version.text = new_version
    tree.write(file_path, xml_declaration=True, encoding='UTF-8')


def update_version_in_setup(file_path, new_version):
    new_version = new_version.split('-')[0]  # remove rc version
    lines = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if line.startswith('version = '):
            lines[i] = f"version = '{new_version}'\n"
            break
    with open(file_path, 'w') as f:
        f.writelines(lines)


def find_files(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


if __name__ == '__main__':
    next_version = sys.argv[1]
    for file_path in find_files('package.xml', '.'):
        update_version(file_path, next_version)
    if os.path.exists('setup.py'):
        update_version_in_setup('setup.py', next_version)
