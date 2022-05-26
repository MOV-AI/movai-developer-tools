"""Module where all the behaviour of a command should be destributed."""
import sys
from movai_developer_tools.utils import logger as logging
from movai_developer_tools.utils.container_tools import ContainerTools


class Spawner(ContainerTools):
    """Main class to get properties of the active spawner container"""

    def __init__(self, args):
        """If your executor requires some initialization, use the class constructor for it"""
        logging.debug("Spawner Init")
        # Reg expressions for finding the spawner container
        self.regex_spawner_name = "^spawner-.*"
        super().__init__(self.regex_spawner_name)
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
        logging.debug(f"Execute spawner behaviour with args: {self.args}")
        try:
            return self.prop_to_method[self.args.sub_command]()
        except KeyError:
            logging.error(
                "Invalid command: "
                + self.args.sub_command
                + ". Supported sub_commands are: ("
                + " ".join(map(str, self.prop_to_method))
                + ")"
            )
            sys.exit()

    @staticmethod
    def add_expected_arguments(parser):
        """Method exposed for the handle to append our executer arguments."""
        parser.add_argument(
            "sub_command",
            help="Property of the component to be fetched, options are (ip, id, name, gateway, userspace-dir, exec, logs)",
        )
        parser.add_argument(
            "--cmd",
            help="Command to be executed in the spawner",
            default="echo 'Hi there, I am an echo being executed in the spawner container. Please use [--cmd EXEC_COMMAND] to specify the command you want to run'",
        )
        parser.add_argument(
            "--user",
            help="User to execute docker exec command as. Default: movai",
            default="movai",
        )
        parser.add_argument(
            "--env",
            help="A dictionary or a list of strings in the following format 'PASSWORD=xxx' 'USER=xxx'",
            nargs="+",
            default=[],
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
        "sub_command",
        help="Property of the component to be fetched, options are (ip, id, name, gateway, userspace-dir, exec, logs)",
    )
    args = parser.parse_args()
    spawner = Spawner(args)
    spawner.execute()
