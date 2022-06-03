"""Module that contains a set of functions to ease interacting with the MOV.AI backup tool"""
from movai_developer_tools.utils import logger
from movai_developer_tools.utils.container_tools import ContainerTools
import pathlib
import sys
from typing import Optional


class BackupHelper:
    """Set of functions to help export/import of metadata objects when developing with MOV.AI platform.

    Args:
        userspace_bind_dir: The directory where the userspace is mounted. Defaults to ``"/opt/mov.ai/user"``.
        metadata_install_dir: Metadata install location inside the spawner container.
        manifest_regex: Manifest file name used for listing metadata type and name (Flow:my_flow).
        dry_run: If True, the actions taken by the backup tool are not destructive.

    Attributes:
        userspace_bind_dir (str): The directory where the userspace is mounted. Defaults to ``"/opt/mov.ai/user"``.
        metadata_install_dir (str): Metadata install location inside the spawner container.
        manifest_regex (str): Manifest file name used for listing metadata type and name (Flow:my_flow).
        regex_spawner_name (str): Regular expression for finding the spawner container.
        spawner_cls (ContainerTools): Container object of the spawner container.
        userspace_dir (str): Userspace directory in the host which is mounted inside the spawner container.
        valid_commands (set): A set of accepted commands by backup tool.
        dry_run (bool): If True, the actions taken by the backup tool are not destructive.

    """

    def __init__(
        self,
        dry_run: bool = False,
        userspace_bind_dir: str = "/opt/mov.ai/user",
        metadata_install_dir: str = "/opt/ros/${ROS_DISTRO}/share",
        manifest_regex: str = "manifest.txt",
    ) -> None:
        # Container userspace bind location
        self.userspace_bind_dir = userspace_bind_dir
        # Metadata install location in spawner
        self.metadata_install_dir = metadata_install_dir
        # Manifest regex
        self.manifest_regex = manifest_regex

        # Instanciate spawner container class
        # Reg expressions for finding the spawner container
        regex_spawner_name = "^spawner-.*"
        # Instanciate for silent operation if silent arg is True, else take default
        self.spawner_cls = ContainerTools(regex_spawner_name, silent=True)
        # Get userspace directory
        self.userspace_dir = self.spawner_cls.get_userspace_dir()
        # Set of accepted commands
        self.valid_commands = {"import", "export", "remove", "re-install"}
        # Dry run parameter
        self.dry_run = dry_run

    def get_installed_manifest_files(self) -> map:
        """Return a map object of paths of manifest files that are already installed by packages in the container.

        Returns:
            A map of paths inside the spawner container.

        """
        # Make required args for exec_run method
        cmd = f"find {self.metadata_install_dir} -name {self.manifest_regex}"
        # Execute command with exec_run command
        _, manifest_files_in_spawner = self.spawner_cls.exec_run(cmd=cmd)
        # Add fix for: !---Thenameofthepackage.--: No such file or directory error
        # Quote every manifest paths
        manifest_files_in_spawner = list(
            map(lambda x: "'" + x + "'", manifest_files_in_spawner.decode().split())
        )
        return manifest_files_in_spawner

    def get_manifest_files_in_host(self, dir: pathlib.PosixPath) -> map:
        """Return a map object of manifest files found in the host.

        Args:
            dir: Directory path to search for manifest files.

        Returns:
            A map object of manifest file paths found in recursive search from dir.

        """
        # Get all manifest files recursively in the host
        # Validate if the working directory is inside the userspace_dir
        work_dir = str(dir)
        if self.userspace_dir not in work_dir:
            logger.error(
                f"Directory({work_dir}) must be inside the userspace({self.userspace_dir}"
            )
            sys.exit(1)

        # Search for manifest files in working_directory
        manifest_files_in_host = map(
            lambda x: str(x.absolute()), dir.rglob(self.manifest_regex)
        )
        return manifest_files_in_host

    def get_manifest_files_in_spawner(self, work_dir: pathlib.PosixPath) -> map:
        """Get a list of manifest file locations inside the spawner container given working directory.

        Args:
            work_dir: A PosixPath object of the working directory in the host.

        Returns:
            A map of paths of manifest files inside the spawner container.

        """
        manifest_files_in_host = self.get_manifest_files_in_host(work_dir)
        # Map paths from host to the ones mounted in the container
        manifest_files_in_spawner = map(
            lambda x: x.replace(self.userspace_dir, self.userspace_bind_dir),
            manifest_files_in_host,
        )
        return manifest_files_in_spawner

    def iterative_backup_action(
        self, command: str, work_dir: Optional[str] = None
    ) -> None:
        """Iteratively import/export/remove/re-install mov.ai metadata mentioned in manifest.txt files.

        Args:
            command: Action to be taken. Options are in self.valid_commands.
            work_dir: Working directory.

        """
        # If command not valid, exit
        if command not in self.valid_commands:
            logger.error(f"Command({command}) is not valid, exiting.")
            sys.exit(1)

        # If command is re-install bypass getting manfiest files in work_dir or CWD
        # In re-install get list inside the install location in spawner
        if command == "re-install":
            manifest_files_in_spawner = self.get_installed_manifest_files()
            # Re-install is not supported by the backup tool directly, it is actually import
            command = "import"
        else:
            # If user provides directory arg use that as root dir, else use CWD
            if work_dir:
                working_directory = pathlib.Path(work_dir).resolve()
            else:
                working_directory = pathlib.Path.cwd().resolve()
            # Get manifest files in the spawner using working_directory
            manifest_files_in_spawner = self.get_manifest_files_in_spawner(
                working_directory
            )

        # Backup options. -i for individual, -c for clearing existing metadata, -f for force (don't stop on error)
        backup_opts = "-i -c -f"
        # -f argument is not supported for "remove" command
        if command == "remove":
            backup_opts = backup_opts.replace(" -f", "")

        # Import metadata using each manifest
        for manifest in manifest_files_in_spawner:
            # Log
            logger.info(f"{command.upper()}ING metadata present in {manifest}")
            # Get manifest file directory and metadata directory (project, -p arg on backup tool)
            manifest_dir_in_spawner = manifest.replace("/manifest.txt", "")
            metadata_dir = manifest_dir_in_spawner + "/metadata"

            # If PYTHONPATH is not set, scenes fail to export
            env = {
                "PYTHONPATH": "/opt/mov.ai/app:/opt/ros/melodic/lib/python3/dist-packages:/opt/ros/noetic/lib/python3/dist-packages"
            }

            # Exec command for the container
            exec_cmd = f"python3 -m tools.backup -p {metadata_dir} -a {command} -m {manifest} {backup_opts}"
            # Bypass [Y/n/[A]ll/[K]eep all] command for export command
            if command == "export":
                exec_cmd = "echo 'A' | " + exec_cmd

            # Execute if not dry run
            if not self.dry_run:
                self.spawner_cls.exec_run(cmd=exec_cmd, environment=env)
            else:
                logger.info("Dry run mode, please remove the dry run arg to execute")


if __name__ == "__main__":
    """Test this script"""
    backup_helper = BackupHelper(dry_run=True)
    backup_helper.iterative_backup_action(command="export")
