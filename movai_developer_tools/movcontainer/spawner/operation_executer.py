import sys
from argparse import Namespace
from movai_developer_tools.utils import logger
from movai_developer_tools.utils.container_tools import ContainerTools


class Spawner(ContainerTools):
    """Main class to fetch properties of the active spawner container.

    Attributes:
        regex_container_name (str): Regular expression for finding the spawner container by name.

    """

    def __init__(self) -> None:
        logger.debug("Spawner Init")
        # Reg expression for finding the spawner container
        self.regex_container_name = "^spawner-.*"

    def get_ip(self) -> None:
        """Print container ip."""
        logger.info(f"IPAddress: {self.ip()}")

    def get_id(self) -> None:
        """Print container short id."""
        logger.info(f"Short ID: {self.id()}")

    def get_name(self) -> None:
        """Print container name."""
        logger.info(f"Name: {self.name()}")

    def get_gateway(self) -> None:
        """Print container gateway."""
        logger.info(f"Gateway: {self.gateway()}")

    def get_userspace_dir(self) -> None:
        """Print container userspace directory."""
        logger.info(f"Userspace directory: {self.userspace_dir()}")

    def execute(self, args: Namespace) -> None:
        """Execute the spawner behaviour. The sub_commad argument is used to execute respective method.

        Args:
            args: A set of parsed args.

        """
        # Instanciate ContainerTools
        super().__init__(self.regex_container_name)

        # Map sub command to the method
        prop_to_method = {
            "ip": self.get_ip,
            "id": self.get_id,
            "name": self.get_name,
            "gateway": self.get_gateway,
            "restart": self.restart,
            "userspace-dir": self.get_userspace_dir,
            "logs": self.logs,
        }

        # Try executing the sub-command, error and exit on invalid sub-commands
        try:
            return prop_to_method[args.sub_command]()
        except KeyError:
            logger.error(
                "Invalid command: "
                + args.sub_command
                + ". Supported sub_commands are: ("
                + " ".join(map(str, prop_to_method))
                + ")"
            )
            sys.exit(1)

    @staticmethod
    def add_expected_arguments(parser):
        """Method exposed for the handle to append our executer arguments."""


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Main class to fetch properties of the active spawner container"
    )
    parser.add_argument(
        "sub_command",
        help="Property of the component to be fetched, options are (ip, id, name, gateway, userspace-dir, logs)",
    )
    args = parser.parse_args()
    spawner = Spawner()
    spawner.execute(args)
