# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class AuthMethod:
    pass


class NoAuth(AuthMethod):
    pass


class BasicAuth(AuthMethod):

    def __init__(self, username, password):  # type: (str, str) -> None
        self.username = username
        self.password = password


class SessionAuth(AuthMethod):

    def __init__(self, token):  # type: (str) -> None
        self.token = token
