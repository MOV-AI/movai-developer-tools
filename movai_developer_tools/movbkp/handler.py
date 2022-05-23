"""Main package module. Contains the handler, executors and other modules inside.# noqa: E501"""
import argparse
import sys

from movai_developer_tools.utils.logger import logging
from movai_developer_tools.movbkp.import_metadata.operation_executer import Importer
from movai_developer_tools.movbkp.export_metadata.operation_executer import Exporter

executors = {
    "import": Importer,
    "export": Exporter,
}


def handle():
    """Entrypoint method of the package. It handles commands to the executers"""
    parser = argparse.ArgumentParser(
        description="This component containes backup (import/export) tools used on MOV.AI metadata files when developing with MOV.AI"
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
