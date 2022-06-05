"""Main package module. Contains the handler, executors and other modules inside.# noqa: E501"""
import argparse
import sys

from movai_developer_tools.utils import logger
from movai_developer_tools.movcontainer.spawner.operation_executer import (
    Spawner,
)
from movai_developer_tools.movcontainer.ros_master.operation_executer import (
    RosMaster,
)

executors = {"spawner": Spawner, "ros-master": RosMaster}


def handle():
    """Entrypoint method of the package. It handles commands to the executers"""
    parser = argparse.ArgumentParser(
        description="This component helps to retrieve docker container information developing with MOV.AI."
    )
    parser.add_argument(
        "command",
        help=f"Command to be executed. Options are ({', '.join(executors.keys())})",
    )
    parser.add_argument(
        "sub_command",
        help="Property of the component to be fetched, options are (ip, id, name, gateway, userspace-dir, logs)",
    )

    # executor arguments
    for executer in executors.values():
        executer.add_expected_arguments(parser)

    args = parser.parse_args()

    try:
        executor = executors[args.command]()
    except KeyError:
        logger.error(
            "Invalid command: "
            + args.command
            + ". Supported commands are: ("
            + " ".join(map(str, executors))
            + ")"
        )
        sys.exit()

    executor.execute(args)


if __name__ == "__main__":
    handle()
