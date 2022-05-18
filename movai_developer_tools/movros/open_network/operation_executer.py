"""Module where all the behaviour of a command should be destributed."""
import movai_developer_tools.utils.logger as logging



class OperationExecuter:
    """Main class to expose ros topics, services and parameters from docker to the host"""

    def __init__(self):
        """If your executor requires some initialization, use the class constructor for it"""
        logging.info("Init")

    def execute(self, args):
        """Method where the main behaviour of the executer should be"""
        logging.info("execute behaviour")
        logging.info(args)
        logging.info("TODO: Please complete me")

    @staticmethod
    def add_expected_arguments(parser):
        # """Method exposed for the handle to append our executer arguments."""
        # parser.add_argument(
        #     "--executor_specific_arg",
        #     help="specific argument needed for this executor",
        # )
        pass