# get_new_version.py
import sys

from packaging import version


def get_next_version(base_version, update_type):
    ver_base = version.parse(base_version)
    if update_type == 'patch':
        next_ver = f'{ver_base.major}.{ver_base.minor}.{ver_base.micro + 1}'
    elif update_type == 'minor':
        next_ver = f'{ver_base.major}.{ver_base.minor + 1}.0'
    elif update_type == 'major':
        next_ver = f'{ver_base.major + 1}.0.0'
    elif update_type == 'rc':
        if ver_base.is_prerelease:
            # Increase the RC version
            next_ver = f'{ver_base.base_version}-rc{ver_base.pre[1] + 1}'
        else:
            # If it's not a pre-release, start the RC versioning
            next_ver = f'{ver_base.base_version}-rc1'
    elif update_type == 'rc1':
        # Reset the RC version to 1
        next_ver = f'{ver_base.base_version}-rc1'
    elif update_type == 'rc_remove':
        # Remove the RC version
        next_ver = ver_base.base_version
    else:   # none
        next_ver = base_version
    return next_ver


if __name__ == '__main__':
    base_version = sys.argv[1]
    update_type = sys.argv[2]
    next_version = get_next_version(base_version, update_type)
    print(next_version)
