"""Module where all the behaviour of a command should be destributed."""
import movai_developer_tools.utils.logger as logging
import docker
import re


class Spawner:
    """Main class to get properties of the active spawner container"""

    def __init__(self):
        """If your executor requires some initialization, use the class constructor for it"""
        logging.info("Init")
        # Instanciate docker client
        self.docker_client = docker.from_env()
        # Reg expressions for finding the spawner container
        self.regex_spawner_name = "^spawner-.*"
        # Property to method map
        self.prop_to_method = {
            "ip": self.get_spawner_ip,
            "id": self.get_spawner_id,
            "name": self.get_spawner_name,
            "gateway": self.get_spawner_gateway,
        }

    def get_spawner_ip(self):
        """Get ip address of the first network of a container found using regex of the name"""
        containers = self.docker_client.containers.list()
        for container in containers:
            name = container.name
            networks = container.attrs["NetworkSettings"]["Networks"]
            if re.search(self.regex_spawner_name, name):
                network = next(iter(networks))
                ip = networks[network]["IPAddress"]
                print(f"IPAddress: {ip}")
                return ip
        print(
            f"Did not find a runnning spawner container: Regex used {self.regex_spawner_name}"
        )

    def get_spawner_id(self):
        """Get short id of a container found using regex of the name"""
        containers = self.docker_client.containers.list()
        for container in containers:
            name = container.name
            short_id = container.short_id
            if re.search(self.regex_spawner_name, name):
                print(f"Short ID: {short_id}")
                return short_id
        print(
            f"Did not find a runnning spawner container: Regex used {self.regex_spawner_name}"
        )

    def get_spawner_name(self):
        """Get the name of a container found using regex"""
        containers = self.docker_client.containers.list()
        for container in containers:
            name = container.name
            if re.search(self.regex_spawner_name, name):
                print(f"Name: {name}")
                return name
        print(
            f"Did not find a runnning spawner container: Regex used {self.regex_spawner_name}"
        )

    def get_spawner_gateway(self):
        """Get gateway of the first network of a container found using regex of the name"""
        containers = self.docker_client.containers.list()
        for container in containers:
            name = container.name
            networks = container.attrs["NetworkSettings"]["Networks"]
            if re.search(self.regex_spawner_name, name):
                network = next(iter(networks))
                gateway = networks[network]["Gateway"]
                print(f"Gateway: {gateway}")
                return gateway
        print(
            f"Did not find a runnning spawner container: Regex used {self.regex_spawner_name}"
        )

    def execute(self, args):
        """Method where the main behaviour of the executer should be"""
        logging.info("execute behaviour: movmisc/spawner_name")
        logging.info(args)
        return self.prop_to_method[args.property]()

    @staticmethod
    def add_expected_arguments(parser):
        """Method exposed for the handle to append our executer arguments."""
        parser.add_argument(
            "property",
            help="Property of the component to be fetched, options are (ip, id, name, gateway)",
        )
