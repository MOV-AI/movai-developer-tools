"""Module that contains a wrapper container_tools to ease interacting with the python docker module"""
from movai_developer_tools.utils import logger
import docker
import sys
import time


class ContainerTools:
    """Set of methods to help access docker functions using the API"""

    def __init__(self, regex) -> None:
        """Constructor for container tools class"""
        self.regex = regex
        # Container userspace bind location
        self.container_bind_dir = "/opt/mov.ai/user"

    def get_obj_by_name_regex(self):
        """Return a container object with matching regex name search, if not found exit"""
        client = docker.from_env()
        containers = client.containers.list(filters={"name": self.regex})
        if containers:
            return containers[0]
        else:
            logger.error(
                f"Did not find a runnning container with name search: Regex used {self.regex}"
            )
            sys.exit(1)

    def get_ip(self):
        """Return a container ip given a regex string to compare against the name."""
        container = self.get_obj_by_name_regex()
        networks = container.attrs["NetworkSettings"]["Networks"]
        network = next(iter(networks))
        ip = networks[network]["IPAddress"]
        # Log if not silent
        if not self.args.silent:
            logger.info(f"IPAddress: {ip}")
        return ip

    def get_id(self):
        """Get short id of a container found using regex of the name"""
        container = self.get_obj_by_name_regex()
        short_id = container.short_id
        # Log if not silent
        if not self.args.silent:
            logger.info(f"Short ID: {short_id}")
        return short_id

    def get_name(self):
        """Get the name of a container found using regex"""
        container = self.get_obj_by_name_regex()
        name = container.name
        # Log if not silent
        if not self.args.silent:
            logger.info(f"Name: {name}")
        return name

    def get_gateway(self):
        """Get gateway of the first network of a container found using regex of the name"""
        container = self.get_obj_by_name_regex()
        networks = container.attrs["NetworkSettings"]["Networks"]
        network = next(iter(networks))
        gateway = networks[network]["Gateway"]
        # Log if not silent
        if not self.args.silent:
            logger.info(f"Gateway: {gateway}")
        return gateway

    def get_archive(self, path):
        """Wrapper over get_archive api in the container found using regex of the name"""
        container = self.get_obj_by_name_regex()
        return container.get_archive(path)

    def put_archive(self, path, data):
        """Wrapper over put_archive api in the container found using regex of the name"""
        container = self.get_obj_by_name_regex()
        return container.put_archive(path, data)

    def restart(self):
        """Wrapper over restart api in the container found using regex of the name"""
        container = self.get_obj_by_name_regex()
        return container.restart()

    def get_userspace_dir(self):
        """Return userspace that is mounted in the container"""
        container = self.get_obj_by_name_regex()
        binds = container.attrs["HostConfig"]["Binds"]
        # Check the bind at "/opt/mov.ai/user", which is where the userspace is mounted
        userspace_dir = None
        for bind in binds:
            _split = bind.split(":")
            if _split[1] == self.container_bind_dir:
                userspace_dir = _split[0]
                # Log if not silent
                if not self.args.silent:
                    logger.info(f"Userspace directory: {userspace_dir}")
                return userspace_dir

        # Exit if userspace is not found
        logger.info("Userspace not mounted.")
        sys.exit(1)

    def logs(self):
        """Get logs of the container"""
        container = self.get_obj_by_name_regex()
        # Get logs stream
        logs_stream = container.logs(tail=100, follow=True, stream=True)
        # Print stream, exit on keyboard interrupt
        try:
            while True:
                # Remove the "\n" to remove the empty line after every print
                # Using print to keep the same color and structure of docker logs
                print(logs_stream.next().decode().strip("\n"))
                # Sleep 0.1ms, keep printing logs very fast.
                # TODO: Better method that while loop?.
                time.sleep(0.0001)
        except KeyboardInterrupt:
            logger.info("Recieved keyboard interrupt, exiting.")
            sys.exit()

    def exec(self):
        """Execute given command inside the container, user:movai"""
        container = self.get_obj_by_name_regex()
        exit_code, output = container.exec_run(
            cmd=["bash", "-c", self.args.cmd],
            user=self.args.user,
            environment=self.args.env,
        )
        # Log if not silent
        if not self.args.silent:
            # Log output in ascii
            print(f"{output.decode('ascii')}")
        return output


if __name__ == "__main__":
    regex_spawner_name = "^spawner-.*"
    container_tools = ContainerTools(regex_spawner_name)
    print(f"Spawner ip: {container_tools.get_ip()}")
    print(f"Spawner id:  {container_tools.get_id()}")
    print(f"Spawner name: {container_tools.get_name()}")
    print(f"Spawner gateway: {container_tools.get_gateway()}")
    print(f"Spawner container obj: {container_tools.get_obj_by_name_regex()}")
