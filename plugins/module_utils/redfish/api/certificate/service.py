# -*- coding: utf-8 -*-

# YADRO OpenBmc Ansible Collection
# Version 1.1.0
# Copyright (c) 2022 YADRO (KNS Group LLC)

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

try:
    from typing import Optional, ClassVar, List, Tuple
except ImportError:
    # Satisfy Python 2 which doesn't have typing.
    Optional = ClassVar = List = Tuple = None

from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.base import RedfishAPIObject
from ansible_collections.yadro.obmc.plugins.module_utils.redfish.api.certificate.certificate import Certificate


CERTIFICATE_LOCATIONS = {
    'CA': '/redfish/v1/Managers/bmc/Truststore/Certificates',
    'LDAP': '/redfish/v1/AccountService/LDAP/Certificates',
    'HTTPS': '/redfish/v1/Managers/bmc/NetworkProtocol/HTTPS/Certificates'
}


class CertificateService(RedfishAPIObject):

    @classmethod
    def select_version(cls, version):  # type: (str) -> Optional[ClassVar[CertificateService]]
        if version == "#CertificateService.v1_0_0.CertificateService":
            return CertificateService_v1_0_0
        elif version == "#CertificateService.v1_0_0.CertificateService.Mockup":
            return CertificateServiceMockup_v1_0_0

    def add_https_certificate(self, content):  # type: (str) -> Certificate
        raise NotImplementedError("Method not implemented")

    def add_ldap_certificate(self, content):  # type: (str) -> Certificate
        raise NotImplementedError("Method not implemented")

    def add_ca_certificate(self, content):  # type: (str) -> Certificate
        raise NotImplementedError("Method not implemented")

    def generate_csr(
        self,
        crt_type,  # type: str
        country,  # type: str
        city,  # type: str
        common_name,  # type: str
        state,  # type: str
        organization,  # type: str
        organizational_unit,  # type: str
        alternative_names=None,  # type: Optional[List[str]]
        key_usage=None,  # type: Optional[List[str]]
        contact_person='',  # type: Optional[str]
        challenge_password='',  # type: Optional[str]
        email='',  # type: Optional[str]
        given_name='',  # type: Optional[str]
        initials='',  # type: Optional[str]
        key_pair_algorithm='EC',  # type: Optional[str]
        key_curve_id='secp384r1',  # type: Optional[str]
        surname='',  # type: Optional[str]
        unstructured_name='',  # type: Optional[str]
        crt_location=None,  # type: Optional[str]
    ):  # type: (...) -> str
        raise NotImplementedError("Method not implemented")

    def get_all_certificates(self):  # type: () -> List[Certificate]
        raise NotImplementedError("Method not implemented")

    def get_https_certificate(self):  # type: () -> Certificate
        raise NotImplementedError("Method not implemented")

    def get_ldap_certificate(self):  # type: () -> Certificate
        raise NotImplementedError("Method not implemented")

    def get_ca_certificate(self):  # type: () -> Certificate
        raise NotImplementedError("Method not implemented")

    def replace_certificate(
        self,
        init_crt,  # type: Certificate
        new_crt_content,  # type: str
        crt_format='PEM',  # type: str
    ):  # type: (...) -> Certificate
        raise NotImplementedError("Method not implemented")

    @property
    def certificates(self):  # type: () -> List[Certificate]
        raise NotImplementedError("Method not implemented")


class CertificateService_v1_0_0(CertificateService):

    def add_https_certificate(self, content):  # type: (str) -> Certificate
        location = self._get_crt_location('HTTPS')
        return self.add_certificate(location, content)

    def add_ldap_certificate(self, content):  # type: (str) -> Certificate
        location = self._get_crt_location('LDAP')
        return self.add_certificate(location, content)

    def add_ca_certificate(self, content):  # type: (str) -> Certificate
        location = self._get_crt_location('CA')
        return self.add_certificate(location, content)

    def add_certificate(self, location, content):  # type: (str, str) -> Certificate
        path = location

        self._client.post(path, body={
            'CertificateString': content,
        })

        return self.get_certificate(location)

    def generate_csr(
        self,
        crt_type,  # type: str
        country,  # type: str
        city,  # type: str
        common_name,  # type: str
        state,  # type: str
        organization,  # type: str
        organizational_unit,  # type: str
        alternative_names=None,  # type: Optional[List[str]]
        key_usage=None,  # type: Optional[List[str]]
        contact_person='',  # type: Optional[str]
        challenge_password='',  # type: Optional[str]
        email='',  # type: Optional[str]
        given_name='',  # type: Optional[str]
        initials='',  # type: Optional[str]
        key_pair_algorithm='EC',  # type: Optional[str]
        key_curve_id='secp384r1',  # type: Optional[str]
        surname='',  # type: Optional[str]
        unstructured_name='',  # type: Optional[str]
        crt_location=None,  # type: Optional[str]
    ):   # type: (...) -> str

        crt_location = self._get_crt_location(crt_type)

        if len(country) != 2:
            raise Exception(
                'Argument "country" must have 2 characters. '
                'String "{0}" with {1} characters was passed'.format(
                    country,
                    len(country),
                )
            )

        response = self._client.post(
            "{0}/Actions/CertificateService.GenerateCSR".format(self._path),
            body={
                "CertificateCollection": {'@odata.id': crt_location},
                "Country": country,
                "City": city,
                "CommonName": common_name,
                "State": state,
                "Organization": organization,
                "AlternativeNames": alternative_names or [],
                "KeyUsage": key_usage or [],
                "ChallengePassword": challenge_password,
                "ContactPerson": contact_person,
                "Email": email,
                "GivenName": given_name,
                "Initials": initials,
                "KeyCurveId": key_curve_id,
                "KeyPairAlgorithm": key_pair_algorithm,
                "OrganizationalUnit": organizational_unit,
                "Surname": surname,
                "UnstructuredName": unstructured_name,
            }
        ).json

        return response['CSRString']

    def get_all_certificates(self):  # type: () -> List[Certificate]
        response = self._client.get(
            self._path + '/CertificateLocations').json

        crt_collection = []
        if response['Links']['Certificates@odata.count'] > 0:
            paths = [d['@odata.id'] for d
                     in response['Links']['Certificates']]

            for path in paths:
                crt_data = self._client.get(path).json
                crt = Certificate.from_json(self._client, crt_data)
                crt_collection.append(crt)

        return crt_collection

    def get_https_certificate(self):  # type: () -> Certificate
        location = self._get_crt_location('HTTPS')
        return self.get_certificate(location)

    def get_ldap_certificate(self):  # type: () -> Certificate
        location = self._get_crt_location('LDAP')
        return self.get_certificate(location)

    def get_ca_certificate(self):  # type: () -> Certificate
        location = self._get_crt_location('CA')
        return self.get_certificate(location)

    def get_certificate(self, location):  # type: (str) -> Certificate
        response = self._client.get(location).json

        members = response['Members']
        if len(members) > 0:
            path = members[0]['@odata.id']
            crt_data = self._client.get(path).json
            crt = Certificate.from_json(self._client, crt_data)
            return crt

    def _get_crt_location(self, crt_type):  # type: (str) -> str
        crt_type = crt_type.upper()
        location = CERTIFICATE_LOCATIONS.get(crt_type)
        if not location:
            raise Exception(
                'Wrong type of certificate was passed. '
                'Available: {0}. Received: {1}'.format(
                    ', '.join(CERTIFICATE_LOCATIONS.keys()),
                    crt_type,
                )
            )

        return location

    # TODO: Should make Certificate.replace() method. It would be simpler
    #  for client's code. But it requires the link from Certificate to
    #  CertificateService and it's hard for implementation for now.
    def replace_certificate(
        self,
        init_crt,  # type: Certificate
        new_crt_content,  # type: str
        crt_format='PEM',  # type: str
    ):  # type: (...) -> None

        self._client.post(
            self._path + '/Actions/CertificateService.ReplaceCertificate',
            body={
                'CertificateUri': {
                    '@odata.id': init_crt.location + '/' + init_crt.id,
                },
                'CertificateType': crt_format,
                'CertificateString': new_crt_content,
            }
        )


class CertificateServiceMockup_v1_0_0(CertificateService_v1_0_0):

    def add_certificate(self, location, content):  # type: (str, str) -> Certificate
        path = location

        data_absence_msg = 'Data is not presented in mockup object'
        self._client.post(path, body={
            '@odata.type': '#Certificate.v1_0_0.Certificate',
            'CertificateString': content,
            'Issuer': data_absence_msg,
            'KeyUsage': data_absence_msg,
            'Name': data_absence_msg,
            'Subject': data_absence_msg,
            'ValidNotAfter': data_absence_msg,
            'ValidNotBefore': data_absence_msg,
        })

        return self.get_certificate(location)
