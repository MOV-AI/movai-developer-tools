from movai_developer_tools.utils import logger
from movai_developer_tools.utils import backup_helper


class ReInstaller:
    """Main class to delete metadata using the backup tool in the spawner container"""

    def __init__(self):
        """If your executor requires some initialization, use the class constructor for it"""
        logger.debug("ReInstaller Init")

    def execute(self, args):
        """Method where the main behaviour of the executer should be"""
        logger.debug(f"Execute reinstaller behaviour with args: {args}")
        # Get manifest files that are installed inside the spawner
        manifest_files_in_spawner = backup_helper.get_manifest_files_in_spawner(args)

        # Re-install is not supported by the backup tools directly, it is actually import
        args.command = "import"
        # Add fix for  !---Thenameofthepackage.--: No such file or directory error
        # Quote every manifest paths
        manifest_files_in_spawner = list(
            map(lambda x: "'" + x + "'", manifest_files_in_spawner)
        )
        # Execute
        backup_helper.iterative_backup_action(args, manifest_files_in_spawner)

    @staticmethod
    def add_expected_arguments(parser):
        """Method exposed for the handle to append our executer arguments."""
