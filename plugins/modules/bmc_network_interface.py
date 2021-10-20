#!/usr/bin/python
# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = r"""
---
module: bmc_network_interface
short_description: Module for managing OpenBmc network interfaces.
version_added: "1.0.0"
description:
  - Configures IP address at specific ethernet device.
  - Enables and disables address resolution via DHCP.
  - Configures interface namespace servers.
  - This module supports check mode.
extends_documentation_fragment:
  - yadro.obmc.connection_options
author: "Radmir Safin (@radmirsafin)"
options:
  name:
    type: str
    required: true
    description: Ethernet interface name to configure.
  dhcp_enabled:
    type: bool
    description:
      - Responsible for interface DHCP activation.
      - Cannot be set to C(true) together I(ipv4_addresses) option.
      - If DHCP is enabled, static network configuration will be lost.
  ipv4_addresses:
    type: list
    elements: dict
    description:
      - List of IP addresses to set at interface.
      - Cannot be configured if I(dhcp_enabled) is C(true).
      - If static configuration is present, DHCP will be disabled.
      - Each IP address record it is dictionary which must contains
        O(gateway), O(address) and O(subnet_mask) keys. For more details look to examples.
  static_nameservers:
    type: list
    elements: str
    description: List of static nameservers assigned to interface.
"""

RETURN = r"""
---
msg:
  type: str
  returned: always
  description: Operation status message.
error_info:
  type: str
  returned: on error
  description: Error details.
"""

EXAMPLES = r"""
---
- name: Setup eth0 dhcp
  yadro.obmc.bmc_network_interface:
    connection:
      hostname: "{{ server }}"
      username: "{{ username }}"
      password: "{{ password }}"
    name: "eth0"
    dhcp_enabled: true

- name: Disable dhcp and set static address
  yadro.obmc.bmc_network_interface:
    connection:
      hostname: "{{ server }}"
      username: "{{ username }}"
      password: "{{ password }}"
    name: "eth0"
    dhcp_enabled: false
    ipv4_addresses:
      - gateway: 192.168.0.1
        address: 192.168.0.2
        subnet_mask: 255.255.255.0
      - gateway: 192.168.0.1
        address: 192.168.0.2
        subnet_mask: 255.255.255.0
    static_nameservers:
      - 192.168.0.100
      - 192.168.0.101

- name: Change static nameservers
  yadro.obmc.bmc_network_interface:
    connection:
      hostname: "{{ server }}"
      username: "{{ username }}"
      password: "{{ password }}"
    name: "eth0"
    static_nameservers:
      - 192.168.1.100
      - 192.168.2.100

- name: Change eth0 ip addresses
  yadro.obmc.bmc_network_interface:
    connection:
      hostname: "{{ server }}"
      username: "{{ username }}"
      password: "{{ password }}"
    name: "eth0"
    ipv4_addresses:
      - gateway: 192.168.0.1
        address: 192.168.0.21
        subnet_mask: 255.255.255.0

- name: Enable DHCP and remove static addresses
  yadro.obmc.bmc_network_interface:
    connection:
      hostname: "{{ server }}"
      username: "{{ username }}"
      password: "{{ password }}"
    name: "eth0"
    dhcp_enabled: true
"""

import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import ConnectionError, SSLValidationError
from ansible.module_utils.six.moves.urllib.error import URLError, HTTPError
from ansible_collections.yadro.obmc.plugins.module_utils.client.client import create_client


def run_module(module):
    params = module.params
    payload = {}

    if params["dhcp_enabled"] and params["ipv4_addresses"]:
        module.fail_json(
            msg="Can't configure network interface.",
            error_info="Conflict between static configuration and DHCP.",
            changed=False,
        )

    client = create_client(**params["connection"])
    interfaces = client.get_ethernet_interface_collection()
    if params["name"] not in interfaces:
        module.fail_json(
            msg="Can't configure network interface.",
            error_info="Interface {0} not found.".format(params["name"]),
            changed=False
        )

    current_config = client.get_ethernet_interface(params["name"])
    if params["dhcp_enabled"] is not None:
        if current_config["DHCPv4"]["DHCPEnabled"] != params["dhcp_enabled"]:
            payload["DHCPv4"] = {"DHCPEnabled": params["dhcp_enabled"]}

    if params["ipv4_addresses"] is not None:
        changed = True
        if len(current_config["IPv4StaticAddresses"]) == len(params["ipv4_addresses"]):
            if all(
                {
                    "Address": conf["address"],
                    "AddressOrigin": "Static",
                    "Gateway": conf["gateway"],
                    "SubnetMask": conf["subnet_mask"],
                } in current_config["IPv4StaticAddresses"] for conf in params["ipv4_addresses"]
            ):
                changed = False
        if changed:
            payload["IPv4StaticAddresses"] = []
            for conf in params["ipv4_addresses"]:
                payload["IPv4StaticAddresses"].append({
                    "Address": conf["address"],
                    "Gateway": conf["gateway"],
                    "SubnetMask": conf["subnet_mask"],
                })

    if params["static_nameservers"] is not None:
        changed = True
        if len(current_config["StaticNameServers"]) == len(params["static_nameservers"]):
            if all(ns in current_config["StaticNameServers"] for ns in params["static_nameservers"]):
                changed = False
        if changed:
            payload["StaticNameServers"] = params["static_nameservers"]

    if payload:
        if not module.check_mode:
            client.update_ethernet_interface(params["name"], payload)
        module.exit_json(msg="Interface configuration updated.", changed=True)
    else:
        module.exit_json(msg="No changes required.", changed=False)


def main():
    module = AnsibleModule(
        argument_spec={
            "connection": {
                "required": True,
                "type": "dict",
                "options": {
                    "hostname": {"required": True, "type": "str"},
                    "username": {"required": True, "type": "str"},
                    "password": {"required": True, "type": "str", "no_log": True},
                    "port": {"required": False, "type": "int", "default": 443},
                    "validate_certs": {"required": False, "type": "bool", "default": True},
                    "timeout": {"required": False, "type": "int", "default": 10},
                }
            },
            "name": {"type": "str", "required": True},
            "dhcp_enabled": {"type": "bool", "required": False},
            "ipv4_addresses": {"type": "list", "required": False, "elements": "dict"},
            "static_nameservers": {"type": "list", "required": False, "elements": "str"}
        },
        supports_check_mode=True
    )

    try:
        run_module(module)
    except HTTPError as e:
        module.fail_json(msg="Request finished with error.", error_info=json.load(e))
    except (URLError, SSLValidationError, ConnectionError) as e:
        module.fail_json(msg="Can't connect to server.", error_info=str(e))


if __name__ == "__main__":
    main()
