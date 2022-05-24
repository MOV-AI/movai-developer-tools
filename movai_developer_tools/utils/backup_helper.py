"""Module that contains a set of functions to ease interacting with the metadata backup functionality"""
from movai_developer_tools.utils.logger import logging
from movai_developer_tools.movmisc.spawner.operation_executer import Spawner
import os
import sys


def get_manifest_files_in_spawner(args) -> list:
    """Get a list of manifest.txt file locations inside the spawner container"""
    # Container userspace bind location
    container_bind_dir = "/opt/mov.ai/user"
    spawner_cls = Spawner()

    # Run spawner container command with args
    # Make required args for spawner_exec method
    args.silent = True
    args.user = "movai"
    args.env = []
    host_userspace = spawner_cls.get_spawner_userspace_dir(args)

    # Check provided directory is inside the userspace
    cwd = os.getcwd()
    if host_userspace not in cwd:
        logging.error(
            f"Directory to be used must be inside the userspace: {host_userspace}"
        )
        sys.exit(1)

    # Get path in spawner
    dir_in_spawner = container_bind_dir + cwd.replace(host_userspace, "")
    # Get all manifest files found in child directories
    args.cmd = f"find {dir_in_spawner} -name 'manifest.txt'"
    manifest_files_in_spawner = spawner_cls.spawner_exec(args).decode("ascii").split()

    return manifest_files_in_spawner


if __name__ == "__main__":
    """Test this script"""
    import argparse

    parser = argparse.ArgumentParser(
        description="This component containes helper scripts used with the backup component when developing with MOV.AI"
    )
    parser.add_argument(
        "--silent",
        help="Silence the output of commands. Used when commands are used internally to silence the output",
        action="store_true",
    )
    parser.add_argument(
        "--cmd",
        help="Command to be executed in the spawner",
        default="echo 'Hi there, I am an echo being executed in the spawner container. Please use [--cmd EXEC_COMMAND] to specify the command you want to run'",
    )
    parser.add_argument(
        "--user",
        help="User to execute docker exec command as. Default: movai",
        default="movai",
    )
    parser.add_argument(
        "--env",
        help="A dictionary or a list of strings in the following format 'PASSWORD=xxx' 'USER=xxx'",
        nargs="+",
        default=[],
    )
    args = parser.parse_args()

    print(f"Manifest files in spawner: {get_manifest_files_in_spawner(args)}")
