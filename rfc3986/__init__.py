# -*- coding: utf-8 -*-
# Copyright (c) 2014 Rackspace
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
rfc3986
=======

An implementation of semantics and validations described in RFC 3986. See
http://rfc3986.rtfd.org/ for documentation.

:copyright: (c) 2014 Rackspace
:license: Apache v2.0, see LICENSE for details
"""

__title__ = 'rfc3986'
__author__ = 'Ian Cordasco'
__author_email__ = 'ian.cordasco@rackspace.com'
__license__ = 'Apache v2.0'
__copyright__ = 'Copyright 2014 Rackspace'
__version__ = '0.2.1'

from .api import (URIReference, uri_reference, is_valid_uri, normalize_uri)

__all__ = ['URIReference', 'uri_reference', 'is_valid_uri', 'normalize_uri']