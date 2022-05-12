# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.yadro.obmc.plugins.module_utils.redfish.exceptions import RedfishError


class HTTPClientError(RedfishError):
    pass


class RESTClientUnauthorized(RedfishError):
    pass


class RESTClientRequestError(RedfishError):
    pass


class RESTClientNotFoundError(RedfishError):
    pass


class RESTClientConnectionError(RedfishError):
    pass
