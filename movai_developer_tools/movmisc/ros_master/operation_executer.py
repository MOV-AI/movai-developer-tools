"""Module where all the behaviour of a command should be destributed."""
import sys
from movai_developer_tools.utils import logger as logging
from movai_developer_tools.utils.container_tools import ContainerTools


class RosMaster(ContainerTools):
    """Main class to get properties of the active ros-master container"""

    def __init__(self, args):
        """If your executor requires some initialization, use the class constructor for it"""
        logging.debug("RosMaster Init")
        # Reg expressions for finding the ros-master container
        self.regex_ros_master_name = "^ros-master-*"
        super().__init__(self.regex_ros_master_name)
        # Property to method map
        self.prop_to_method = {
            "ip": self.get_ip,
            "id": self.get_id,
            "name": self.get_name,
            "gateway": self.get_gateway,
            "restart": self.restart,
            "userspace-dir": self.get_userspace_dir,
            "exec": self.exec,
            "logs": self.logs,
        }
        # Pass args as instance variable
        self.args = args

    def execute(self):
        """Method where the main behaviour of the executer should be"""
        logging.debug(f"Execute RosMaster behaviour with args: {self.args}")
        try:
            return self.prop_to_method[self.args.sub_command]()
        except KeyError:
            logging.error(
                "Invalid command: "
                + self.args.sub_command
                + ". Supported sub-commands are: ("
                + " ".join(map(str, self.prop_to_method))
                + ")"
            )
            sys.exit()

    @staticmethod
    def add_expected_arguments(parser):
        """Method exposed for the handle to append our executer arguments."""
        # parser.add_argument(
        #     "property",
        #     help="Property of the ros-master to be fetched, options are (ip, id, name)",
        # )


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
        "sub_command",
        help="Property of the component to be fetched, options are (ip, id, name, gateway, userspace-dir, exec, logs)",
    )
    args = parser.parse_args()
    spawner = RosMaster(args)
    spawner.execute()
