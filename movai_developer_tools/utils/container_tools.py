"""Module that contains a wrapper container_tools to ease interacting with the python docker module"""
import logging
import docker
import sys


def get_container_obj_by_name_regex(regex):
    """Return a container object with matching regex name search, if not found exit"""
    client = docker.from_env()
    containers = client.containers.list(filters={"name": regex})
    if containers:
        return containers[0]
    else:
        logging.error(f"Did not find a runnning spawner container: Regex used {regex}")
        sys.exit(1)


def get_container_ip(regex):
    """Return a container ip given a regex string to compare against the name."""
    container = get_container_obj_by_name_regex(regex)
    networks = container.attrs["NetworkSettings"]["Networks"]
    network = next(iter(networks))
    ip = networks[network]["IPAddress"]
    return ip


def get_container_id(regex):
    """Get short id of a container found using regex of the name"""
    container = get_container_obj_by_name_regex(regex)
    short_id = container.short_id
    return short_id


def get_container_name(regex):
    """Get the name of a container found using regex"""
    container = get_container_obj_by_name_regex(regex)
    name = container.name
    return name


def get_container_gateway(regex):
    """Get gateway of the first network of a container found using regex of the name"""
    container = get_container_obj_by_name_regex(regex)
    networks = container.attrs["NetworkSettings"]["Networks"]
    network = next(iter(networks))
    gateway = networks[network]["Gateway"]
    return gateway


if __name__ == "__main__":
    regex_spawner_name = "^spawner-.*"
    print(f"Spawner ip: {get_container_ip(regex_spawner_name)}")
    print(f"Spawner id:  {get_container_id(regex_spawner_name)}")
    print(f"Spawner name: {get_container_name(regex_spawner_name)}")
    print(f"Spawner gateway: {get_container_gateway(regex_spawner_name)}")
    print(
        f"Spawner container obj: {get_container_obj_by_name_regex(regex_spawner_name)}"
    )
