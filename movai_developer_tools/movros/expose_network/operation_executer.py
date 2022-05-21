"""Module where all the behaviour of a command should be destributed."""
import movai_developer_tools.utils.logger as logging
from movai_developer_tools.movmisc.spawner.operation_executer import Spawner
from movai_developer_tools.movmisc.ros_master.operation_executer import RosMaster


class ExposeNetwork:
    """Main class to expose ros topics, services and parameters from docker to the host"""

    def __init__(self):
        """If your executor requires some initialization, use the class constructor for it"""
        logging.debug("ExposeNetwork Init")

    def execute(self, args):
        """Method where the main behaviour of the executer should be"""
        logging.debug(f"Execute ExposeNetwork behaviour with args: {args}")
        # Make args for calling other services
        # Silence the log output from other services because the function is being used internally
        # Only the return value is used and not the printed one
        args.silent = True
        # Get name of the spawner container
        args.property = "name"
        spawner_name = Spawner().execute(args)
        # Get ip of the spawner and ros-master container networks
        args.property = "ip"
        spawner_ip = Spawner().execute(args)
        ros_master_ip = RosMaster().execute(args)
        # Get gateway of the spawner container network
        args.property = "gateway"
        spawner_gateway = Spawner().execute(args)

        logging.info(
            f"spawner_name: {spawner_name}, spawner_ip: {spawner_ip}, ros_master_ip: {ros_master_ip}, spawner_gateway: {spawner_gateway}"
        )

    @staticmethod
    def add_expected_arguments(parser):
        """Method exposed for the handle to append our executer arguments."""
        # parser.add_argument(
        #     "--executor_specific_arg",
        #     help="specific argument needed for this executor",
        # )
