# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.yadro.obmc.plugins.module_utils.client.bmc import OpenBmcRestClient
from ansible_collections.yadro.obmc.plugins.module_utils.client.vegman import VegmanBmcRestClient
from ansible_collections.yadro.obmc.plugins.module_utils.client.mockup import DMTFMockupRestClient


class UnsupporedSystemError(Exception):
    pass


def create_client(hostname, username, password, base_prefix="/redfish/v1/",
                  validate_certs=True, port=443, timeout=10):

    client = OpenBmcRestClient(hostname=hostname, username=username, password=password,
                               base_prefix=base_prefix, validate_certs=validate_certs,
                               port=port, timeout=timeout)

    systems = client.get_system_collection()["Members"]
    if len(systems) != 1:
        raise UnsupporedSystemError("Operations with only one BMC system supported. Found: {0}"
                                    .format(len(systems)))

    supported_systems = {
        "VEGMAN S220 Server": VegmanBmcRestClient,
        "Mockup Server": DMTFMockupRestClient,
    }

    system_info = client.get_system(systems[0])
    try:
        client.__class__ = supported_systems[system_info["Model"]]
    except KeyError:
        raise UnsupporedSystemError("System unsupported: {0}. Known systems: {1}".format(
            system_info["Model"], supported_systems.keys()))
    return client
