"""Module where all the behaviour of a command should be destributed."""
import sys
import movai_developer_tools.utils.logger as logging
import docker
import re


class RosMaster:
    """Main class to get properties of the active ros_master container"""

    def __init__(self):
        """If your executor requires some initialization, use the class constructor for it"""
        logging.info("Init")
        # Instanciate docker client
        self.docker_client = docker.from_env()
        # Reg expressions for finding the ros_master container
        self.regex_ros_master_name = "^ros-master-*"
        # Property to method map
        self.prop_to_method = {
            "ip": self.get_ros_master_ip,
            "id": self.get_ros_master_id,
            "name": self.get_ros_master_name,
        }

    def get_ros_master_id(self):
        """Get short id of a container found using regex of the name"""
        containers = self.docker_client.containers.list()
        for container in containers:
            name = container.name
            short_id = container.short_id
            if re.search(self.regex_ros_master_name, name):
                print(short_id)
                return short_id
        print(
            f"Did not find a runnning ros_master container: Regex used {self.regex_ros_master_name}"
        )

    def get_ros_master_ip(self):
        """Get ip address of the first network of a container found using regex of the name"""
        containers = self.docker_client.containers.list()
        for container in containers:
            name = container.name
            networks = container.attrs["NetworkSettings"]["Networks"]
            if re.search(self.regex_ros_master_name, name):
                network = next(iter(networks))
                ip = networks[network]["IPAddress"]
                print(ip)
                return ip
        print(
            f"Did not find a runnning ros_master container: Regex used {self.regex_ros_master_name}"
        )

    def get_ros_master_name(self):
        """Get the name of a container found using regex"""
        containers = self.docker_client.containers.list()
        for container in containers:
            name = container.name
            if re.search(self.regex_ros_master_name, name):
                print(name)
                return name
        print(
            f"Did not find a runnning ros_master container: Regex used {self.regex_ros_master_name}"
        )

    def execute(self, args):
        """Method where the main behaviour of the executer should be"""
        logging.info("execute behaviour: movmisc/ros_master_name")
        logging.info(args)
        try:
            return self.prop_to_method[args.property]()
        except KeyError:
            logging.error(
                "Invalid command: "
                + args.property
                + ". Supported commands are: ("
                + " ".join(map(str, self.prop_to_method))
                + ")"
            )
            sys.exit()

    @staticmethod
    def add_expected_arguments(parser):
        """Method exposed for the handle to append our executer arguments."""
        # parser.add_argument(
        #     "property",
        #     help="Property of the ros_master to be fetched, options are (ip, id, name)",
        # )
