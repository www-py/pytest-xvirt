from typing import List

import pytest

from xvirt import XVirt
from xvirt.plugin_remote import XvirtPluginRemote
from xvirt.plugin_server import XvirtPluginServer


@pytest.hookimpl
def pytest_addhooks(pluginmanager):
    from xvirt import newhooks

    pluginmanager.add_hookspecs(newhooks)


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config) -> None:
    xvirt_packages = []
    xvirt_instances: List[XVirt] = config.hook.pytest_xvirt_setup(config=config, xvirt_packages=xvirt_packages)
    instances_count = len(xvirt_instances)
    if instances_count == 0:
        config.pluginmanager.register(XvirtPluginRemote(config), "xvirt-plugin-remote")
        return
    if instances_count != 1:
        raise Exception('multiple xvirt users not supported')

    xvirt_instance = xvirt_instances[0]
    xvirt_instance.config = config
    xvirt_package = xvirt_instance.virtual_path()
    config.pluginmanager.register(XvirtPluginServer(xvirt_instance, config, xvirt_package), "xvirt-plugin-server")


