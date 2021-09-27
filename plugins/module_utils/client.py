# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Modules
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.six.moves.urllib.parse import urljoin
from ansible.module_utils.basic import missing_required_lib

try:
    import requests
    from requests.auth import HTTPBasicAuth
except ImportError:
    REQUESTS_FOUND = False
else:
    REQUESTS_FOUND = True


def join_urls(base, prefix):
    return urljoin(base.rstrip("/"), prefix.lstrip("/"))


class RestClient:

    def __init__(self, base_url, base_prefix="/redfish/v1/",
                 username=None, password=None,
                 verify_certs=True, timeout=10):

        if not REQUESTS_FOUND:
            raise ImportError(missing_required_lib("requests"))

        if "://" not in base_url:
            self._base_url = "https://{0}".format(base_url)
        else:
            self._base_url = base_url
        self._base_url = self._base_url

        self._base_prefix = base_prefix
        self._url = join_urls(self._base_url, self._base_prefix)
        self._auth = requests.auth.HTTPBasicAuth(username, password)

        self.verify_certs = verify_certs
        self.timeout = timeout

    def _rest_request(self, path, method="GET", args=None, body=None):
        request_args = {
            "url": join_urls(self._url, path),
            "auth": self._auth,
            "verify": self.verify_certs,
            "timeout": self.timeout,
        }
        if method == "GET":
            return requests.get(**request_args)

    def get(self, path, args=None):
        return self._rest_request(path, method="GET", args=args)
