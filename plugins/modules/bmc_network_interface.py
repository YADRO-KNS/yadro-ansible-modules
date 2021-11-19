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
short_description: Manage BMC network interfaces.
version_added: "1.0.0"
description:
  - Configures IP address at specific ethernet device.
  - Enables and disables address resolution via DHCP.
  - Configures interface namespace servers.
  - This module supports check mode.
author: "Radmir Safin (@radmirsafin)"
extends_documentation_fragment:
  - yadro.obmc.connection_options
options:
  name:
    required: True
    type: str
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
      - Only one IP address currently supported (will be fixed in future releases).
      - List of IP addresses to set at interface.
      - Cannot be configured if I(dhcp_enabled) is C(true).
      - If static configuration is present, DHCP will be disabled.
      - Each IP address record it is dictionary which must contains
        I(gateway), I(address) and I(subnet_mask) keys.
      - For more details look to examples.
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
  description: Error details if raised.
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


from ansible_collections.yadro.obmc.plugins.module_utils.obmc_module import OpenBmcModule


class OpenBmcNetworkInterfaceModule(OpenBmcModule):

    def __init__(self):
        argument_spec = {
            "name": {"type": "str", "required": True},
            "dhcp_enabled": {"type": "bool", "required": False},
            "ipv4_addresses": {"type": "list", "required": False, "elements": "dict"},
            "static_nameservers": {"type": "list", "required": False, "elements": "str"}
        }
        super(OpenBmcNetworkInterfaceModule, self).__init__(argument_spec=argument_spec, supports_check_mode=True)

    def _run(self):
        payload = {}

        if self.params["dhcp_enabled"] and self.params["ipv4_addresses"]:
            self.fail_json(
                msg="Cannot configure network interface.",
                error_info="Conflict between static configuration and DHCP.",
                changed=False,
            )

        if self.params["ipv4_addresses"] and len(self.params["ipv4_addresses"]) > 1:
            self.fail_json(
                msg="Cannot configure network interface.",
                error_info="Only one IP address supported. Please, remove extra configuration.",
                changed=False,
            )

        interfaces = self.client.get_ethernet_interface_collection()
        if self.params["name"] not in interfaces:
            self.fail_json(
                msg="Cannot configure network interface.",
                error_info="Interface {0} not found.".format(self.params["name"]),
                changed=False
            )

        current_config = self.client.get_ethernet_interface(self.params["name"])

        if self.params["dhcp_enabled"] is not None:
            if current_config["DHCPv4"]["DHCPEnabled"] != self.params["dhcp_enabled"]:
                payload["DHCPv4"] = {"DHCPEnabled": self.params["dhcp_enabled"]}

        if self.params["ipv4_addresses"] is not None:
            changed = True
            if len(current_config["IPv4StaticAddresses"]) == len(self.params["ipv4_addresses"]):
                if all(
                        {
                            "Address": conf["address"],
                            "AddressOrigin": "Static",
                            "Gateway": conf["gateway"],
                            "SubnetMask": conf["subnet_mask"],
                        } in current_config["IPv4StaticAddresses"] for conf in self.params["ipv4_addresses"]
                ):
                    changed = False
            if changed:
                payload["IPv4StaticAddresses"] = []
                for conf in self.params["ipv4_addresses"]:
                    payload["IPv4StaticAddresses"].append({
                        "Address": conf["address"],
                        "Gateway": conf["gateway"],
                        "SubnetMask": conf["subnet_mask"],
                    })

        if self.params["static_nameservers"] is not None:
            changed = True
            if len(current_config["StaticNameServers"]) == len(self.params["static_nameservers"]):
                if all(ns in current_config["StaticNameServers"] for ns in self.params["static_nameservers"]):
                    changed = False
            if changed:
                payload["StaticNameServers"] = self.params["static_nameservers"]

        if payload:
            if not self.check_mode:
                self.client.update_ethernet_interface(self.params["name"], payload)
            self.exit_json(msg="Interface configuration updated.", changed=True)
        else:
            self.exit_json(msg="No changes required.", changed=False)


def main():
    OpenBmcNetworkInterfaceModule().run()


if __name__ == "__main__":
    main()
