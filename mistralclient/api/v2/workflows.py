# Copyright 2014 - Mirantis, Inc.
# Copyright 2015 - StackStorm, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import six

from mistralclient.api import base


urlparse = six.moves.urllib.parse


class Workflow(base.Resource):
    resource_name = 'Workflow'


class WorkflowManager(base.ResourceManager):
    resource_class = Workflow

    def create(self, definition, scope='private'):
        self._ensure_not_empty(definition=definition)

        resp = self.client.http_client.post(
            '/workflows?scope=%s' % scope,
            definition,
            headers={'content-type': 'text/plain'}
        )

        if resp.status_code != 201:
            self._raise_api_exception(resp)

        return [self.resource_class(self, resource_data)
                for resource_data in base.extract_json(resp, 'workflows')]

    def update(self, definition, scope='private'):
        self._ensure_not_empty(definition=definition)

        resp = self.client.http_client.put(
            '/workflows?scope=%s' % scope,
            definition,
            headers={'content-type': 'text/plain'}
        )

        if resp.status_code != 200:
            self._raise_api_exception(resp)

        return [self.resource_class(self, resource_data)
                for resource_data in base.extract_json(resp, 'workflows')]

    def list(self, marker='', limit=None, sort_keys='', sort_dirs=''):
        qparams = {}

        if marker:
            qparams['marker'] = marker

        if limit:
            qparams['limit'] = limit

        if sort_keys:
            qparams['sort_keys'] = sort_keys

        if sort_dirs:
            qparams['sort_dirs'] = sort_dirs

        query_string = ("?%s" % urlparse.urlencode(list(qparams.items()))
                        if qparams else "")

        return self._list(
            '/workflows%s' % query_string,
            response_key='workflows',
        )

    def get(self, name):
        self._ensure_not_empty(name=name)

        return self._get('/workflows/%s' % name)

    def delete(self, name):
        self._ensure_not_empty(name=name)

        self._delete('/workflows/%s' % name)

    def validate(self, definition):
        self._ensure_not_empty(definition=definition)

        resp = self.client.http_client.post(
            '/workflows/validate',
            definition,
            headers={'content-type': 'text/plain'}
        )

        if resp.status_code != 200:
            self._raise_api_exception(resp)

        return base.extract_json(resp, None)
