"""Module where all the behaviour of a command should be destributed."""
import sys
from movai_developer_tools.utils import logger as logging, container_tools


class Spawner:
    """Main class to get properties of the active spawner container"""

    def __init__(self):
        """If your executor requires some initialization, use the class constructor for it"""
        logging.debug("Spawner Init")
        # Reg expressions for finding the spawner container
        self.regex_spawner_name = "^spawner-.*"
        # Property to method map
        self.prop_to_method = {
            "ip": self.get_spawner_ip,
            "id": self.get_spawner_id,
            "name": self.get_spawner_name,
            "gateway": self.get_spawner_gateway,
            "userspace-dir": self.get_spawner_userspace_dir,
        }
        # Container userspace bind location
        self.container_bind_dir = "/opt/mov.ai/user"

    def get_spawner_ip(self, args):
        """Get ip address of the first network of a container found using regex of the name"""
        ip = container_tools.get_container_ip(self.regex_spawner_name)
        # Log if not silent
        if not args.silent:
            logging.info(f"IPAddress: {ip}")
        return ip

    def get_spawner_id(self, args):
        """Get short id of a container found using regex of the name"""
        short_id = container_tools.get_container_id(self.regex_spawner_name)
        # Log if not silent
        if not args.silent:
            logging.info(f"Short ID: {short_id}")
        return short_id

    def get_spawner_name(self, args):
        """Get the name of a container found using regex"""
        name = container_tools.get_container_name(self.regex_spawner_name)
        # Log if not silent
        if not args.silent:
            logging.info(f"Name: {name}")
        return name

    def get_spawner_gateway(self, args):
        """Get gateway of the first network of a container found using regex of the name"""
        gateway = container_tools.get_container_gateway(self.regex_spawner_name)
        # Log if not silent
        if not args.silent:
            logging.info(f"Gateway: {gateway}")
        return gateway

    def get_spawner_userspace_dir(self, args):
        """Return userspace that is mounted in the spawner"""
        spawner_container = container_tools.get_container_obj_by_name_regex(
            self.regex_spawner_name
        )
        binds = spawner_container.attrs["HostConfig"]["Binds"]
        # Check the bind at "/opt/mov.ai/user", which is where the userspace is mounted
        userspace_dir = None
        for bind in binds:
            _split = bind.split(":")
            if _split[1] == self.container_bind_dir:
                userspace_dir = _split[0]
                # Log if not silent
                if not args.silent:
                    logging.info(f"Userspace directory: {userspace_dir}")
                return userspace_dir
        # Exit if userspace is not found
        logging.error("Userspace not mounted.")
        sys.exit(1)

    def execute(self, args):
        """Method where the main behaviour of the executer should be"""
        logging.debug(f"Execute spawner behaviour with args: {args}")
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
            help="Property of the component to be fetched, options are (ip, id, name, gateway, userspace-dir)",
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="This component containes miscellaneous tools used when developing with MOV.AI"
    )
    parser.add_argument(
        "--silent",
        help="Silence the output of commands. Used when commands are used internally to silence the output",
        action="store_true",
    )
    parser.add_argument(
        "property",
        help="Property of the component to be fetched, options are (ip, id, name, gateway)",
    )
    args = parser.parse_args()
    spawner = Spawner()
    spawner.execute(args)
