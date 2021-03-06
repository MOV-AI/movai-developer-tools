[![pages-build-deployment](https://github.com/MOV-AI/movai-developer-tools/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/MOV-AI/movai-developer-tools/actions/workflows/pages/pages-build-deployment)

# MOV.AI developer tools
A python package build to facilitate development when using MOV.AI.

## Motivation
During development we need to perform tasks that in some cases involve executing long commands.
The scripts in this repository try to shorten those commands thus making development more efficient.
Besides that, we are also avoiding to have to enter the spawner container to perform tasks.
That is done by exposing the more frequent commands on the host.

## Installation
Simply execute the following:
`python3 -m pip install -i https://artifacts.cloud.mov.ai/repository/pypi-integration/simple --extra-index-url https://pypi.org/simple movai-developer-tools`

## Features
### MOV.AI object backup tools
* `movbkp` - Recursively imports or exports or re-installs all manifest.txt files found under the directory
  * `import` - Imports the metadata specified in the found manifest.txt
  * `export` - Exports the metadata specified in the found manifest.txt
  * `remove` - Removes the metadata specified in the found manifest.txt
  * `re-install` - Imports all the metadata from installed packages in the spawner container
  * `--directory` - Directory to search manifests, defaults to CWD
  * `--dry-run` - Dry run any command without modifiying any files

### ROS tools
* `movros` - ROS related functions
  * `expose-network` - Exports all the necessary vars so that host ROS system can communicate with MOV.AI's ROS master. (Only if the host has a ROS LTS installation.)

### MOV.AI application container tools
* `movcontainer` - MOV.AI containers related functions
  * `spawner` - Spawner container related functions
    * `ip` - Prints IP of the container
    * `id` - Prints short ID of the container
    * `name` - Prints name of the container
    * `gateway` - Prints Host virtual IP in the docker network
    * `userspace-dir` - Prints the mounted userspace directory
    * `logs` - Shows container logs
  * `ros-master` - ROS master container related functions
    * `ip` - Prints IP of the container
    * `id` - Prints short ID of the container
    * `name` - Prints name of the container
    * `gateway` - Prints Host virtual IP in the docker network
    * `userspace-dir` - Prints the mounted userspace directory
    * `logs` - Shows container logs

## Full documentation
Full documentation of this python package is hosted at https://mov-ai.github.io/movai-developer-tools/
