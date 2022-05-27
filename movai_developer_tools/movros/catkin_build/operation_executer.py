"""Module where all the behaviour of a command should be destributed."""
from movai_developer_tools.utils import logger
from movai_developer_tools.movmisc.spawner.operation_executer import Spawner


class CatkinBuild:
    """Main class to expose ros topics, services and parameters from docker to the host"""

    def __init__(self):
        """If your executor requires some initialization, use the class constructor for it"""
        logger.debug("CatkinBuild Init")
        # ROS instllation dir
        self.ros_ws_dir = "/opt/ros"

    def execute(self, args):
        """Method where the main behaviour of the executer should be"""
        logger.info("Running catkin build in spawner")

        # Use container exec to do catkin build in spawner
        args.cmd = "cd /opt/mov.ai/workspaces/USER_ROS1 && catkin build -j2 -l2 --mem-limit 50%"
        args.user = "movai"
        args.env = []
        args.silent = False
        spawner = Spawner(args)
        spawner.exec()

    @staticmethod
    def add_expected_arguments(parser):
        """Method exposed for the handle to append our executer arguments."""
        # parser.add_argument(
        #     "--executor_specific_arg",
        #     help="specific argument needed for this executor",
        # )
