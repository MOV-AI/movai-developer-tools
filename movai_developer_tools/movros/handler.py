"""Main package module. Contains the handler, executors and other modules inside.# noqa: E501"""
import argparse
import sys
from movai_developer_tools.utils import logger
from movai_developer_tools.movros.expose_network.operation_executer import (
    ExposeNetwork,
)
from movai_developer_tools.movros.catkin_build.operation_executer import (
    CatkinBuild,
)

executors = {
    "expose-network": ExposeNetwork,
    "catkin-build": CatkinBuild,
}


def handle():
    """Entrypoint method of the package. It handles commands to the executers"""
    parser = argparse.ArgumentParser(
        description="This component helps in bridging the gap to ROS when developing with MOV.AI."
    )

    parser.add_argument("command", help="Command to be executed.")

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

    executor.execute()


if __name__ == "__main__":
    handle()
