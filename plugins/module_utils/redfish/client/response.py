# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

try:
    from typing import Dict
except ImportError:
    # Satisfy Python 2 which doesn't have typing.
    Dict = None

import json
from ansible.module_utils.six.moves.http_client import HTTPResponse


class HTTPClientResponse:

    def __init__(self, response):  # type: (HTTPResponse) -> None
        self.body = None
        self._response = response
        if self._response:
            self.body = self._response.read()

    @property
    def json(self):  # type: () -> Dict
        try:
            return json.loads(self.body)
        except ValueError:
            raise ValueError("Unable to parse json")

    @property
    def headers(self):  # type: () -> Dict
        return dict(self._response.headers)

    @property
    def status_code(self):  # type: () -> int
        return self._response.getcode()

    @property
    def is_success(self):  # type: () -> bool
        return self.status_code in (200, 201, 202, 204)
