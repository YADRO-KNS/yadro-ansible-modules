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
        description: I(connection) option describes OpenBmc connection details.
        suboptions:
          hostname:
            required: True
            type: str
            description: OpenBmc server IP address or hostname.
          username:
            required: True
            type: str
            description: OpenBmc username to login.
          password:
            required: True
            type: str
            description: OpenBmc user password.
          port:
            type: int
            default: 443
            description: OpenBmc REST API port.
          validate_certs:
            type: bool
            default: True
            description:
              - Responsible for SSL certificates validation.
              - If set to False certificates won't validated.
          timeout:
            type: int
            default: 10
            description: API request timeout.
"""
