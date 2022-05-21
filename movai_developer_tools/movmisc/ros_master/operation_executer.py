"""Module where all the behaviour of a command should be destributed."""
import sys
from movai_developer_tools.utils import logger as logging, container_tools


class RosMaster:
    """Main class to get properties of the active ros-master container"""

    def __init__(self):
        """If your executor requires some initialization, use the class constructor for it"""
        logging.debug("RosMaster Init")
        # Reg expressions for finding the ros-master container
        self.regex_ros_master_name = "^ros-master-*"
        # Property to method map
        self.prop_to_method = {
            "ip": self.get_ros_master_ip,
            "id": self.get_ros_master_id,
            "name": self.get_ros_master_name,
            "gateway": self.get_ros_master_gateway,
        }

    def get_ros_master_ip(self, args):
        """Get ip address of the first network of a container found using regex of the name"""
        ip = container_tools.get_container_ip(self.regex_ros_master_name)
        if ip is None:
            logging.error(
                f"Did not find a runnning {args.command} container: Regex used {self.regex_ros_master_name}"
            )
        else:
            if not args.silent:
                logging.info(f"IPAddress: {ip}")
        return ip

    def get_ros_master_id(self, args):
        """Get short id of a container found using regex of the name"""
        short_id = container_tools.get_container_id(self.regex_ros_master_name)
        if short_id is None:
            logging.error(
                f"Did not find a runnning {args.command} container: Regex used {self.regex_ros_master_name}"
            )
        else:
            if not args.silent:
                logging.info(f"Short ID: {short_id}")
        return short_id

    def get_ros_master_name(self, args):
        """Get the name of a container found using regex"""
        name = container_tools.get_container_name(self.regex_ros_master_name)
        if name is None:
            logging.error(
                f"Did not find a runnning {args.command} container: Regex used {self.regex_ros_master_name}"
            )
        else:
            if not args.silent:
                logging.info(f"Name: {name}")
        return name

    def get_ros_master_gateway(self, args):
        """Get gateway of the first network of a container found using regex of the name"""
        gateway = container_tools.get_container_gateway(self.regex_ros_master_name)
        if gateway is None:
            logging.error(
                f"Did not find a runnning {args.command} container: Regex used {self.regex_ros_master_name}"
            )
        else:
            if not args.silent:
                logging.info(f"Gateway: {gateway}")
        return gateway

    def execute(self, args):
        """Method where the main behaviour of the executer should be"""
        logging.debug(f"Execute RosMaster behaviour with args: {args}")
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
        # parser.add_argument(
        #     "property",
        #     help="Property of the {args.command} to be fetched, options are (ip, id, name)",
        # )
