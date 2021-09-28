# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

from ansible.module_utils.urls import open_url, ConnectionError, SSLValidationError
from ansible.module_utils.six.moves.urllib.error import URLError, HTTPError
from ansible.module_utils.six.moves.urllib.parse import urlencode


def build_url(base, path, query_params=None):
    url = "{0}/{1}".format(base.rstrip("/"), path.lstrip("/"))
    if query_params:
        url += "?" + urlencode(query_params)
    return url


class RestClientError(Exception):
    pass


class RestClientResponse:

    def __init__(self, response):
        self.http_response = response
        if self.http_response:
            self.body = self.http_response.read()

    @property
    def json_data(self):
        try:
            return json.loads(self.body)
        except ValueError:
            raise ValueError("Unable to parse json")

    @property
    def status_code(self):
        return self.http_response.getcode()

    @property
    def is_success(self):
        return self.status_code in [200, 201, 202, 204]


class RestClient:

    def __init__(self, hostname, base_prefix="/redfish/v1/", username=None, password=None,
                 validate_certs=True, timeout=10):

        self._protocol = "https"
        self._port = 443
        if "://" in hostname:
            raise RestClientError("Hostname must not contain protocol definition.")

        self._base_prefix = base_prefix
        self._base_url = build_url(
            "{0}://{1}:{2}".format(self._protocol, hostname, self._port),
            self._base_prefix
        )

        self._username = username
        self._password = password
        self.validate_certs = validate_certs
        self.timeout = timeout

    def _get_reqeust_params(self, method, headers=None):
        request_headers = {}
        if headers:
            request_headers.update(headers)

        request_params = {
            "method": method,
            "validate_certs": self.validate_certs,
            "use_proxy": True,
            "timeout": self.timeout,
            "follow_redirects": "all",
            "headers": request_headers
        }

        if "X-Auth-Token" in request_headers:
            request_params["force_basic_auth"] = False
        else:
            request_params["force_basic_auth"] = True
            request_params["url_username"] = self._username
            request_params["url_password"] = self._password

        return request_params

    def _make_request(self, path, method, query_params=None, body=None, headers=None):
        if not headers:
            headers = {}

        url = build_url(self._base_url, path, query_params=query_params)
        if body:
            if isinstance(body, dict) or isinstance(body, list):
                headers["Content-Type"] = "application/json"
                request_body = json.dumps(body)
            elif isinstance(body, bytes):
                headers["Content-Type"] = "application/octet-stream"
                request_body = body
            else:
                raise RestClientError("{0} type currently unsupported".format(type(body)))
        else:
            request_body = None

        request_params = self._get_reqeust_params(method, headers)
        response = open_url(url=url, data=request_body, **request_params)
        return RestClientResponse(response)

    def get(self, path, query_params=None, headers=None):
        return self._make_request(path, method="GET", query_params=query_params, headers=headers)

    def post(self, path, body=None, headers=None):
        return self._make_request(path, method="POST", body=body, headers=headers)
