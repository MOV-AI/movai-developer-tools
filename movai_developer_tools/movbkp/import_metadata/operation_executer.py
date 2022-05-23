"""Module where all the behaviour of a command should be destributed."""
from movai_developer_tools.utils import logger as logging
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
        # Get container to make the operation in silently
        args.silent = True
        spawner_container_name = self.spawner.get_spawner_name(args)
        logging.error(spawner_container_name)

    @staticmethod
    def add_expected_arguments(parser):
        """Method exposed for the handle to append our executer arguments."""
        # parser.add_argument(
        #     "property",
        #     help="Property of the component to be fetched, options are (ip, id, name, gateway)",
        # )
