#!/usr/bin/python
# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.1.0
# Copyright (c) 2022 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = r"""
---
module: bmc_ldap_config
short_description: Configures LDAP authentication
version_added: "1.1.0"
description:
  - This module is responsible for external account providers configuration
  - Supports check mode.
  - Supports ldap:// and ldaps:// protocols
  - Supports OpenLDAP and Active Directory
author: "Sergey Kovalev (@kvlvs)"
extends_documentation_fragment:
  - yadro.obmc.connection_options
options:
  service_type:
    required: True
    type: str
    choices: [OpenLDAP, ActiveDirectory]
    description: Defines the LDAP service
  uri:
    required: False
    type: str
    description:
      - The address of the external LDAP service
      - Should start with ldap:// or ldaps://
  enabled:
    required: False
    type: bool
    description: An indication of whether this service is enabled
  bind_dn:
    required: False
    type: str
    description:
      - DN of the user who will interact with the LDAP service
  password:
    required: False
    type: str
    description:
      - Password of the user who will interact with the LDAP service
      - If I(password) is passed, module result is always changed=True
  base_dn:
    required: False
    type: str
    description:
      - The base distinguished names to use to search an external LDAP service
  user_id_attribute:
    required: False
    type: str
    description:
      - The attribute name that contains the LDAP user name entry
  group_id_attribute:
    required: False
    type: str
    description:
      - The attribute name that contains the groups for a user on the LDAP user entry.
  role_groups:
    required: False
    type: list
    elements: dict
    description:
      - The mapping rules to convert the external account providers account
        information to the local role.
      - If this option is defined, previous role groups settings will be erased
      - By default users who logged in throughout external provider account have ReadOnly rights
    suboptions:
      name:
        required: True
        type: str
        description:
          - The name of the remote group that maps to the local role to which this entity links
      role:
        required: False
        type: str
        choices: [Administrator, Operator, ReadOnly]
        description:
         - The name of the local role to which to map the remote user or group
         - Required when I(state=present)
      state:
        required: False
        type: str
        choices: [present, absent]
        default: present
        description:
          - C(present) creates role group if it does not exist or updates existing
          - C(absent) removes existing role group
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
ldap_config:
  type: dict
  returned: on success
  description: Actual ldap configuration
  sample: {
    "service_type": "OpenLDAP",
    "uri": "ldap://192.168.100.101",
    "enabled": True,
    "bind_dn": "cn=admin,dc=example,dc=com",
    "password": None,
    "base_dn": "dc=example,dc=com",
    "role_groups": [
        {
          "name": "test_group",
          "role": "Administrator"
        }
    ]
  }
"""

EXAMPLES = r"""
---
- name: Enable LDAP authentication
  yadro.obmc.bmc_ldap_config:
    connection:
      hostname: "localhost"
      username: "username"
      password: "password"
    service_type: "OpenLDAP"
    uri: "ldap://192.168.100.101"
    enabled: true
    bind_dn: "cn=lookup,dc=example,dc=com"
    password: "password"
    base_dn: "dc=example,dc=com"
    role_groups:
      - name: test_group
        role: Administrator
        state: present

- name: Disable LDAP authentication
  yadro.obmc.bmc_ldap_config:
    connection:
      hostname: "localhost"
      username: "username"
      password: "password"
    service_type: "OpenLDAP"
    enabled: false

- name: Remove role group
  yadro.obmc.bmc_ldap_config:
    connection:
      hostname: "localhost"
      username: "username"
      password: "password"
    service_type: "OpenLDAP"
    role_groups:
      - name: test_group
        state: absent
"""


from ansible_collections.yadro.obmc.plugins.module_utils.obmc_module import OpenBmcModule
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.enums import AccountProvider


class OpenBmcLdapConfigModule(OpenBmcModule):

    def __init__(self):
        argument_spec = {
            'service_type': {
                'required': True,
                'type': 'str',
                'choices': ['OpenLDAP', 'ActiveDirectory'],
            },
            'uri': {'required': False, 'type': 'str'},
            'enabled': {'required': False, 'type': 'bool'},
            'bind_dn': {'required': False, 'type': 'str'},
            'password': {'required': False, 'type': 'str', 'no_log': True},
            'base_dn': {'required': False, 'type': 'str'},
            'user_id_attribute': {'required': False, 'type': 'str'},
            'group_id_attribute': {'required': False, 'type': 'str'},
            'role_groups': {
                'required': False,
                'type': 'list',
                'elements': 'dict',
                'options': {
                    'name': {'type': 'str', 'required': True},
                    'role': {
                        'type': 'str',
                        'required': False,
                        'choices': ['Administrator', 'Operator', 'ReadOnly']},
                    'state': {
                        'type': 'str',
                        'required': False,
                        'choices': ['present', 'absent'],
                        'default': 'present',
                    }
                }
            }
        }
        super(OpenBmcLdapConfigModule, self).__init__(
            argument_spec=argument_spec,
            supports_check_mode=True,
        )

        # We should extra validate role groups because it has
        # second-level options which are not supported by required_if
        self._validate_role_groups()

    def _run(self):
        service_type = self._define_service_type()
        account_service = self.redfish.get_account_service()
        actual_config = account_service.get_ldap_config(service_type)

        # Send only defined parameters
        prepared_data = dict(
            (k, v) for k, v in self.params.items()
            if v is not None and k in actual_config
        )

        if 'role_groups' in prepared_data:
            existing_groups = actual_config['role_groups']
            groups_update = self._get_groups_update(existing_groups)
            # If processed groups are equal to existing,
            # no group changes are needed
            if groups_update == existing_groups:
                prepared_data.pop('role_groups')
            else:
                prepared_data['role_groups'] = groups_update

        groups_change = 'role_groups' in prepared_data
        password_passed = 'password' in prepared_data

        need_changes = groups_change or password_passed or any(
            new_val != actual_config[k]
            for k, new_val in prepared_data.items()
        )

        if need_changes:
            result = dict(msg="Operation successful.", changed=True)
            if not self.check_mode:
                actual_config = account_service.config_ldap(
                    service_type=service_type,
                    **prepared_data
                )
                result['ldap_config'] = actual_config
            self.exit_json(**result)
        else:
            self.exit_json(
                msg="No changes required.",
                ldap_config=actual_config,
                changed=False)

    def _define_service_type(self):
        if self.params['service_type'] == 'OpenLDAP':
            return AccountProvider.OPENLDAP

        if self.params['service_type'] == 'ActiveDirectory':
            return AccountProvider.ACTIVE_DIRECTORY

        self.fail_json(
            msg='Unsupported service type',
            error='service_type value error',
            changed=False,
        )

    def _get_groups_update(self, existing_groups):
        rv = existing_groups.copy()
        desired_groups = self.params['role_groups']

        for desired in desired_groups:
            group_found = False
            for i, group in enumerate(existing_groups):
                group_found = group['name'] == desired['name']

                if group_found and desired['state'] == 'absent':
                    rv[i] = None
                elif group_found and desired['state'] == 'present' \
                        and group['role'] != desired['role']:
                    new_data = rv[i].copy()
                    new_data['role'] = desired['role']
                    rv[i] = new_data

                if group_found:
                    break

            if not group_found and desired['state'] == 'present':
                rv.append(
                    dict(name=desired['name'], role=desired['role'])
                )

        return rv

    def _validate_role_groups(self):
        if self.params['role_groups'] is None:
            return

        for group in self.params['role_groups']:
            present = group['state'] == 'present'
            no_role = group['role'] is None
            if present and no_role:
                self.fail_json(
                    error='Missing required arguments',
                    msg='state is present but role suboption '
                        'is missing in role_groups option',
                    changed=False)


def main():
    OpenBmcLdapConfigModule().run()


if __name__ == "__main__":
    main()
