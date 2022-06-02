"""Module where all the behaviour of a command should be destributed."""
from movai_developer_tools.utils import logger
from movai_developer_tools.utils.container_tools import ContainerTools


class CatkinBuild:
    """Main class to build ros workspace."""

    def __init__(self) -> None:
        logger.debug("CatkinBuild Init")

    def execute(self):
        """Method where the main behaviour of the executer should be"""
        # ROS instllation dir
        # ros_install_dir = "/opt/ros"

        # Instanciate spawner container class
        # Reg expressions for finding the spawner container
        regex_spawner_name = "^spawner-.*"
        # Instanciate for silent operation if silent arg is True, else take default
        spawner = ContainerTools(regex_spawner_name, silent=True)
        # Info to the user
        logger.info(f"Running catkin build in spawner {spawner.get_name()}")

        # # Use container exec to do catkin build in spawner
        # args.cmd = "cd /opt/mov.ai/workspaces/USER_ROS1 && catkin build -j2 -l2 --mem-limit 50%"
        # args.user = "movai"
        # args.env = []
        # args.silent = False
        # spawner = Spawner(args)
        # spawner.exec()

    @staticmethod
    def add_expected_arguments(parser):
        """Method exposed for the handle to append our executer arguments."""
