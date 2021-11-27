# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    DOCUMENTATION = r"""
    options:
      connection:
        required: True
        type: dict
        description:
          - I(connection) describes OpenBmc connection configuration. Two authentication methods
          - available (username and password or session_key). Session key can be received using
          - bmc_session module. One of authentication methods must be used.
        suboptions:
          hostname:
            required: True
            type: str
            description: BMC server IP address or hostname.
          username:
            type: str
            description: BMC username to login.
          password:
            type: str
            description: BMC user password.
          session_key:
            type: str
            description: BMC session key.
          port:
            type: int
            default: 443
            description: BMC REST API port.
          validate_certs:
            type: bool
            default: True
            description:
              - Responsible for SSL certificates validation.
              - If set to False certificates won't validated.
          timeout:
            type: int
            default: 30
            description: BMC REST API request timeout.
"""
