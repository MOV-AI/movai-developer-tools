from movai_developer_tools.utils import logger as logging
from movai_developer_tools.utils import backup_helper


class Remover:
    """Main class to delete metadata using the backup tool in the spawner container"""

    def __init__(self):
        """If your executor requires some initialization, use the class constructor for it"""
        logging.debug("Remover Init")

    def execute(self, args):
        """Method where the main behaviour of the executer should be"""
        logging.debug(f"Execute remover behaviour with args: {args}")
        manifest_files_in_spawner = backup_helper.get_manifest_files_in_spawner(args)

        # Execute
        backup_helper.iterative_backup_action(args, manifest_files_in_spawner)

    @staticmethod
    def add_expected_arguments(parser):
        """Method exposed for the handle to append our executer arguments."""
