"""Module that contains a wrapper container_tools to ease interacting with the python docker module"""
import docker
import re


def get_container_ip(regex):
    """Return a container ip given a regex string to compare against the name."""
    client = docker.from_env()
    containers = client.containers.list()
    for container in containers:
        name = container.name
        networks = container.attrs["NetworkSettings"]["Networks"]
        if re.search(regex, name):
            network = next(iter(networks))
            ip = networks[network]["IPAddress"]
            return ip
    return None


def get_container_id(regex):
    """Get short id of a container found using regex of the name"""
    client = docker.from_env()
    containers = client.containers.list()
    for container in containers:
        name = container.name
        short_id = container.short_id
        if re.search(regex, name):
            return short_id
    return None


def get_container_name(regex):
    """Get the name of a container found using regex"""
    client = docker.from_env()
    containers = client.containers.list()
    for container in containers:
        name = container.name
        if re.search(regex, name):
            return name
    return None


def get_container_gateway(regex):
    """Get gateway of the first network of a container found using regex of the name"""
    client = docker.from_env()
    containers = client.containers.list()
    for container in containers:
        name = container.name
        networks = container.attrs["NetworkSettings"]["Networks"]
        if re.search(regex, name):
            network = next(iter(networks))
            gateway = networks[network]["Gateway"]
            return gateway
    return None
