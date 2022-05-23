"""Module where all the behaviour of a command should be destributed."""
from movai_developer_tools.utils import logger as logging


class Exporter:
    """Main class to get properties of the active spawner container"""

    def __init__(self):
        """If your executor requires some initialization, use the class constructor for it"""
        logging.debug("Exporter Init")

    def execute(self, args):
        """Method where the main behaviour of the executer should be"""
        logging.debug(f"Execute exporter behaviour with args: {args}")

    @staticmethod
    def add_expected_arguments(parser):
        """Method exposed for the handle to append our executer arguments."""
        # parser.add_argument(
        #     "property",
        #     help="Property of the component to be fetched, options are (ip, id, name, gateway)",
        # )
