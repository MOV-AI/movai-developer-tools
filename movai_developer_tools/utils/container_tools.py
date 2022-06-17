"""Module that contains methods to ease interacting with the python docker module in the context of docker containers from MOV.AI."""
from movai_developer_tools.utils import logger
import docker
import sys
import time
import typing
from docker.models.containers import ExecResult


class ContainerTools:
    """Wrapper over docker API functions that are useful when developing with MOV.AI platform.

    Args:
        regex: The regular expression used to find the docker container object by name.
        userspace_bind_dir: The directory where the userspace is mounted. Defaults to ``"/opt/mov.ai/user"``.

    Attributes:
        userspace_bind_dir (str): The directory where the userspace is mounted. Defaults to ``"/opt/mov.ai/user"``.
        container (Container): The container object found using the regular expression.

    """

    def __init__(
        self,
        regex: str,
        userspace_bind_dir: str = "/opt/mov.ai/user",
    ) -> None:
        # Container userspace bind location
        self.userspace_bind_dir = userspace_bind_dir

        # Get container object with regex search over name, exit if not found
        client = docker.from_env()
        containers = client.containers.list(filters={"name": regex})
        if containers:
            self.container = containers[0]
        else:
            logger.error(
                f"Did not find a runnning container with name search: Regex used {regex}"
            )
            sys.exit(1)

    def ip(self) -> str:
        """Return a container ip given a regex string to compare against the name.

        Returns:
            The IP of the container.

        """
        networks = self.container.attrs["NetworkSettings"]["Networks"]
        network = next(iter(networks))
        ip = networks[network]["IPAddress"]
        return ip

    def id(self) -> str:
        """Get short id of a container found using regex of the name.

        Returns:
            Short ID of the container.

        """
        return self.container.short_id

    def name(self) -> str:
        """Get the name of a container found using regex.

        Returns:
            The name of the container.

        """
        return self.container.name

    def gateway(self) -> str:
        """Get gateway of the first network of a container found using regex of the name.

        Returns:
            The gateway of the container.

        """
        networks = self.container.attrs["NetworkSettings"]["Networks"]
        network = next(iter(networks))
        gateway = networks[network]["Gateway"]
        return gateway

    def get_archive(self, path: str) -> tuple:
        """Wrapper over archive API.

        Args:
            path: Path to the file or folder to retrieve.

        Returns:
            First element is a raw tar data stream. Second element is
            a dict containing ``stat`` information on the specified ``path``.

        """
        return self.container.get_archive(path)

    def put_archive(self, path: str, data: bytes) -> bool:
        """Wrapper over put_archive API.

        Args:
            path: Path inside the container where the file(s) will be
                extracted. Must exist.
            data: tar data to be extracted

        Returns:
            The return value. True for success, False otherwise.

        """
        return self.container.put_archive(path, data)

    def restart(self) -> None:
        """Wrapper over restart API."""
        self.container.restart()

    def userspace_dir(self) -> str:
        """Return userspace that is mounted in the container.

        Returns:
            The userspace directory path in the host.

        """
        binds = self.container.attrs["HostConfig"]["Binds"]
        # Check the bind at self.userspace_bind_dir, which is where the userspace is mounted
        userspace_dir = None
        for bind in binds:
            _split = bind.split(":")
            if _split[1] == self.userspace_bind_dir:
                userspace_dir = _split[0]
                return userspace_dir

        # Exit if userspace is not found
        logger.info("Userspace not mounted.")
        sys.exit(1)

    def logs(
        self,
        tail: typing.Union[int, str] = 100,
        follow: bool = True,
        stream: bool = True,
    ) -> None:
        """Wrapper over logs API.

        Args:
            tail: Output specified number of lines at the end of logs.
                Either an integer of number of lines or the string ``all``.
                Defaults to``100``.
            follow: Follow log output. Default ``True``
            stream: Stream the response. Defaults to ``True``.

        Todo:
            Find better alternatice for while loop to print logs.

        """
        # Get logs stream
        logs_stream = self.container.logs(tail=tail, follow=follow, stream=stream)
        # Print stream, exit on keyboard interrupt
        try:
            while True:
                # Remove the "\n" to remove the empty line after every print
                # Using print to keep the same color and structure of docker logs
                print(logs_stream.next().decode().strip("\n"))
                # Sleep 0.1ms, keep printing logs very fast.
                time.sleep(0.0001)
        except KeyboardInterrupt:
            logger.info("Recieved keyboard interrupt, exiting.")
            sys.exit()

    def exec_run(
        self,
        cmd: str = "echo 'Hi there, I am an echo being executed in the container you have chosen. Please use [--cmd=EXEC_COMMAND] to specify the command you want to run'",
        user: str = "movai",
        environment: list = [],
    ) -> ExecResult:
        """Wrapper over exec_run API.

        Args:
            cmd: Command to be executed.
            user: User to execute command as. Default: movai
            environment: A dictionary or a list of strings in the following format
                        ``["PASSWORD=xxx"]`` or ``{"PASSWORD": "xxx"}``.

        Returns:
            A tuple of (exit_code, output)
                exit_code: (int):
                    Exit code for the executed command or ``None`` if
                    either ``stream`` or ``socket`` is ``True``.
                output: (generator, bytes, or tuple):
                    If ``stream=True``, a generator yielding response chunks.
                    If ``socket=True``, a socket object for the connection.
                    If ``demux=True``, a tuple of two bytes: stdout and stderr.
                    A bytestring containing response data otherwise.

        """
        exec_result = self.container.exec_run(
            cmd=["bash", "-c", cmd],
            user=user,
            environment=environment,
        )
        return exec_result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="This component helps to retrieve docker container information developing with MOV.AI."
    )
    parser.add_argument(
        "--name-regex",
        help="Container name search regex",
        default=None,
    )
    parser.add_argument(
        "--sub-command",
        help="Property of the component to be fetched, options are (ip, id, name, gateway, userspace-dir, logs)",
        default=None,
    )

    args = parser.parse_args()

    if args.name_regex is None:
        logger.info(
            "Using default value of the regex (^spawner-.*) to find the container"
        )
        container_tools = ContainerTools("^spawner-.*")
    else:
        container_tools = ContainerTools(args.name_regex)

    valid_sub_commands = ["ip", "id", "name", "userspace-dir", "gateway", "restart"]
    # If no specific command is given
    if args.sub_command is None:
        logger.info(
            f"No sub-command given, Executing ip, id, name, userspace-dir and gateway methods of the {container_tools.name()} container"
        )
        print(container_tools.ip())
        print(container_tools.id())
        print(container_tools.name())
        print(container_tools.userspace_dir())
        print(container_tools.gateway())
    elif args.sub_command in valid_sub_commands:
        arg_to_method = {
            "ip": container_tools.ip,
            "id": container_tools.id,
            "name": container_tools.name,
            "userspace-dir": container_tools.userspace_dir,
            "gateway": container_tools.gateway,
            "restart": container_tools.restart,
        }
        print(arg_to_method[args.sub_command]())
    else:
        logger.error(f"Invalid sub-command, valid values are: {valid_sub_commands}")
