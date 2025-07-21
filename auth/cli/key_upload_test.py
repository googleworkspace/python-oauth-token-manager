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
# from copy import deepcopy
from unittest import mock

from .key_uploader import KeyUpload

CLASS_UNDER_TEST = 'auth.local_file'
MASTER_FILE = {'test_root': {'a': 'A', 'b': 'B'}, 'email': 'key'}


class KeyUploadTest(unittest.TestCase):
  def setUp(self) -> None:
    self.open = mock.mock_open(read_data=json.dumps(MASTER_FILE))

  def test_good_unencoded(self):
    with mock.patch(f'{CLASS_UNDER_TEST}.open', self.open):
      test = KeyUpload()

      test.load_src = mock.MagicMock(return_value=MASTER_FILE)
      event = {
          'key': 'key',
          'file': 'test.json',
          'encode_key': False,
          'local_store': True,
      }
      test.upload(**event)
      self.open().write.assert_called_once()
      # self.assertEqual(expected.get('api_key'),
      #                  datastore.datastore.get('auth').get('api_key'))

  # def test_good_unencoded(self):
  #   with mock.patch(f'{CLASS_UNDER_TEST}.open', self.open):
  #     _ = mock.patch.object(KeyUpload, 'load_src', self.open)
  #     mock_method = mock.patch.object(local_file.LocalFile,
  #                                     'update_document',
  #                                     return_value=None)
  #     event = {
  #         'key': 'key',
  #         'file': 'test.json',
  #         'encode_key': False,
  #         'local_store': True,
  #     }
  #     _ = KeyUpload().upload(**event)
  #     self.open.assert_called_with('test.json', 'r')
  #     self.open().read.assert_called()
  #     mock_method.assert_called()
  #     mock_method.assert_called_with(id='key',
  #                                    new_data=MASTER_FILE)

  # def test_good_encoded(self):
  #   with mock.patch(f'{CLASS_UNDER_TEST}.open', self.open):
  #     with mock.patch.object(local_file.LocalFile,
  #                            'update_document',
  #                            return_value=None) as mock_method:
  #       event = {
  #         'key': 'key',
  #         'file': 'test.json',
  #         'encode_key': True,
  #         'local_store': True,
  #       }
  #       _ = key_upload.upload(**event)
  #       self.open.assert_called_with('test.json', 'r')
  #       self.open().read.assert_called()
  #       mock_method.assert_called()
  #       expected = deepcopy(self.valid_source)

  #       mock_method.assert_called_with(id='a2V5',
  #                                      new_data=expected)
