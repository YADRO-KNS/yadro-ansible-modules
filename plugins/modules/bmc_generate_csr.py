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
module: bmc_generate_csr
short_description: Generating Certificate Sign Request.
version_added: "1.1.0"
description:
  - Generates csr on bmc side for creating ssl certificate.
author: "Sergey Kovalev (@kvlvs)"
extends_documentation_fragment:
  - yadro.obmc.connection_options
options:
  path:
    required: False
    type: str
    description:
      - The local (control node) path where csr file will be created.
      - Target must be a file.
  crt_type:
    required: True
    type: str
    choices: [https, ldap]
    description: Type of certificate.
  country:
    required: True
    type: str
    description: 2-symbols country code.
  city:
    required: True
    type: str
    description: The city in which the organization is located.
  common_name:
    required: True
    type: str
    description: Domain name for server's lookups.
  state:
    required: True
    type: str
    description: The state in which the organization is located.
  organization:
    required: True
    type: str
    description: The organization name.
  organizational_unit:
    required: True
    type: str
    description: The organizational unit name.
  alternative_names:
    required: False
    type: list
    elements: str
    description: Alternative host names.
  key_usage:
    required: False
    type: list
    elements: str
    description: Purpose of the public key in the certificate.
  contact_person:
    required: False
    type: str
    description: User who makes the request.
  challenge_password:
    required: False
    type: str
    description: Password which is applied to the certificate for revocation requests.
  email:
    required: False
    type: str
    description: Email of user who makes the request.
  given_name:
    required: False
    type: str
    description: Name of user who makes the request.
  initials:
    required: False
    type: str
    description: Initials of user who makes the request.
  key_pair_algorithm:
    required: False
    type: str
    default: EC
    description: Type of key pair for signing algorithms.
  key_curve_id:
    required: False
    type: str
    default: secp384r1
    description: Key curve identifier.
  surname:
    required: False
    type: str
    description: Surname of user who makes the request.
  unstructured_name:
    required: False
    type: str
    description: Subject's unstructured name.
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
csr_content:
  type: str
  returned: on success
  description: Generated csr content.
"""

EXAMPLES = r"""
---
- name: Generating CSR
  yadro.obmc.bmc_generate_csr:
    connection:
      hostname: "{{ server }}"
      username: "{{ username }}"
      password: "{{ password }}"
    crt_type: https
    country: RU
    city: St. Petersburg
    common_name: testhost.com
    state: St. Petersburg
    organization: Yadro
    organizational_unit: Software Development
"""


import os
from ansible_collections.yadro.obmc.plugins.module_utils.obmc_module import OpenBmcModule


class OpenBmcGenerateCsrModule(OpenBmcModule):

    def __init__(self):
        argument_spec = {
            'path': {'type': 'str', 'required': False},
            'crt_type': {
                'type': 'str',
                'required': True,
                'choices': ['https', 'ldap'],
            },
            'country': {'type': 'str', 'required': True},
            'city': {'type': 'str', 'required': True},
            'common_name': {'type': 'str', 'required': True},
            'state': {'type': 'str', 'required': True},
            'organization': {'type': 'str', 'required': True},
            'organizational_unit': {'type': 'str', 'required': True},
            'alternative_names': {
                'type': 'list',
                'elements': 'str',
                'required': False,
            },
            'key_usage': {
                'type': 'list',
                'elements': 'str',
                'required': False,
            },
            'contact_person': {'type': 'str', 'required': False},
            'challenge_password': {'type': 'str', 'no_log': True, 'required': False},
            'email': {'type': 'str', 'required': False},
            'given_name': {'type': 'str', 'required': False},
            'initials': {'type': 'str', 'required': False},
            'key_pair_algorithm': {
                'type': 'str',
                'default': 'EC',
                'required': False,
            },
            'key_curve_id': {
                'type': 'str',
                'default': 'secp384r1',
                'required': False,
            },
            'surname': {'type': 'str', 'required': False},
            'unstructured_name': {'type': 'str', 'required': False},
        }

        super(OpenBmcGenerateCsrModule, self).__init__(
            argument_spec=argument_spec,
            supports_check_mode=True,
        )

    def _run(self):
        csr_path = self.params['path']
        if csr_path:
            self._check_csr_path(csr_path)

        crt_service = self.redfish.get_certificate_service()
        csr_content = crt_service.generate_csr(
            crt_type=self.params['crt_type'],
            country=self.params['country'],
            city=self.params['city'],
            common_name=self.params['common_name'],
            state=self.params['state'],
            organization=self.params['organization'],
            organizational_unit=self.params['organizational_unit'],
            alternative_names=self.params['alternative_names'],
            key_usage=self.params['key_usage'],
            contact_person=self.params['contact_person'] or '',
            challenge_password=self.params['challenge_password'] or '',
            email=self.params['email'] or '',
            given_name=self.params['given_name'] or '',
            initials=self.params['initials'] or '',
            key_pair_algorithm=self.params['key_pair_algorithm'],
            key_curve_id=self.params['key_curve_id'],
            surname=self.params['surname'] or '',
            unstructured_name=self.params['unstructured_name'] or '',
        )

        if csr_path:
            with open(csr_path, 'w') as f:
                f.write(csr_content)

        self.exit_json(
            msg="Operation successful.",
            csr_content=csr_content,
            changed=True,
        )

    def _check_csr_path(self, csr_path):
        _dir = os.path.dirname(csr_path)

        if not os.path.exists(_dir):
            self.fail_json(
                msg='Target directory not found',
                error='Directory %s does not exist' % _dir,
                changed=False,
            )

        if os.path.isdir(csr_path):
            self.fail_json(
                msg='Target file is a directory',
                error='%s is a directory. Please define a path to file' % csr_path,
                changed=False,
            )


def main():
    OpenBmcGenerateCsrModule().run()


if __name__ == "__main__":
    main()
