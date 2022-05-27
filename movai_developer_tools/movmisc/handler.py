"""Main package module. Contains the handler, executors and other modules inside.# noqa: E501"""
import argparse
import sys

from movai_developer_tools.utils import logger
from movai_developer_tools.movmisc.spawner.operation_executer import (
    Spawner,
)
from movai_developer_tools.movmisc.ros_master.operation_executer import (
    RosMaster,
)

executors = {"spawner": Spawner, "ros-master": RosMaster}


def handle():
    """Entrypoint method of the package. It handles commands to the executers"""
    parser = argparse.ArgumentParser(
        description="This component containes miscellaneous tools used when developing with MOV.AI"
    )
    parser.add_argument(
        "command",
        help=f"Command to be executed. Options are ({', '.join(executors.keys())})",
    )
    # Silent optional argument for when using the commands internally from other commands
    parser.add_argument(
        "--silent",
        help="Silence the output of commands. Used when commands are used internally to silence the output",
        action="store_true",
    )
    parser.add_argument(
        "sub_command",
        help="Property of the component to be fetched, options are (ip, id, name, gateway, userspace-dir, exec, logs)",
    )
    parser.add_argument(
        "--cmd",
        help="Command to be executed in the spawner",
        default="echo 'Hi there, I am an echo being executed in the container you have chosen. Please use [--cmd=EXEC_COMMAND] to specify the command you want to run'",
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

    # executor arguments
    for executer in executors.values():
        executer.add_expected_arguments(parser)

    args = parser.parse_args()

    try:
        executor = executors[args.command](args)
    except KeyError:
        logger.error(
            "Invalid command: "
            + args.command
            + ". Supported commands are: ("
            + " ".join(map(str, executors))
            + ")"
        )
        sys.exit()

    executor.execute()


if __name__ == "__main__":
    handle()
