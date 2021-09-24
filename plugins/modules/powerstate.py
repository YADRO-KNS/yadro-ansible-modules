#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# YADRO Ansible Modules
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = r'''
---
module: powerstate
short_description: Module short description.
version_added: "1.0.0"
description: Module full description.
options:
  hostname:
    description: Hostname description
    type: str
    required: True
  username:
    description: Username description
    type: str
    required: True
  password:
    description: Password description
    type: str
    required: True
  state:
    description: Desired end power state.
    type: str
    required: True
    choices: ['on', 'off']
requirements:
    - "python >= 2.7.5"
author: "Radmir Safin (@rsafin)"
notes:
    - Run this module from a system that has direct access to DellEMC OpenManage Enterprise.
    - This module supports C(check_mode).
'''

RETURN = r'''
---
job_status:
  type: dict
  description: "Power state operation job and progress details from the OME."
  returned: success
  sample: {}
'''

EXAMPLES = r'''
---
- name: Power state operation
  yadro.obmc.powerstate:
    hostname: "192.168.0.1"
    username: "username"
    password: "password"
    state:    "off"
'''


from ansible.module_utils.basic import AnsibleModule


def main():
    module = AnsibleModule(
        argument_spec={
            "hostname": {"required": True, "type": "str"},
            "username": {"required": True, "type": "str"},
            "password": {"required": True, "type": "str", "no_log": True},
            "state": {"required": True, "type": "str", "choices": ["on", "off"]},
        },
        supports_check_mode=False
    )
    module.exit_json(msg="Power State operation job submitted successfully.")


if __name__ == '__main__':
    main()
