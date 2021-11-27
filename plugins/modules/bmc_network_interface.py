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
  - Updates properties in Ethernet interface resource for a BMC.
  - This module supports check mode.
author: "Radmir Safin (@radmirsafin)"
extends_documentation_fragment:
  - yadro.obmc.connection_options
options:
  name:
    required: True
    type: str
    description: The identifier of the Ethernet interface.
  dhcp_enabled:
    type: bool
    description:
      - An indication of whether DHCPv4 is enabled on this Ethernet interface.
      - Cannot be set to C(true) together I(ipv4_addresses) option.
      - If DHCP is enabled, static network configuration will be lost.
  ipv4_addresses:
    type: list
    elements: dict
    description:
      - The IPv4 static addresses assigned to this interface.
      - Only one IP address currently supported (will be fixed in future releases).
      - Cannot be configured if I(dhcp_enabled) is C(true).
      - If static configuration is present, DHCP will be disabled.
      - Each IP address record it is dictionary which must contains
        I(gateway), I(address) and I(subnet_mask) keys.
      - For more details look to examples.
  static_nameservers:
    type: list
    elements: str
    description: List of static DNS server names.
"""

RETURN = r"""
---
msg:
  type: str
  returned: always
  description: Operation status message.
error:
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


from functools import partial
from ansible_collections.yadro.obmc.plugins.module_utils.obmc_module import OpenBmcModule


class OpenBmcNetworkInterfaceModule(OpenBmcModule):

    def __init__(self):
        argument_spec = {
            "name": {"type": "str", "required": True},
            "dhcp_enabled": {"type": "bool", "required": False},
            "ipv4_addresses": {"type": "list", "required": False, "elements": "dict"},
            "static_nameservers": {"type": "list", "required": False, "elements": "str"}
        }
        super(OpenBmcNetworkInterfaceModule, self).__init__(
            argument_spec=argument_spec,
            supports_check_mode=True
        )

    def _run(self):
        changes = []

        if self.params["dhcp_enabled"] and self.params["ipv4_addresses"]:
            self.fail_json(
                msg="Cannot configure network interface.",
                error="Conflict between static configuration and DHCP.",
                changed=False,
            )

        if self.params["ipv4_addresses"] and len(self.params["ipv4_addresses"]) > 1:
            self.fail_json(
                msg="Cannot configure network interface.",
                error="Only one IP address supported.",
                changed=False,
            )

        interface = self.redfish.get_manager("bmc").get_ethernet_interface(self.params["name"])
        if interface is None:
            self.fail_json(
                msg="Cannot configure network interface.",
                error="Interface {0} not found.".format(self.params["name"]),
                changed=False
            )

        if self.params["dhcp_enabled"] is not None:
            if interface.get_dhcpv4_enabled() != self.params["dhcp_enabled"]:
                changes.append(partial(
                    interface.set_dhcpv4_enabled,
                    self.params["dhcp_enabled"],
                ))

        ip_addresses = interface.get_static_ipv4_addresses()
        if self.params["ipv4_addresses"] is not None:
            ip_changed = True
            if len(ip_addresses) == len(self.params["ipv4_addresses"]):
                if all(
                        {
                            "Address": conf["address"],
                            "AddressOrigin": "Static",
                            "Gateway": conf["gateway"],
                            "SubnetMask": conf["subnet_mask"],
                        } in ip_addresses for conf in self.params["ipv4_addresses"]
                ):
                    ip_changed = False
            if ip_changed:
                payload = []
                for conf in self.params["ipv4_addresses"]:
                    payload.append({
                        "Address": conf["address"],
                        "Gateway": conf["gateway"],
                        "SubnetMask": conf["subnet_mask"],
                    })
                changes.append(partial(
                    interface.set_ipv4_addresses,
                    payload,
                ))

        static_nameservers = interface.get_static_nameservers()
        if self.params["static_nameservers"] is not None:
            nameservers_changed = True
            if len(static_nameservers) == len(self.params["static_nameservers"]):
                if all(ns in static_nameservers for ns in self.params["static_nameservers"]):
                    nameservers_changed = False
            if nameservers_changed:
                changes.append(partial(
                    interface.set_static_nameservers,
                    self.params["static_nameservers"],
                ))

        if changes:
            if not self.check_mode:
                for action in changes:
                    action()
            self.exit_json(msg="Operation successful.", changed=True)
        else:
            self.exit_json(msg="No changes required.", changed=False)


def main():
    OpenBmcNetworkInterfaceModule().run()


if __name__ == "__main__":
    main()
