# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import unittest
from unittest import mock

from .credentials_helpers import encode_key
from .exceptions import KeyEncodingError


class CredentialsHelpersTest(unittest.TestCase):
  def test_encode_valid(self) -> None:
    self.assertEqual('YnV0dGVyY3VwQGFzeW91d2lzaC5jb20',
                     encode_key('buttercup@asyouwish.com'))

  def test_encode_none(self) -> None:
    with self.assertRaisesRegex(KeyEncodingError, 'Cannot encode None'):
      encode_key(None)
