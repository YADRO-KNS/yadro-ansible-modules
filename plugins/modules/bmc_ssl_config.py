#!/usr/bin/python
# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2022 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = r"""
---
module: bmc_ssl_config
short_description: Configuring BMC certificates
version_added: "1.1.0"
description:
  - Addition/replacing HTTPS, LDAP, CA certificates.
  - Deletion CA certificate.
  - Supports check mode.
author: "Sergey Kovalev (@kvlvs)"
extends_documentation_fragment:
  - yadro.obmc.connection_options
options:
  crt_type:
    required: True
    type: str
    choices: [https, ldap, ca]
    description: Type of certificate
  crt_path:
    type: str
    description:
      - Path to the certificate's file
      - Option required if state is present and crt_content is not passed
  crt_content:
    type: str
    description:
      - Content of certificate, which is desired to be added at BMC
      - Option required if state is present and crt_path is not passed
  crt_format:
    required: False
    type: str
    default: PEM
    description: Certificate's format
  state:
    required: False
    type: str
    choices: [present, absent]
    default: present
    description:
      - Defines should certificate exist or not.
      - Works only with CA certificate.
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
- name: HTTPS certificate setup
  yadro.obmc.bmc_ssl_config:
    connection:
      hostname: "{{ server }}"
      username: "{{ username }}"
      password: "{{ password }}"
    crt_type: https
    crt_path: /tmp/https.crt
"""

from functools import partial
from ansible_collections.yadro.obmc.plugins.module_utils.obmc_module import OpenBmcModule


class OpenBmcSslConfigModule(OpenBmcModule):

    def __init__(self):
        argument_spec = {
            'crt_type': {
                'type': 'str',
                'required': True,
                'choices': ['https', 'ldap', 'ca'],
            },
            'crt_path': {'type': 'str', 'required': False},
            'crt_content': {'type': 'str', 'required': False},
            'crt_format': {'type': 'str', 'required': False, 'default': 'PEM'},
            'state': {
                'type': 'str',
                'required': False,
                'default': 'present',
                'choices': ['present', 'absent'],
            },
        }

        super(OpenBmcSslConfigModule, self).__init__(
            argument_spec=argument_spec,
            supports_check_mode=True,
            required_if=[
                ['state', 'present', ['crt_path', 'crt_content'], True],
            ],
        )

    def _add_new_certificate(self, crt_service, new_crt_content):
        if self.params['crt_type'] == 'https':
            crt_service.add_https_certificate(new_crt_content)
        elif self.params['crt_type'] == 'ldap':
            crt_service.add_ldap_certificate(new_crt_content)
        elif self.params['crt_type'] == 'ca':
            crt_service.add_ca_certificate(new_crt_content)
        else:
            self.fail_json(
                msg='Method not found',
                error='Method not found for crt_type: {0}'.format(
                    str(self.params['crt_type'])
                ),
                changed=False,
            )

    def _get_certificate(self, crt_service):
        if self.params['crt_type'] == 'https':
            crt = crt_service.get_https_certificate()
        elif self.params['crt_type'] == 'ldap':
            crt = crt_service.get_ldap_certificate()
        elif self.params['crt_type'] == 'ca':
            crt = crt_service.get_ca_certificate()
        else:
            crt = None

        return crt

    def _get_crt_content(self):
        if self.params['crt_path']:
            with open(self.params['crt_path'], encoding='utf-8') as f:
                crt_content = f.read()
            return crt_content
        elif self.params['crt_content']:
            return self.params['crt_content']

        self.fail_json(
            msg='Please provide valid crt_path or crt_content options',
            error='Could not find certificate content',
            changed=False,
        )

    def _run(self):
        if self.params['state'] == 'absent' and self.params['crt_type'] != 'ca':
            self.fail_json(
                msg='State absent is allowed only for ca certificates',
                error='Wrong state for certificate',
                changed=False,
            )

        crt_service = self.redfish.get_certificate_service()
        crt = self._get_certificate(crt_service)

        action = None
        if self.params['state'] == 'present':
            new_crt_content = self._get_crt_content()

            if crt is not None:
                action = partial(
                    crt_service.replace_certificate,
                    crt,
                    new_crt_content,
                    self.params['crt_format'],
                )
            else:
                action = partial(
                    self._add_new_certificate,
                    crt_service,
                    new_crt_content,
                )

        if self.params['state'] == 'absent' and crt is not None:
            action = crt.delete

        if action:
            if not self.check_mode:
                action()
            self.exit_json(msg="Operation successful.", changed=True)
        else:
            self.exit_json(msg="No changes required.", changed=False)


def main():
    OpenBmcSslConfigModule().run()


if __name__ == "__main__":
    main()
