# Copyright (c) 2012 Zadara Storage, Inc.
# Copyright (c) 2012 OpenStack Foundation
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
Tests for ZFS volume driver
"""

import mox
import time

from oslo.config import cfg

from cinder.openstack.common import log as logging
from cinder.openstack.common import processutils as putils
from cinder import test
from cinder.volume import configuration as conf
from cinder.volume.drivers.zfs import ZFSVolumeDriver

LOG = logging.getLogger("cinder.volume.driver")

CONF = cfg.CONF
# LOG = logging.getLogger(__name__)


class ZFSDriverTestCase(test.TestCase):
    """Test case for ZFS volume driver."""

    def setUp(self):
        super(ZFSDriverTestCase, self).setUp()

        self.mox = mox.Mox()
        CONF.zfs_zpool = 'fake_pool'
        self.driver = ZFSVolumeDriver(configuration=conf.Configuration(None))

    def tearDown(self):
        self.mox.UnsetStubs()
        super(ZFSDriverTestCase, self).tearDown()

    def test_create(self):
        """Create volume."""

        fake_vol = {'name': 'vol001', 'size': '20'}

        self.mox.StubOutWithMock(self.driver, '_execute')

        self.driver._execute('zfs', 'list', 'fake_pool/vol001',
                             run_as_root=True).\
            AndRaise(putils.ProcessExecutionError(
                stderr="dataset does not exist"))

        self.driver._execute('zfs', 'create', '-s', '-V', '20g',
                             'fake_pool/vol001',
                             run_as_root=True)

        self.mox.ReplayAll()
        self.driver.create_volume(fake_vol)

        self.mox.VerifyAll()

    def test_create_exists(self):
        """Create volume, while backing location already exists."""

        fake_vol = {'name': 'vol001', 'size': '20'}

        self.mox.StubOutWithMock(self.driver, '_execute')

        self.driver._execute('zfs', 'list', 'fake_pool/vol001',
                             run_as_root=True).\
            AndReturn(("PLACEHOLDER", ""))

        self.mox.ReplayAll()
        self.driver.create_volume(fake_vol)

        self.mox.VerifyAll()

    def test_create_from_snapshot(self):
        """Create volume from a snapshot."""

        fake_vol = {'name': 'vol001', 'size': '20'}
        fake_snap = {'volume_name': 'vol002', 'name': 'snapity'}

        self.mox.StubOutWithMock(self.driver, '_execute')

        self.driver._execute('zfs', 'clone', 'fake_pool/vol002@snapity',
                             'fake_pool/vol001', run_as_root=True)

        self.mox.ReplayAll()
        self.driver.create_volume_from_snapshot(fake_vol, fake_snap)

        self.mox.VerifyAll()

    def test_delete(self):
        """Delete volume."""

        fake_vol = {'name': 'vol001', 'size': '20'}

        self.mox.StubOutWithMock(self.driver, '_execute')

        self.driver._execute('zfs', 'get', '-H', '-r',
                             '-t', 'snapshot',
                             'clones', 'fake_pool/vol001',
                             run_as_root=True).\
            AndReturn(("", ""))

        self.driver._execute('zfs', 'destroy', '-r', 'fake_pool/vol001',
                             run_as_root=True)

        self.mox.ReplayAll()
        self.driver.delete_volume(fake_vol)

        self.mox.VerifyAll()

    def test_delete_retry(self):
        """Delete volume."""

        fake_vol = {'name': 'vol001', 'size': '20'}

        self.mox.StubOutWithMock(self.driver, '_execute')
        self.mox.StubOutWithMock(time, 'sleep')

        self.driver._execute('zfs', 'get', '-H', '-r',
                             '-t', 'snapshot',
                             'clones', 'fake_pool/vol001',
                             run_as_root=True).\
            AndReturn(("", ""))

        self.driver._execute('zfs', 'destroy', '-r', 'fake_pool/vol001',
                             run_as_root=True).\
            AndRaise(putils.ProcessExecutionError(stderr="dataset is busy"))

        time.sleep(15)

        self.driver._execute('zfs', 'get', '-H', '-r',
                             '-t', 'snapshot',
                             'clones', 'fake_pool/vol001',
                             run_as_root=True).\
            AndReturn(("", ""))

        self.driver._execute('zfs', 'destroy', '-r', 'fake_pool/vol001',
                             run_as_root=True)

        self.mox.ReplayAll()
        self.driver.delete_volume(fake_vol)

        self.mox.VerifyAll()

    def test_create_snapshot(self):
        """Creates a snapshot."""

        fake_snap = {'volume_name': 'vol002', 'name': 'snapity'}

        self.mox.StubOutWithMock(self.driver, '_execute')

        self.driver._execute('zfs', 'snapshot', 'fake_pool/vol002@snapity',
                             run_as_root=True).\
            AndReturn(("", ""))

        self.mox.ReplayAll()
        self.driver.create_snapshot(fake_snap)

        self.mox.VerifyAll()

    def test_delete_snapshot(self):
        """Creates a snapshot."""

        fake_snap = {'volume_name': 'vol002', 'name': 'snapity'}

        self.mox.StubOutWithMock(self.driver, '_execute')

        self.driver._execute('zfs', 'destroy', '-d',
                             'fake_pool/vol002@snapity', run_as_root=True).\
            AndReturn(("", ""))

        self.mox.ReplayAll()
        self.driver.delete_snapshot(fake_snap)

        self.mox.VerifyAll()
