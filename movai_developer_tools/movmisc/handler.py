"""Main package module. Contains the handler, executors and other modules inside.# noqa: E501"""
import argparse
import sys

import movai_developer_tools.utils.logger as logging
from movai_developer_tools.movmisc.spawner.operation_executer import (
    Spawner,
)

executors = {"spawner": Spawner}


def handle():
    """Entrypoint method of the package. It handles commands to the executers"""
    parser = argparse.ArgumentParser(
        description="This component containes miscellaneous tools used when developing with MOV.AI"
    )

    parser.add_argument(
        "command",
        help=f"Command to be executed. Options are ({', '.join(executors.keys())})",
    )

    # executor arguments
    for executer in executors.values():
        executer.add_expected_arguments(parser)

    args = parser.parse_args()

    try:
        executor = executors[args.command]()
    except KeyError:
        logging.error(
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
