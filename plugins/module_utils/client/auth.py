# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class Auth:
    pass


class BasicAuth(Auth):

    def __init__(self, username, password):
        self.username = username
        self.password = password


class SessionAuth(Auth):

    def __init__(self, token):
        self.token = token


class AuthError(Exception):
    pass
