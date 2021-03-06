# Copyright 2011 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Keypair interface (1.1 extension).
"""

from novaclient import api_versions
from novaclient import base


class Keypair(base.Resource):
    """
    A keypair is a ssh key that can be injected into a server on launch.
    """

    def __repr__(self):
        return "<Keypair: %s>" % self.id

    def _add_details(self, info):
        dico = 'keypair' in info and \
            info['keypair'] or info
        for (k, v) in dico.items():
            # NOTE(rpodolyaka): keypair name allows us to uniquely identify
            #                   a specific keypair, while its id attribute
            #                   is nothing more than an implementation
            #                   detail. We can safely omit the id attribute
            #                   here to ensure setattr() won't raise
            #                   AttributeError trying to set read-only
            #                   property id
            if k != 'id':
                setattr(self, k, v)

    @property
    def id(self):
        return self.name

    def delete(self):
        self.manager.delete(self)


class KeypairManager(base.ManagerWithFind):
    resource_class = Keypair
    keypair_prefix = "os-keypairs"
    is_alphanum_id_allowed = True

    @api_versions.wraps("2.0", "2.9")
    def get(self, keypair):
        """
        Get a keypair.

        :param keypair: The ID of the keypair to get.
        :rtype: :class:`Keypair`
        """
        return self._get("/%s/%s" % (self.keypair_prefix, base.getid(keypair)),
                         "keypair")

    @api_versions.wraps("2.10")
    def get(self, keypair, user_id=None):
        """
        Get a keypair.

        :param keypair: The ID of the keypair to get.
        :param user_id: Id of key-pair owner (Admin only).
        :rtype: :class:`Keypair`
        """
        query_string = "?user_id=%s" % user_id if user_id else ""
        url = "/%s/%s%s" % (self.keypair_prefix, base.getid(keypair),
                            query_string)
        return self._get(url, "keypair")

    @api_versions.wraps("2.0", "2.1")
    def create(self, name, public_key=None):
        """
        Create a keypair

        :param name: name for the keypair to create
        :param public_key: existing public key to import
        """
        body = {'keypair': {'name': name}}
        if public_key:
            body['keypair']['public_key'] = public_key
        return self._create('/%s' % self.keypair_prefix, body, 'keypair')

    @api_versions.wraps("2.2", "2.9")
    def create(self, name, public_key=None, key_type="ssh"):
        """
        Create a keypair

        :param name: name for the keypair to create
        :param public_key: existing public key to import
        :param key_type: keypair type to create
        """
        body = {'keypair': {'name': name,
                            'type': key_type}}
        if public_key:
            body['keypair']['public_key'] = public_key
        return self._create('/%s' % self.keypair_prefix, body, 'keypair')

    @api_versions.wraps("2.10")
    def create(self, name, public_key=None, key_type="ssh", user_id=None):
        """
        Create a keypair

        :param name: name for the keypair to create
        :param public_key: existing public key to import
        :param key_type: keypair type to create
        :param user_id: user to add.
        """
        body = {'keypair': {'name': name,
                            'type': key_type}}
        if public_key:
            body['keypair']['public_key'] = public_key
        if user_id:
            body['keypair']['user_id'] = user_id
        return self._create('/%s' % self.keypair_prefix, body, 'keypair')

    @api_versions.wraps("2.0", "2.9")
    def delete(self, key):
        """
        Delete a keypair

        :param key: The :class:`Keypair` (or its ID) to delete.
        """
        self._delete('/%s/%s' % (self.keypair_prefix, base.getid(key)))

    @api_versions.wraps("2.10")
    def delete(self, key, user_id=None):
        """
        Delete a keypair

        :param key: The :class:`Keypair` (or its ID) to delete.
        :param user_id: Id of key-pair owner (Admin only).
        """
        query_string = "?user_id=%s" % user_id if user_id else ""
        url = '/%s/%s%s' % (self.keypair_prefix, base.getid(key), query_string)
        self._delete(url)

    @api_versions.wraps("2.0", "2.9")
    def list(self):
        """
        Get a list of keypairs.
        """
        return self._list('/%s' % self.keypair_prefix, 'keypairs')

    @api_versions.wraps("2.10")
    def list(self, user_id=None):
        """
        Get a list of keypairs.

        :param user_id: Id of key-pairs owner (Admin only).
        """
        query_string = "?user_id=%s" % user_id if user_id else ""
        url = '/%s%s' % (self.keypair_prefix, query_string)
        return self._list(url, 'keypairs')
