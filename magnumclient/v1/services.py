# Copyright 2014 NEC Corporation.  All rights reserved.
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

from magnumclient.common import base
from magnumclient.common import utils
from magnumclient import exceptions

CREATION_ATTRIBUTES = ['bay_uuid', 'manifest', 'manifest_url']


class Service(base.Resource):
    def __repr__(self):
        return "<COE-Service %s>" % self._info


class ServiceManager(base.Manager):
    resource_class = Service

    @staticmethod
    def _path(id=None, bay_uuid=None):
        if id and bay_uuid:
            return '/v1/services/%s/%s' % (id, bay_uuid)
        else:
            return '/v1/services'

    def list(self, bay_ident, marker=None, limit=None, sort_key=None,
             sort_dir=None, detail=False):
        """Retrieve a list of services.

        :param bay_ident: UUID or Name of the Bay.
        :param marker: Optional, the UUID or Name of a service, e.g. the
                       last service from a previous result set. Return
                       the next result set.
        :param limit: The maximum number of results to return per
                      request, if:

            1) limit > 0, the maximum number of services to return.
            2) limit == 0, return the entire list of services.
            3) limit param is NOT specified (None), the number of items
               returned respect the maximum imposed by the Magnum API
               (see Magnum's api.max_limit option).

        :param sort_key: Optional, field used for sorting.

        :param sort_dir: Optional, direction of sorting, either 'asc' (the
                         default) or 'desc'.

        :param detail: Optional, boolean whether to return detailed information
                       about services.

        :returns: A list of services.

        """
        if limit is not None:
            limit = int(limit)

        filters = utils.common_filters(marker, limit, sort_key, sort_dir)
        filters.append('bay_ident=%s' % bay_ident)

        path = ''
        if detail:
            path += 'detail'
        if filters:
            path += '?' + '&'.join(filters)

        if limit is None:
            return self._list(self._path(path), "services")
        else:
            return self._list_pagination(self._path(path), "services",
                                         limit=limit)

    def get(self, service_id, bay_uuid):
        try:
            return self._list(self._path(service_id, bay_uuid))[0]
        except IndexError:
            return None

    def create(self, **kwargs):
        new = {}
        for (key, value) in kwargs.items():
            if key in CREATION_ATTRIBUTES:
                new[key] = value
            else:
                raise exceptions.InvalidAttribute(
                    "Key must be in %s" % ",".join(CREATION_ATTRIBUTES))
        return self._create(self._path(), new)

    def delete(self, service_id, bay_uuid):
        return self._delete(self._path(service_id, bay_uuid))

    def update(self, service_id, bay_uuid, patch):
        return self._update(self._path(service_id, bay_uuid), patch)
