# (c) Copyright 2014 Hewlett-Packard Development Company, L.P.
#    All Rights Reserved.
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
#
"""Fake HP client for testing LeftHand without installing the client."""

import sys

import mock

from cinder.tests import fake_hp_client_exceptions as hpexceptions

hplefthand = mock.Mock()
hplefthand.version = "1.0.4"
hplefthand.exceptions = hpexceptions

sys.modules['hplefthandclient'] = hplefthand
