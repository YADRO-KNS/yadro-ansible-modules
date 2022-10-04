# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.1.0
# Copyright (c) 2022 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

try:
    from typing import Optional, ClassVar
except ImportError:
    # Satisfy Python 2 which doesn't have typing.
    Optional = ClassVar = None

from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.base \
    import RedfishAPIObject


class Certificate(RedfishAPIObject):

    @classmethod
    def select_version(cls, version):  # type: (str) -> Optional[ClassVar[Certificate_v1_0_0]]
        if version == "#Certificate.v1_0_0.Certificate":
            return Certificate_v1_0_0

    def delete(self):
        raise NotImplementedError('Method not implemented')


class Certificate_v1_0_0(Certificate):

    def __init__(self, client, path, data):
        super(Certificate_v1_0_0, self).__init__(client, path, data)

        self.location, self.id = self._data['@odata.id'].rsplit('/', 1)
        self.content = self._data['CertificateString']
        self.issuer = self._data['Issuer']
        self.key_usage = self._data['KeyUsage']
        self.name = self._data['Name']
        self.subject = self._data['Subject']
        self.valid_not_after = self._data['ValidNotAfter']
        self.valid_not_before = self._data['ValidNotBefore']

    def delete(self):
        self._client.delete(self._path)
