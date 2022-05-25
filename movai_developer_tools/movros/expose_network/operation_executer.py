"""Module where all the behaviour of a command should be destributed."""
import movai_developer_tools.utils.logger as logging
from movai_developer_tools.movmisc.spawner.operation_executer import Spawner
from movai_developer_tools.movmisc.ros_master.operation_executer import RosMaster
from pathlib import Path


class ExposeNetwork:
    """Main class to expose ros topics, services and parameters from docker to the host"""

    def __init__(self):
        """If your executor requires some initialization, use the class constructor for it"""
        logging.debug("ExposeNetwork Init")
        # ROS instllation dir
        self.ros_install_dir = "/opt/ros"

    # def get_file_docker(self, path: str) -> :

    def execute(self, args):
        """Method where the main behaviour of the executer should be"""
        logging.debug(f"Execute ExposeNetwork behaviour with args: {args}")
        # Validate if ROS LTS is installed in the host
        supported_ros_distros = ["noetic", "melodic"]
        ros_installed = False
        for ros_distro in supported_ros_distros:
            if Path(f"{self.ros_install_dir}" + f"/{ros_distro}/setup.bash").is_file():
                ros_installed = True
                break

        # Exit if ros is not installed
        if not ros_installed:
            logging.error(
                f"No supported ROS distribution ({supported_ros_distros}) is installed, aborting ROS setup"
            )
            return 1

        # Make args for calling other services
        # Silence the log output from other services because the function is being used internally
        # Only the return value is used and not the printed one
        args.silent = True
        # Get ip of the spawner and ros-master container networks
        args.sub_command = "ip"
        spawner_ip = Spawner().execute(args)
        ros_master_ip = RosMaster().execute(args)
        # Get gateway of the spawner container network
        args.sub_command = "gateway"
        spawner_gateway = Spawner().execute(args)

        # TODO: Update docker entry point script: Check and add export ROS_IP={spawner_ip}
        # Get docker entry point file

        # Check if the export ROS_IP is already in docker entrypoint, and export it if not
        # if [[ $(docker exec -it "${container_name}" sh -c "grep -q 'export ROS_IP=${spawner_ip}' /usr/local/bin/docker-entrypoint.sh && echo 1 || echo 0" | grep -o -E '[0-1]+') == 0 ]]
        # then
        #     echo "ROS_IP Not exported in $(mo-spawner-name), exporting: ${spawner_ip}."
        #     docker exec -ituroot "${container_name}" sh -c "sed -i -e '/set -e/a export ROS_IP=${spawner_ip}' /usr/local/bin/docker-entrypoint.sh"
        #     # For the export to take effect, container needs restart
        #     read -p "Container ${container_name} needs to be restarted for changes to take effect. Do you want to restart ${container_name} now? (Y/n)" -n 1 -r
        #     echo
        #     if [[ $REPLY =~ ^[Yy]$ ]]
        #     then
        #         docker restart "${container_name}" > /dev/null
        #     else
        #         echo "Skipping restart!"
        #     fi
        # fi

        # # Check if in spawner's bashrc
        # if [[ $(docker exec -it "${container_name}" sh -c "grep -q 'export ROS_IP=${spawner_ip}'  /opt/mov.ai/.bashrc && echo 1 || echo 0" | grep -o -E '[0-1]+') == 0 ]]
        # then
        #     docker exec -it "${container_name}" sh -c "echo '\nexport' ROS_IP=${spawner_ip} >> /opt/mov.ai/.bashrc"
        # fi

        # export ROS_IP="${host_ip}"
        # export ROS_MASTER_URI="http://${master_ip}:11311/"
        # echo "ROS environment variables ROS_IP and ROS_MASTER_URI exported. You can now use your ROS tools :)"

        # TODO: Update docker bashrc: Add ROS_IP
        # TODO: Export ROS_IP and ROS_MASTER_URI to the host
        # export ROS_IP="${gateway}"
        # export ROS_MASTER_URI="http://${ros_master_ip}:11311/"
        # echo "ROS environment variables ROS_IP and ROS_MASTER_URI exported. You can now use your ROS tools :)"
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
