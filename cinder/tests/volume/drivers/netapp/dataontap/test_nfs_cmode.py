# Copyright (c) 2014 Andrew Kerr.  All rights reserved.
# Copyright (c) 2015 Tom Barron.  All rights reserved.
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
Mock unit tests for the NetApp cmode nfs storage driver
"""

import mock
from oslo_utils import units

from cinder.brick.remotefs import remotefs as remotefs_brick
from cinder import test
from cinder.tests.volume.drivers.netapp.dataontap import fakes as fake
from cinder.tests.volume.drivers.netapp import fakes as na_fakes
from cinder import utils
from cinder.volume.drivers.netapp.dataontap.client import client_cmode
from cinder.volume.drivers.netapp.dataontap import nfs_cmode
from cinder.volume.drivers.netapp import utils as na_utils
from cinder.volume.drivers import nfs


class NetAppCmodeNfsDriverTestCase(test.TestCase):
    def setUp(self):
        super(NetAppCmodeNfsDriverTestCase, self).setUp()

        kwargs = {'configuration': self.get_config_cmode()}

        with mock.patch.object(utils, 'get_root_helper',
                               return_value=mock.Mock()):
            with mock.patch.object(remotefs_brick, 'RemoteFsClient',
                                   return_value=mock.Mock()):
                self.driver = nfs_cmode.NetAppCmodeNfsDriver(**kwargs)
                self.driver._mounted_shares = [fake.NFS_SHARE]
                self.driver.ssc_vols = True

    def get_config_cmode(self):
        config = na_fakes.create_configuration_cmode()
        config.netapp_storage_protocol = 'nfs'
        config.netapp_login = 'admin'
        config.netapp_password = 'pass'
        config.netapp_server_hostname = '127.0.0.1'
        config.netapp_transport_type = 'http'
        config.netapp_server_port = '80'
        config.netapp_vserver = 'openstack'
        return config

    @mock.patch.object(client_cmode, 'Client', mock.Mock())
    @mock.patch.object(nfs.NfsDriver, 'do_setup')
    @mock.patch.object(na_utils, 'check_flags')
    def test_do_setup(self, mock_check_flags, mock_super_do_setup):
        self.driver.do_setup(mock.Mock())

        self.assertTrue(mock_check_flags.called)
        self.assertTrue(mock_super_do_setup.called)

    def test_get_pool_stats(self):

        total_capacity_gb = na_utils.round_down(
            fake.TOTAL_BYTES / units.Gi, '0.01')
        free_capacity_gb = na_utils.round_down(
            fake.AVAILABLE_BYTES / units.Gi, '0.01')
        capacity = dict(
            reserved_percentage = fake.RESERVED_PERCENTAGE,
            total_capacity_gb = total_capacity_gb,
            free_capacity_gb = free_capacity_gb,
        )

        mock_get_capacity = self.mock_object(
            self.driver, '_get_share_capacity_info')
        mock_get_capacity.return_value = capacity

        mock_get_vol_for_share = self.mock_object(
            self.driver, '_get_vol_for_share')
        mock_get_vol_for_share.return_value = None

        result = self.driver._get_pool_stats()

        self.assertEqual(fake.RESERVED_PERCENTAGE,
                         result[0]['reserved_percentage'])
        self.assertEqual(total_capacity_gb, result[0]['total_capacity_gb'])
        self.assertEqual(free_capacity_gb, result[0]['free_capacity_gb'])
