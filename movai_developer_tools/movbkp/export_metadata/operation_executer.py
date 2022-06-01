from movai_developer_tools.utils import logger
from movai_developer_tools.utils.backup_helper import BackupHelper
from argparse import Namespace


class Exporter(BackupHelper):
    """Main class to export metadata using the backup tool in the spawner container."""

    def __init__(self):
        logger.debug("Exporter Init")

    def execute(self, args: Namespace):
        """Execute the export behaviour.

        Args:
            args: A set of parsed args.

        """
        # Call superclass init
        super().__init__(dry_run=args.dry)
        # Execute
        self.iterative_backup_action(command=args.command, work_dir=args.dir)

    @staticmethod
    def add_expected_arguments(parser):
        """Method exposed for the handle to append our executer arguments."""
