# Copyright 2014-2015 Red Hat, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from oslo_config import cfg
from oslo_log import log

from ceilometer.agent import plugin_base as plugin
from ceilometer.i18n import _LW
from ceilometer import keystone_client

LOG = log.getLogger(__name__)

cfg.CONF.import_group('service_credentials', 'ceilometer.keystone_client')


class EndpointDiscovery(plugin.DiscoveryBase):
    """Discovery that supplies service endpoints.

    This discovery should be used when the relevant APIs are not well suited
    to dividing the pollster's work into smaller pieces than a whole service
    at once. Example of this is the floating_ip pollster which calls
    nova.floating_ips.list() and therefore gets all floating IPs at once.
    """

""" Edit by Tony
    This discovery is only for:
    http://192.168.1.10:8774/v2/d04021d5a4144b4c9f579fdc1d1c2a9a
    http://192.168.1.10:9292
"""

    @staticmethod
    def discover(manager, param=None):
        endpoints = keystone_client.get_service_catalog(
            manager.keystone).get_urls(
                service_type=param,
                interface=cfg.CONF.service_credentials.interface,
                region_name=cfg.CONF.service_credentials.region_name)
        LOG.debug("Tony: endpoints = %s", endpoints)
        if not endpoints:
            LOG.warning(_LW('No endpoints found for service %s'),
                        "<all services>" if param is None else param)
            return []
        return endpoints
