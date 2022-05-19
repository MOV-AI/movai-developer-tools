"""Module where all the behaviour of a command should be destributed."""
import movai_developer_tools.utils.logger as logging
import docker
import re


class SpawnerName:
    """Main class to expose ros topics, services and parameters from docker to the host"""

    def __init__(self):
        """If your executor requires some initialization, use the class constructor for it"""
        logging.info("Init")
        # Instanciate docker client
        self.docker_client = docker.from_env()
        # Reg expressions for finding the spawner container
        self.regex = "^spawner-.*"

    def execute(self, args):
        """Method where the main behaviour of the executer should be"""
        logging.info("execute behaviour: movmisc/spawner_name")
        logging.info(args)
        containers = self.docker_client.containers.list()
        for container in containers:
            name = container.name
            if re.search(self.regex, name):
                return name

    @staticmethod
    def add_expected_arguments(parser):
        """Method exposed for the handle to append our executer arguments."""
        # parser.add_argument(
        #     "--executor_specific_arg",
        #     help="specific argument needed for this executor",
        # )
