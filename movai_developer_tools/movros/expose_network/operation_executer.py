"""Module where all the behaviour of a command should be destributed."""
import movai_developer_tools.utils.logger as logging
from movai_developer_tools.movmisc.spawner.operation_executer import Spawner
from movai_developer_tools.movmisc.ros_master.operation_executer import RosMaster
from pathlib import Path
import sys
import tarfile
from io import BytesIO
import time


class ExposeNetwork:
    """Main class to expose ros topics, services and parameters from docker to the host"""

    def __init__(self):
        """If your executor requires some initialization, use the class constructor for it"""
        logging.debug("ExposeNetwork Init")
        # ROS instllation dir
        self.ros_install_dir = "/opt/ros"
        # Supported ROS distors
        self.supported_ros_distros = ["noetic", "melodic"]

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

        # Spawner class
        self.spawner = Spawner()
        # RosMaster class
        self.ros_master = RosMaster()

    def validate_ros_installation(self):
        """Validate supported ROS installation in the host"""
        # Validate if ROS LTS is installed in the host
        ros_installed = False
        for ros_distro in self.supported_ros_distros:
            if Path(f"{self.ros_install_dir}" + f"/{ros_distro}/setup.bash").is_file():
                ros_installed = True
                return True

        # Exit if ros is not installed
        if not ros_installed:
            logging.error(
                f"No supported ROS distribution ({self.supported_ros_distros}) is installed, aborting ROS setup"
            )
            sys.exit(1)

    def get_file_content(self, file) -> tuple:
        """Returns a tuple (content, stats). Content is with binary string items of the given file in the spawner container.
        For more information on the stats, follow this link: https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.Container.get_archive
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

    def write_file_to_tar(self, tarname, tardata, tarinfo):
        """Write a tar file given a binary string (tardata) and tarinfo"""
        with BytesIO() as f_bytesio:
            # Make tarfile with modified info
            with tarfile.open(fileobj=f_bytesio, mode="w:tar") as tar:
                tar.addfile(tarinfo=tarinfo, fileobj=BytesIO(tardata))
            f_bytesio.seek(0)
            # Write tarfile
            with open(tarname, "wb") as out:
                out.write(f_bytesio.read())

    def yes_or_no(self, question) -> bool:
        """Return bool based on user input"""
        reply = str(input(question + " (Y/n): ")).lower().strip()
        if reply[0] == "y":
            return True
        if reply[0] == "n":
            return False
        else:
            return self.yes_or_no(question)

    def generate_tarinfo(self, filename, data, mode):
        """Generate tarinfo from args"""
        tar_info = tarfile.TarInfo(filename)
        tar_info.mtime = time.time()
        tar_info.mode = mode
        tar_info.size = len(data)
        return tar_info

    def execute(self, args):
        """Method where the main behaviour of the executer should be"""
        logging.debug(f"Execute ExposeNetwork behaviour with args: {args}")

        # Make args for calling other services
        # Silence the log output from other services because the function is being used internally
        # Only the return value is used and not the printed one
        args.silent = True
        # Get spawner name
        args.sub_command = "name"
        spawner_name = self.spawner.get_spawner_name(args)
        # Get ip of the spawner and ros-master container networks
        args.sub_command = "ip"
        spawner_ip = self.spawner.execute(args)
        ros_master_ip = self.ros_master.execute(args)
        # Get gateway of the spawner container network
        args.sub_command = "gateway"
        spawner_gateway = self.spawner.execute(args)

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
            logging.info(
                f"ROS_IP Not exported in {spawner_name} docker-entrypoint, exporting: {spawner_ip}."
            )
            if set_e_lineno is not None:
                content = (
                    content[: set_e_lineno + 1]
                    + [export_bstring]
                    + content[set_e_lineno + 1 :]
                )
            else:
                logging.error(
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
                f"Container ${spawner_name} needs to be restarted for changes to take effect. Do you want to restart ${spawner_name} now?"
            )
            if reply:
                self.spawner.restart()
            else:
                logging.info("Skipping restart!")

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
            logging.info(
                f"ROS_IP Not exported in {spawner_name} bashrc, exporting: {spawner_ip}."
            )
            content.append(export_bstring)

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

        logging.info(
            f"spawner_ip: {spawner_ip}, ros_master_ip: {ros_master_ip}, spawner_gateway: {spawner_gateway}"
        )

    @staticmethod
    def add_expected_arguments(parser):
        """Method exposed for the handle to append our executer arguments."""
        # parser.add_argument(
        #     "--executor_specific_arg",
        #     help="specific argument needed for this executor",
        # )
