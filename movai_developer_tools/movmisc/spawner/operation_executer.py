"""Module where all the behaviour of a command should be destributed."""
import sys
import movai_developer_tools.utils.logger as logging
import docker
import re


class Spawner:
    """Main class to get properties of the active spawner container"""

    def __init__(self):
        """If your executor requires some initialization, use the class constructor for it"""
        logging.debug("Spawner Init")
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

    def get_spawner_ip(self, args):
        """Get ip address of the first network of a container found using regex of the name"""
        containers = self.docker_client.containers.list()
        for container in containers:
            name = container.name
            networks = container.attrs["NetworkSettings"]["Networks"]
            if re.search(self.regex_spawner_name, name):
                network = next(iter(networks))
                ip = networks[network]["IPAddress"]
                if not args.silent:
                    logging.info(f"IPAddress: {ip}")
                return ip
        logging.error(
            f"Did not find a runnning spawner container: Regex used {self.regex_spawner_name}"
        )

    def get_spawner_id(self, args):
        """Get short id of a container found using regex of the name"""
        containers = self.docker_client.containers.list()
        for container in containers:
            name = container.name
            short_id = container.short_id
            if re.search(self.regex_spawner_name, name):
                if not args.silent:
                    logging.info(f"Short ID: {short_id}")
                return short_id
        logging.error(
            f"Did not find a runnning spawner container: Regex used {self.regex_spawner_name}"
        )

    def get_spawner_name(self, args):
        """Get the name of a container found using regex"""
        containers = self.docker_client.containers.list()
        for container in containers:
            name = container.name
            if re.search(self.regex_spawner_name, name):
                if not args.silent:
                    logging.info(f"Name: {name}")
                return name
        logging.error(
            f"Did not find a runnning spawner container: Regex used {self.regex_spawner_name}"
        )

    def get_spawner_gateway(self, args):
        """Get gateway of the first network of a container found using regex of the name"""
        containers = self.docker_client.containers.list()
        for container in containers:
            name = container.name
            networks = container.attrs["NetworkSettings"]["Networks"]
            if re.search(self.regex_spawner_name, name):
                network = next(iter(networks))
                gateway = networks[network]["Gateway"]
                if not args.silent:
                    logging.info(f"Gateway: {gateway}")
                return gateway
        logging.error(
            f"Did not find a runnning spawner container: Regex used {self.regex_spawner_name}"
        )

    def execute(self, args):
        """Method where the main behaviour of the executer should be"""
        logging.debug(f"Execute Spawner behaviour with args: {args}")
        try:
            return self.prop_to_method[args.property](args)
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
        parser.add_argument(
            "property",
            help="Property of the component to be fetched, options are (ip, id, name, gateway)",
        )
