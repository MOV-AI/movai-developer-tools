"""Module that contains a set of functions to ease interacting with the metadata backup functionality"""
from movai_developer_tools.utils.logger import logging
from movai_developer_tools.movmisc.spawner.operation_executer import Spawner
import os
from pathlib import Path
import sys


def get_manifest_files_in_spawner(args) -> list:
    """Get a list of manifest.txt file locations inside the spawner container"""
    # Container userspace bind location
    container_bind_dir = "/opt/mov.ai/user"
    # Manifest regex
    manifest_regex = "*manifest.txt"
    # Instanciate spawner class
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

    # Get all manifest files recursively in the host
    path = Path(cwd)
    manifest_files_in_host = map(
        lambda x: str(x.absolute()), path.rglob(manifest_regex)
    )
    # Convert to spawner container mounted paths
    manifest_files_in_spawner = list(
        map(
            lambda x: x.replace(host_userspace, container_bind_dir),
            manifest_files_in_host,
        )
    )

    return manifest_files_in_spawner


def iterative_backup_action(args, manifest_files_in_spawner) -> None:
    """Iteratively import/export/delete (args.command) based on manifest_files_in_spawner"""
    # Instanciate spawner class
    spawner_cls = Spawner()

    # Backup options for import
    backup_opts = "-i -c -f"

    # If command is remove update backup_opts
    if args.command == "remove":
        backup_opts = backup_opts.replace(" -f", "")

    # Import metadata using each manifest
    for manifest in manifest_files_in_spawner:
        # Log
        logging.info(f"{args.command.upper()}ING metadata present in {manifest}")
        # Get manifest file directory and metadata directory (project, -p arg on backup tool)
        manifest_dir_in_spawner = manifest.replace("/manifest.txt", "")
        metadata_dir = manifest_dir_in_spawner + "/metadata"

        # If PYTHONPATH is not set, scenes fail to export
        args.env = [
            "PYTHONPATH=/opt/mov.ai/app:/opt/ros/melodic/lib/python3/dist-packages:/opt/ros/noetic/lib/python3/dist-packages"
        ]
        # Non silent operation
        args.silent = False

        # Bypass [Y/n/[A]ll/[K]eep all] command for export command
        args.cmd = f"python3 -m tools.backup -p {metadata_dir} -a {args.command} -m {manifest} {backup_opts}"
        if args.command == "export":
            args.cmd = "echo 'A' | " + args.cmd

        # Execute if not dry run
        if not args.dry:
            spawner_cls.spawner_exec(args)
        else:
            logging.info("Dry run mode, please remove the dry run args to execute")


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
    parser.add_argument(
        "-dry",
        "--dry",
        "--dry-run",
        help="Dry run commands (import, export, delete) without modifiying any files",
        action="store_true",
    )
    args = parser.parse_args()

    print(f"Manifest files in spawner: {get_manifest_files_in_spawner(args)}")
