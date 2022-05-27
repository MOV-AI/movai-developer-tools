from movai_developer_tools.utils import logger
from movai_developer_tools.utils.backup_helper import BackupHelper


class Importer(BackupHelper):
    """Main class to import metadata using the backup tool in the spawner container"""

    def __init__(self, args):
        """If your executor requires some initialization, use the class constructor for it"""
        logger.debug("Importer Init")
        # Call superclass init
        super().__init__(args)
        # Pass args as instance variable
        self.args = args

    def execute(self):
        """Method where the main behaviour of the executer should be"""
        logger.debug(f"Execute importer behaviour with self.args: {self.args}")
        # Execute
        self.iterative_backup_action()

    @staticmethod
    def add_expected_arguments(parser):
        """Method exposed for the handle to append our executer arguments."""
