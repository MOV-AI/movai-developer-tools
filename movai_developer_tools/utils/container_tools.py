"""Module that contains a wrapper container_tools to ease interacting with the python docker module"""
import docker


def get_container_by_name_regex(regex):
    """Return a container object with matching regex name search"""
    client = docker.from_env()
    containers = client.containers.list(filters={"name": regex})
    return containers


def get_container_ip(regex):
    """Return a container ip given a regex string to compare against the name."""
    containers = get_container_by_name_regex(regex)
    if containers:
        networks = containers[0].attrs["NetworkSettings"]["Networks"]
        network = next(iter(networks))
        ip = networks[network]["IPAddress"]
        return ip
    return None


def get_container_id(regex):
    """Get short id of a container found using regex of the name"""
    containers = get_container_by_name_regex(regex)
    if containers:
        short_id = containers[0].short_id
        return short_id
    return None


def get_container_name(regex):
    """Get the name of a container found using regex"""
    containers = get_container_by_name_regex(regex)
    if containers:
        name = containers[0].name
        return name
    return None


def get_container_gateway(regex):
    """Get gateway of the first network of a container found using regex of the name"""
    containers = get_container_by_name_regex(regex)
    if containers:
        networks = containers[0].attrs["NetworkSettings"]["Networks"]
        network = next(iter(networks))
        gateway = networks[network]["Gateway"]
        return gateway
    return None


if __name__ == "__main__":
    regex_spawner_name = "^spawner-.*"
    print(get_container_ip(regex_spawner_name))
    print(get_container_id(regex_spawner_name))
    print(get_container_name(regex_spawner_name))
    print(get_container_gateway(regex_spawner_name))
