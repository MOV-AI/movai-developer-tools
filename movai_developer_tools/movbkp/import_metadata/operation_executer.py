"""Module where all the behaviour of a command should be destributed."""
from movai_developer_tools.utils import logger as logging
from movai_developer_tools.utils import backup_helper
from movai_developer_tools.movmisc.spawner.operation_executer import Spawner


class Importer:
    """Main class to get properties of the active spawner container"""

    def __init__(self):
        """If your executor requires some initialization, use the class constructor for it"""
        logging.debug("Importer Init")
        self.spawner = Spawner()

    def execute(self, args):
        """Method where the main behaviour of the executer should be"""
        logging.debug(f"Execute importer behaviour with args: {args}")
        manifest_files_in_spawner = backup_helper.get_manifest_files_in_spawner(args)

        # Backup options for import
        backup_opts = "-i -c"

        # Import metadata using each manifest
        for manifest in manifest_files_in_spawner:
            # Log
            logging.info(f"Importing metadata present in {manifest}")
            # Get manifest file directory and metadata directory (project, -p arg on backup tool)
            manifest_dir_in_spawner = manifest.replace("/manifest.txt", "")
            metadata_dir = manifest_dir_in_spawner + "/metadata"

            # If PYTHONPATH is not set, scenes fail to export
            args.env = [
                "PYTHONPATH=/opt/mov.ai/app:/opt/ros/melodic/lib/python3/dist-packages:/opt/ros/noetic/lib/python3/dist-packages"
            ]
            args.cmd = f"python3 -m tools.backup -p {metadata_dir} -a import -m {manifest} {backup_opts}"
            args.silent = False

            # Execute
            self.spawner.spawner_exec(args)

    @staticmethod
    def add_expected_arguments(parser):
        """Method exposed for the handle to append our executer arguments."""
