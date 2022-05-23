"""Module where all the behaviour of a command should be destributed."""
from movai_developer_tools.utils import logger as logging
from movai_developer_tools.movmisc.spawner.operation_executer import Spawner
import os
import sys


class Importer:
    """Main class to get properties of the active spawner container"""

    def __init__(self):
        """If your executor requires some initialization, use the class constructor for it"""
        logging.debug("Importer Init")
        self.spawner = Spawner()
        # Container userspace bind location
        self.container_bind_dir = "/opt/mov.ai/user"

    def execute(self, args):
        """Method where the main behaviour of the executer should be"""
        logging.debug(f"Execute importer behaviour with args: {args}")
        # Get container to make the operation in silently
        args.silent = True
        host_userspace = self.spawner.get_spawner_userspace_dir(args)
        # Check provided directory is inside the userspace
        cwd = os.getcwd()
        if host_userspace not in cwd:
            logging.error(
                f"Directory to be used must be inside the userspace: {host_userspace}"
            )
            sys.exit(1)
        # Get path in spawner
        dir_in_spawner = self.container_bind_dir + cwd.replace(host_userspace, "")
        logging.error(dir_in_spawner)

    @staticmethod
    def add_expected_arguments(parser):
        """Method exposed for the handle to append our executer arguments."""
        # parser.add_argument(
        #     "property",
        #     help="Property of the component to be fetched, options are (ip, id, name, gateway)",
        # )
