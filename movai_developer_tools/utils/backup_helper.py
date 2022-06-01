"""Module that contains a set of functions to ease interacting with the metadata backup functionality"""
from movai_developer_tools.utils import logger
from movai_developer_tools.movcontainer.spawner.operation_executer import Spawner
import pathlib
import sys


class BackupHelper:
    def __init__(self, args) -> None:
        """Constructor for backup helper class"""
        # Container userspace bind location
        self.userspace_bind_dir = "/opt/mov.ai/user"
        # Metadata install location in spawner
        self.metadata_install_dir = "/opt/ros/${ROS_DISTRO}/share"
        # Manifest regex
        self.manifest_regex = "manifest.txt"
        # Instanciate spawner class
        self.spawner_cls = Spawner(args)
        # Pass args as instance variable
        self.args = args
        # Run spawner container command with args
        self.args.silent = True
        self.args.user = "movai"
        self.args.env = []
        self.host_userspace = self.spawner_cls.get_userspace_dir()

    def get_installed_manifest_files(self) -> map:
        """Return a map object of manifest files that are already installed by packages in the container"""
        # Make required args for exec method
        self.args.cmd = f"find {self.metadata_install_dir} -name {self.manifest_regex}"
        # User docker exec
        # TODO: Alternative for docker exec
        _, manifest_files_in_spawner = self.spawner_cls.exec_run().decode().split()
        # Add fix for: !---Thenameofthepackage.--: No such file or directory error
        # Quote every manifest paths
        manifest_files_in_spawner = list(
            map(lambda x: "'" + x + "'", manifest_files_in_spawner)
        )
        return manifest_files_in_spawner

    def get_valid_directory(self):
        """Validate if the current working directory (or given directory, args.directory) is in the host userspace. Return directory Path if good."""
        # If user provides directory argument use that as root dir, else use CWD
        if self.args.directory:
            working_directory = pathlib.Path(self.args.directory).resolve()
        else:
            working_directory = pathlib.Path.cwd().resolve()

        # Check provided directory is inside the userspace
        if self.host_userspace not in str(working_directory):
            logger.error(
                f"Directory to be used must be inside the userspace. Use the below command: \ncd {self.host_userspace}"
            )
            sys.exit(1)
        else:
            return working_directory

    def get_manifest_files_in_host(self) -> map:
        """Return a map object of manifest files found in the host"""
        # Get all manifest files recursively in the host
        working_directory = self.get_valid_directory()
        manifest_files_in_host = map(
            lambda x: str(x.absolute()), working_directory.rglob(self.manifest_regex)
        )
        return manifest_files_in_host

    def map_paths_host_to_container(self) -> map:
        """Map paths from host to the ones mounted in the container"""
        manifest_files_in_host = self.get_manifest_files_in_host()
        # Convert to spawner container mounted paths
        manifest_files_in_spawner = map(
            lambda x: x.replace(self.host_userspace, self.userspace_bind_dir),
            manifest_files_in_host,
        )
        return manifest_files_in_spawner

    def get_manifest_files_in_spawner(self) -> list:
        """Get a list of manifest.txt file locations inside the spawner container"""
        # In re-install get list inside the install location in spawner
        if self.args.command == "re-install":
            manifest_files_in_spawner = self.get_installed_manifest_files()
            # Re-install is not supported by the backup tools directly, it is actually import
            self.args.command = "import"
        else:
            manifest_files_in_spawner = self.map_paths_host_to_container()
        return manifest_files_in_spawner

    def iterative_backup_action(self) -> None:
        """Iteratively import/export/remove (self.args.command) based on manifest_files_in_spawner"""
        # Get manifest files in the spawner
        manifest_files_in_spawner = self.get_manifest_files_in_spawner()

        # Backup options for import
        backup_opts = "-i -c -f"

        # If command is remove update backup_opts
        if self.args.command == "remove":
            backup_opts = backup_opts.replace(" -f", "")

        # Import metadata using each manifest
        for manifest in manifest_files_in_spawner:
            # Log
            logger.info(
                f"{self.args.command.upper()}ING metadata present in {manifest}"
            )
            # Get manifest file directory and metadata directory (project, -p arg on backup tool)
            manifest_dir_in_spawner = manifest.replace("/manifest.txt", "")
            metadata_dir = manifest_dir_in_spawner + "/metadata"

            # If PYTHONPATH is not set, scenes fail to export
            self.args.env = {
                "PYTHONPATH": "/opt/mov.ai/app:/opt/ros/melodic/lib/python3/dist-packages:/opt/ros/noetic/lib/python3/dist-packages"
            }
            # Non silent operation
            self.args.silent = False

            # Bypass [Y/n/[A]ll/[K]eep all] command for export command
            self.args.cmd = f"python3 -m tools.backup -p {metadata_dir} -a {self.args.command} -m {manifest} {backup_opts}"
            if self.args.command == "export":
                self.args.cmd = "echo 'A' | " + self.args.cmd

            # Execute if not dry run
            if not self.args.dry:
                self.spawner_cls.exec_run()
            else:
                logger.info("Dry run mode, please remove the dry run arg to execute")


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
    parser.add_argument(
        "-dir" "--dir",
        "--directory",
        help="Directory to search manifests, defaults to CWD",
    )
    # TODO: Remove the dependency of command inside this low lever script
    parser.add_argument(
        "command",
        help="Command to be executed.",
    )

    args = parser.parse_args()
    backup_helper = BackupHelper(args)
    print(f"Manifest files in spawner: {backup_helper.get_manifest_files_in_spawner()}")
