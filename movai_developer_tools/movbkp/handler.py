"Recursively imports, exports, removes or re-installs all manifest.txt files found under the directory"
import argparse
import sys
from movai_developer_tools.utils import logger
from movai_developer_tools.movbkp.import_metadata.operation_executer import Importer
from movai_developer_tools.movbkp.export_metadata.operation_executer import Exporter
from movai_developer_tools.movbkp.remove_metadata.operation_executer import Remover
from movai_developer_tools.movbkp.reinstall_metadata.operation_executer import (
    ReInstaller,
)

executors = {
    "import": Importer,
    "export": Exporter,
    "remove": Remover,
    "re-install": ReInstaller,
}


def handle():
    """Entrypoint method of the package. It handles commands to the executers"""
    parser = argparse.ArgumentParser(
        description=f"This component containes backup {', '.join(map(str, executors))} tools used on MOV.AI metadata files when developing with MOV.AI"
    )

    parser.add_argument(
        "command",
        help=f"Command to be executed. Options are ({', '.join(executors.keys())})",
    )
    parser.add_argument(
        "--dry",
        help=f"Dry run commands {', '.join(map(str, executors))} without modifiying any files",
        action="store_true",
    )
    parser.add_argument(
        "--dir",
        help="Directory to search manifests, defaults to CWD",
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
        sys.exit(1)

    executor.execute(args)


if __name__ == "__main__":
    handle()
