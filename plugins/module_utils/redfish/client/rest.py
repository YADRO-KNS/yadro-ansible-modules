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
from ansible.module_utils.urls import ConnectionError, SSLValidationError
from ansible.module_utils.six.moves.urllib.error import URLError, HTTPError
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.client.http import HTTPClient, HTTPClientResponse
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.client.exceptions import (
    RESTClientRequestError,
    RESTClientNotFoundError,
    RESTClientConnectionError,
)


class RESTClient(HTTPClient):

    def __init__(self, *args, **kwargs):
        super(RESTClient, self).__init__(*args, **kwargs)

    def make_request(self, path, method, query_params=None, body=None, headers=None):
        # type: (str, str, Dict, Dict, Dict) -> HTTPClientResponse
        try:
            response = self._make_request(path, method, query_params, body, headers)
        except HTTPError as e:
            if e.code == 404:
                raise RESTClientNotFoundError("Not found: {0}".format(e.url))
            else:
                raise RESTClientRequestError("Request finished with error: {0}".format(json.load(e)))
        except (URLError, SSLValidationError, ConnectionError) as e:
            raise RESTClientConnectionError("Cannot connect to server: {0}".format(str(e)))
        else:
            return response
