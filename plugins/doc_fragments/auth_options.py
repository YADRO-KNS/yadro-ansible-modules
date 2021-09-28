# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    DOCUMENTATION = r'''
    options:
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
        description: OpenBmc REST API port.
        default: 443
      verify_certs:
        type: bool
        description: Responsible for SSL certificates verification. If set to False certificates won't verified.
        default: True
'''
