# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.0.0
# Copyright (c) 2021 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

try:
    from typing import Optional, ClassVar, List
except ImportError:
    # Satisfy Python 2 which doesn't have typing.
    Optional = ClassVar = List = None

from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.base import RedfishAPIObject
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.exceptions import RedfishFieldNotFoundError


class VirtualMedia(RedfishAPIObject):

    @classmethod
    def select_version(cls, version):  # type: (str) -> Optional[ClassVar[VirtualMedia_v1_3_0]]
        if version == "#VirtualMedia.v1_3_0.VirtualMedia":
            return VirtualMedia_v1_3_0

    def insert(
        self,
        image_path,  # type: str
        media_type='USBStick',  # type: str
        username=None,  # type: str
        password=None,  # type: str
        transfer_method='Stream',  # type: str
        write_protected=True,  # type: bool
        inserted=True,  # type: bool
    ):  # type: (...) -> None
        raise NotImplementedError("Method not implemented")


class VirtualMedia_v1_3_0(VirtualMedia):

    def insert(
        self,
        image_path,  # type: str
        media_type='USBStick',  # type: str
        username=None,  # type: str
        password=None,  # type: str
        transfer_method='Stream',  # type: str
        write_protected=True,  # type: bool
        inserted=True,  # type: bool
    ):  # type: (...) -> None

        self._client.post(
            self._path + '/Actions/VirtualMedia.InsertMedia',
            body={
                'Image': image_path,
                'MediaType': media_type,
                'UserName': username or '',
                'Password': password or '',
                'TransferMethod': transfer_method,
                'WriteProtected': write_protected,
                'Inserted': inserted,
            }
        )