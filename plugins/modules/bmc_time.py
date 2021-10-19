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
module: bmc_time
short_description: Module for configure OpenBmc time.
version_added: "1.0.0"
description: Configures NTP servers.
extends_documentation_fragment:
  - yadro.obmc.connection_options
author: "Radmir Safin (@radmirsafin)"
options:
  ntp_enabled:
    required: false
    type: bool
    description: Indicates if NTP protocol is enabled or disabled.
  ntp_servers:
    required: false
    type: list
    description:
      - List of NTP servers IP. Supported up to 3 NTP servers.
      - If empty list is set, all servers configuration will be removed.
    elements: str
"""

RETURN = r"""
---
msg:
  type: str
  returned: always
  description: Operation status message.
  sample: Account created.
error_info:
  type: str
  returned: on error
  description: Error details.
"""

EXAMPLES = r"""
---
- name: Configure NTP servers
  yadro.obmc.bmc_time:
    connection:
      hostname: "{{ server }}"
      username: "{{ username }}"
      password: "{{ password }}"
    ntp_enabled: true
    ntp_servers:
      - 192.168.1.100
      - 192.168.2.100

- name: Change NTP servers
  yadro.obmc.bmc_time:
    connection:
      hostname: "{{ server }}"
      username: "{{ username }}"
      password: "{{ password }}"
    ntp_enabled: true
    ntp_servers:
      - 192.168.3.100

- name: Remove NTP servers
  yadro.obmc.bmc_time:
    connection:
      hostname: "{{ server }}"
      username: "{{ username }}"
      password: "{{ password }}"
    ntp_enabled: true
    ntp_servers: []

- name: Disable NTP support
  yadro.obmc.bmc_time:
    connection:
      hostname: "{{ server }}"
      username: "{{ username }}"
      password: "{{ password }}"
    ntp_enabled: false
"""

import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import ConnectionError, SSLValidationError
from ansible.module_utils.six.moves.urllib.error import URLError, HTTPError
from ansible_collections.yadro.obmc.plugins.module_utils.client.client import create_client


def run_module(module):
    params = module.params
    if params["ntp_servers"] and len(params["ntp_servers"]) > 3:
        module.fail_json(
            msg="Can't configure NTP servers.",
            error_info="Supported no more than 3 NTP servers.".format(k),
            changed=False
        )

    client = create_client(**params["connection"])
    managers = client.get_manager_collection()
    if len(managers) != 1:
        module.fail_json(
            msg="Can't identify BMC manager.",
            error_info="Operations with only one BMC manager supported. Found: {0}".format(len(managers))
        )
    bmc_manager = managers[0]
    network_protocols = client.get_network_protocol(bmc_manager)

    changed = False
    payload = {"NTP": {}}
    if params["ntp_enabled"] is not None and params["ntp_enabled"] != network_protocols["NTP"]["ProtocolEnabled"]:
        changed = True
        payload["NTP"]["ProtocolEnabled"] = params["ntp_enabled"]
    if params["ntp_servers"] is not None and params["ntp_servers"] != network_protocols["NTP"]["NTPServers"]:
        changed = True
        payload["NTP"]["NTPServers"] = params["ntp_servers"]

    if changed:
        if not module.check_mode:
            client.update_network_protocol(bmc_manager, payload)
        module.exit_json(msg="Configuration updated.", changed=changed)
    else:
        module.exit_json(msg="No changes required.", changed=changed)


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
                }
            },
            "ntp_enabled": {"type": "bool", "required": False},
            "ntp_servers": {"type": "list", "required": False, "elements": "str"},
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
