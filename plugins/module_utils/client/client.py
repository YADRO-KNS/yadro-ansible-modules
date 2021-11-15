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


def create_client(hostname, auth, base_prefix="/redfish/v1/",
                  validate_certs=True, port=443, timeout=30):

    client = OpenBmcRestClient(hostname=hostname, auth=auth, base_prefix=base_prefix,
                               validate_certs=validate_certs, port=port, timeout=timeout)

    systems = client.get_system_collection()
    if len(systems) != 1:
        raise UnsupporedSystemError("Operations with only one BMC system supported. Found: {0}"
                                    .format(len(systems)))

    supported_systems = {
        "VEGMAN S220 Server": VegmanBmcRestClient,
        "Mockup Server": DMTFMockupRestClient,
    }

    system_info = client.get_system_by_id(systems[0])
    try:
        client.__class__ = supported_systems[system_info["Model"]]
    except KeyError:
        raise UnsupporedSystemError("System unsupported: {0}. Known systems: {1}".format(
            system_info["Model"], supported_systems.keys()))

    managers = client.get_managers_collection()
    if len(managers) != 1:
        raise UnsupporedSystemError("Operations with only one BMC manager supported. Found: {0}"
                                    .format(len(managers)))

    return client
