#!/usr/bin/python3
import os
import fnmatch
import re
from argparse import ArgumentParser
import json
import sys


def main():
    config = {"ignore_deletion": [], "ignore_deletion_if_recreation": [], "unauthorized_deletion": []}

    args = parse_argument()
    if args.config:
        config = {**config, **load_config(args.config)}
    else:
        print("No config provided. Default values used.")

    ignored_from_env_var = parse_ignored_from_env_var()

    all_deletion = get_resource_deletion()

    # List of all deletion which is not whitelisted or commented. Fail if not empty
    unauthorized_deletion = []

    for resource in all_deletion:
        resource_address = resource["address"]
        if is_resource_match_any(resource_address, config["unauthorized_deletion"]):
            print(f'Resource {resource_address} can not be destroyed for any reason')
            exit(1)
        if is_resource_match_any(resource_address, config["ignore_deletion"]):
            continue
        if is_resource_recreate(resource) and is_resource_match_any(resource_address,
                                                                    config["ignore_deletion_if_recreation"]):
            continue
        if is_resource_match_any(resource_address, ignored_from_env_var):
            print(f"deletion of {resource_address} authorized by env var.")
            continue
        if is_deletion_commented(resource["type"], resource["name"]):
            print(f"deletion of {resource_address} authorized by comment")
            continue
        if is_deletion_in_disabled_file(resource["type"], resource["name"]):
            print(f"deletion of {resource_address} authorized by disabled file feature")
            continue
        unauthorized_deletion.append(resource_address)

    if unauthorized_deletion:
        print("Unauthorized deletion detected for those resources:")
        for deletion in unauthorized_deletion:
            print(f" - {deletion}")
        print("If you really want to delete those resources: comment it or export this environment variable:")
        print(f"export TERRASAFE_ALLOW_DELETION=\"{';'.join(unauthorized_deletion)}\"")
        exit(1)
    else:
        print("0 unauthorized deletion detected")


def parse_argument():
    args_parser = ArgumentParser()
    args_parser.add_argument("--config",
                             help="specify the path to the terrasafe config",
                             required=False
                             )
    return args_parser.parse_args()


def load_config(config_path):
    json_file = open(config_path)
    config = json.load(json_file)
    print("Config loaded from", config_path)
    json_file.close()
    return config


def parse_ignored_from_env_var():
    ignored = os.environ.get("TERRASAFE_ALLOW_DELETION")
    if ignored:
        return ignored.split(";")
    return []


def get_resource_deletion():
    data = json.load(sys.stdin)
    # check format version
    if data["format_version"].split(".")[0] != "0":
        print("Only format major version 0 is supported")
        exit(1)
    if "resource_changes" in data:
        resource_changes = data["resource_changes"]
    else:
        resource_changes = []

    return list(filter(has_delete_action, resource_changes))


def has_delete_action(resource):
    return "delete" in resource["change"]["actions"]


def is_resource_match_any(resource_address, pattern_list):
    for pattern in pattern_list:
        pattern = re.sub(r"\[(.+?)\]", "[[]\g<1>[]]", pattern)
        if fnmatch.fnmatch(resource_address, pattern):
            return True
    return False


def is_resource_recreate(resource):
    actions = resource["change"]["actions"]
    return "create" in actions and "delete" in actions


def is_deletion_commented(resource_type, resource_name):
    regex = re.compile(rf'(#|//)\s*resource\s*\"{resource_type}\"\s*\"{resource_name}\"')
    tf_files = get_all_files(".tf")
    for filepath in tf_files:
        with open(filepath, 'r') as file:
            for line in file:
                if regex.match(line):
                    return True
    return False


def is_deletion_in_disabled_file(resource_type, resource_name):
    regex = re.compile(rf'\s*resource\s*\"{resource_type}\"\s*\"{resource_name}\"')
    tf_files = get_all_files(".tf.disabled")
    for filepath in tf_files:
        with open(filepath, 'r') as file:
            for line in file:
                if regex.match(line):
                    return True


def get_all_files(extension):
    res = []
    for root, dirs, file_names in os.walk("."):
        for file_name in file_names:
            if fnmatch.fnmatch(file_name, "*" + extension):
                res.append(os.path.join(root, file_name))
    return res


if __name__ == '__main__':
    main()
