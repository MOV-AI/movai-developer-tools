from movai_developer_tools.utils import logger
from movai_developer_tools.utils.container_tools import ContainerTools
from pathlib import Path
import sys
import tarfile
from io import BytesIO
import time


class ExposeNetwork:
    """Main class to expose ros topics, services and parameters from docker to the host.

    Attributes:
        ros_install_dir (str): ROS installation directory.
        supported_ros_distros (set): Supported ROS distors.
        entrypoint_dir (str): Docker-entrypoint directory.
        entrypoint_filename (str): Docker-entrypoint filename.
        temp_ep_tar (str): Temporary place to store the docker-entrypoint tar file.
        bashrc_dir (str): Bashrc directory.
        bashrc_filename (str): Bashrc filename.
        temp_bashrc_tar (str): Temporary place to store the bashrc tar file.
        spawner (Spawner): Spawner class instance.
        ros_master (RosMaster): RosMaster class instance.
        ros_distro (str): ROS distro that is installed in the host.

    """

    def __init__(self) -> None:
        logger.debug("ExposeNetwork Init")
        # ROS instllation dir
        self.ros_install_dir = "/opt/ros"
        # Supported ROS distors
        self.supported_ros_distros = {"noetic", "melodic"}

        # Docker-entrypoint dir
        self.entrypoint_dir = "/usr/local/bin"
        # Docker-entrypoint filename
        self.entrypoint_filename = "docker-entrypoint.sh"
        # Temporary place to store the tar file
        self.temp_ep_tar = "/tmp/docker-entrypoint.tar"

        # Bashrc dir
        self.bashrc_dir = "/opt/mov.ai"
        # Bashrc filename
        self.bashrc_filename = ".bashrc"
        # Temporary place to store the tar file
        self.temp_bashrc_tar = "/tmp/bashrc.tar"

        # Instanciate spawner container class
        # Reg expressions for finding the spawner container
        regex_spawner_name = "^spawner-.*"
        # Instanciate for silent operation if silent arg is True, else take default
        self.spawner = ContainerTools(regex_spawner_name, silent=True)

        # Instanciate ros-master container class
        # Reg expressions for finding the ros-master container
        regex_ros_master_name = "^ros-master-.*"
        # Instanciate for silent operation if silent arg is True, else take default
        self.ros_master = ContainerTools(regex_ros_master_name, silent=True)

        # ROS distro in host
        self.ros_distro = None

    def validate_ros_installation(self) -> bool:
        """Validate ROS LTS installation in the host.

        Returns:
            The return value. True if any ROS LTS version is installed, Exit otherwise.

        """
        # Validate if ROS LTS is installed in the host
        ros_installed = False
        for ros_distro in self.supported_ros_distros:
            if Path(f"{self.ros_install_dir}" + f"/{ros_distro}/setup.bash").is_file():
                ros_installed = True
                self.ros_distro = ros_distro
                return True

        # Exit if ros is not installed
        if not ros_installed:
            logger.error(
                f"No supported ROS distribution ({self.supported_ros_distros}) is installed, aborting ROS setup"
            )
            sys.exit(1)

    def get_file_content(self, file: str) -> tuple:
        """Get a file from given spawner and converts the data into a list of byetes.
        For more information on the stats, follow this link: https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.Container.get_archive

        Args:
            file: File to be fetched inside the container.

        Returns:
            A tuple with content (list(bytes)) and stats (dict)

        """
        bits, stats = self.spawner.get_archive(file)
        # Use bytesio file to generate a tarfile to read content
        with BytesIO() as file_obj:
            for i in bits:
                file_obj.write(i)
            file_obj.seek(0)
            with tarfile.open(mode="r", fileobj=file_obj) as tar:
                for member in tar:
                    file = tar.extractfile(member)
                    content = file.readlines()
        return content, stats

    def write_file_to_tar(
        self, tarname: str, tardata: bytes, tarinfo: tarfile.TarInfo
    ) -> None:
        """Write a tar file given a name, data and tarinfo.

        Args:
            tarname: Name of the tarfile.
            tardata: Data to be written into tarfile.
            tarinfo: Info file for tar objects.

        """
        with BytesIO() as f_bytesio:
            # Make tarfile with modified info
            with tarfile.open(fileobj=f_bytesio, mode="w:tar") as tar:
                tar.addfile(tarinfo=tarinfo, fileobj=BytesIO(tardata))
            f_bytesio.seek(0)
            # Write tarfile
            with open(tarname, "wb") as out:
                out.write(f_bytesio.read())

    def yes_or_no(self, question: str) -> bool:
        """Accepts Y/n input from user.

        Args:
            question: The question to be asked to the user.

        Returns:
            The return value. True is the user enter an empty value, or Y/y, False otherwise.

        """
        reply = str(input(question + " (Y/n): ")).lower().strip()
        if reply == "" or reply[0] == "y":
            return True
        if reply[0] == "n":
            return False
        else:
            return self.yes_or_no(question)

    def generate_tarinfo(
        self, filename: str, data: bytes, mode: int
    ) -> tarfile.TarInfo:
        """Generate tarinfo from filename, data and mode.

        Args:
            filename: Name of the file inside the tarfile.
            data: Data inside the tarfile.
            mode: Permissions of the data inside the tarfile.

        Returns:
            A TarInfo file with pre-filled information.

        """
        tar_info = tarfile.TarInfo(filename)
        tar_info.mtime = time.time()
        tar_info.mode = mode
        tar_info.size = len(data)
        return tar_info

    def execute(self) -> None:
        """Execute the expose-network behaviour."""
        # Get spawner name
        spawner_name = self.spawner.get_name()
        # Get ip of the spawner and ros-master containers
        spawner_ip = self.spawner.get_ip()
        ros_master_ip = self.ros_master.get_ip()
        # Get gateway of the spawner container network
        spawner_gateway = self.spawner.get_gateway()

        # Validate ROS host installation
        self.validate_ros_installation()

        # Get docker-entrypoint.sh
        content, stats = self.get_file_content(
            self.entrypoint_dir + "/" + self.entrypoint_filename
        )

        # Check if export line exists, and get set -e string line number
        export_bstring = f"export ROS_IP={spawner_ip}\n".encode()
        # Set e string line in binary (used as anchor to place the export line in entrypoint)
        set_e_bstring = "set -e\n".encode()
        export_exists = False
        set_e_lineno = None
        for i, line in enumerate(content):
            # Check if export_bstring exists
            if export_bstring == line:
                export_exists = True
                break
            # Get lineno of the set_e_bstring
            if set_e_bstring == line:
                set_e_lineno = i

        # If export does not exist, add it, then request restart
        if not export_exists:
            logger.info(
                f"ROS_IP Not exported in {spawner_name} docker-entrypoint, exporting: {spawner_ip}."
            )
            if set_e_lineno is not None:
                content = (
                    content[: set_e_lineno + 1]
                    + [b"\n" + export_bstring]
                    + content[set_e_lineno + 1 :]
                )
            else:
                logger.error(
                    "Not able to find the line number of the set -e command in docker-entrypoint.sh script, exiting"
                )
                sys.exit(1)

            # Save modified file to temporary tar
            # Join mofied list
            modified_content = b"".join(content)
            # Generate tarinfo object from stats
            tar_info = self.generate_tarinfo(
                self.entrypoint_filename, modified_content, stats["mode"]
            )

            # Save
            self.write_file_to_tar(self.temp_ep_tar, modified_content, tar_info)

            # Copy modified file to docker
            data = open(self.temp_ep_tar, "rb").read()
            self.spawner.put_archive(self.entrypoint_dir, data)

            # Request restart
            reply = self.yes_or_no(
                f"Container {spawner_name} needs to be restarted for changes to take effect. Do you want to restart {spawner_name} now?"
            )
            if reply:
                self.spawner.restart()
            else:
                logger.info("Skipping restart!")

        # Check if export is in spawner's bashrc
        # Get bash.rc file
        content, stats = self.get_file_content(
            self.bashrc_dir + "/" + self.bashrc_filename
        )
        export_exists = False
        for line in content:
            if export_bstring == line:
                export_exists = True
                break

        # If export does not exist, add it
        if not export_exists:
            logger.info(
                f"ROS_IP Not exported in {spawner_name} bashrc, exporting: {spawner_ip}."
            )
            # Add a new line before
            content += [b"\n" + export_bstring]

            # Save modified file to temporary tar
            # Join mofied list
            modified_content = b"".join(content)
            # Update tarinfo
            # Generate tarinfo object from stats
            tar_info = self.generate_tarinfo(
                self.bashrc_filename, modified_content, stats["mode"]
            )

            # Save
            self.write_file_to_tar(self.temp_bashrc_tar, modified_content, tar_info)

            # Copy modified file to docker
            data = open(self.temp_bashrc_tar, "rb").read()
            self.spawner.put_archive(self.bashrc_dir, data)

        # Print user actions
        logger.info(
            "Please execute these below commands in your terminal to finalize the procedure.\nUse rostopic list and rostopic echo <topic> to confirm your have access to topics in your host:)"
        )
        print(
            f'\nsource {self.ros_install_dir}/{self.ros_distro}/setup.bash\nexport ROS_IP="{spawner_gateway}"\nexport ROS_MASTER_URI="http://{ros_master_ip}:11311/"'
        )

    @staticmethod
    def add_expected_arguments(parser):
        """Method exposed for the handle to append our executer arguments."""
