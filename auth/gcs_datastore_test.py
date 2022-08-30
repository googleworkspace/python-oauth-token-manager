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

from . import gcs_datastore

from copy import deepcopy
from typing import Any, Dict

MASTER_CONFIG = {
    "auth": {
        "api_key": "api_key",
        "bHVrZUBza3l3YWxrZXIuY29t": {
            "access_token": "access_token",
            "refresh_token": "refresh_token",
            "_key": "luke@skywalker.com"
        },
    },
}

CLASS_UNDER_TEST = 'auth.gcs_datastore'


class GCSDatastoreTest(unittest.TestCase):
  def setUp(self):
    self.open = mock.mock_open(read_data=json.dumps(MASTER_CONFIG))
    # mock.patch('gcsfs.GCSFileSystem', autospec=True).start()

  @mock.patch('gcsfs.GCSFileSystem')
  def test_get_document_with_key(self, mock_filesystem):
    mock_filesystem.return_value.get.return_value = []

    with mock.patch(f'{CLASS_UNDER_TEST}.open', self.open):
      datastore = gcs_datastore.GCSDatastore(project='westley',
                                             bucket='buttercup')
      self.assertEqual({'api_key': 'api_key'},
                       datastore.get_document('auth', 'api_key'))

  @mock.patch('gcsfs.GCSFileSystem')
  def test_get_document_without_key(self, mock_filesystem):
    mock_filesystem.return_value.get.return_value = []
    with mock.patch(f'{CLASS_UNDER_TEST}.open', self.open):
      datastore = gcs_datastore.GCSDatastore(project='westley',
                                             bucket='buttercup')
      self.assertEqual(MASTER_CONFIG,
                       datastore.get_document('auth'))

  @mock.patch('gcsfs.GCSFileSystem')
  def test_get_document_missing_type(self, mock_filesystem):
    mock_filesystem.return_value.get.return_value = []
    with mock.patch(f'{CLASS_UNDER_TEST}.open', self.open):
      datastore = gcs_datastore.GCSDatastore(project='westley',
                                             bucket='buttercup')
      self.assertEqual(None, datastore.get_document('10011'))

  @mock.patch('gcsfs.GCSFileSystem')
  def test_get_document_missing_id(self, mock_filesystem):
    mock_filesystem.return_value.get.return_value = []
    with mock.patch(f'{CLASS_UNDER_TEST}.open', self.open):
      datastore = gcs_datastore.GCSDatastore(project='westley',
                                             bucket='buttercup')
      self.assertEqual(None, datastore.get_document('10011'))

  @mock.patch('gcsfs.GCSFileSystem')
  def test_get_document_missing_key(self, mock_filesystem):
    mock_filesystem.return_value.get.return_value = []
    with mock.patch(f'{CLASS_UNDER_TEST}.open', self.open):
      datastore = gcs_datastore.GCSDatastore(project='westley',
                                             bucket='buttercup')
      self.assertEqual(None, datastore.get_document('auth', 'foo'))

  @mock.patch('gcsfs.GCSFileSystem')
  def test_store_new_document(self, mock_filesystem):
    mock_filesystem.return_value.get.return_value = []
    with mock.patch(f'{CLASS_UNDER_TEST}.open', self.open):
      datastore = gcs_datastore.GCSDatastore(project='westley',
                                             bucket='buttercup')
      datastore.store_document(id='0000', document={'id': '0000'})

      expected = deepcopy(MASTER_CONFIG)
      expected.update({'0000': {'id': '0000'}})

  @mock.patch('gcsfs.GCSFileSystem')
  def test_store_new_document_new_name(self, mock_filesystem):
    mock_filesystem.return_value.get.return_value = []
    with mock.patch(f'{CLASS_UNDER_TEST}.open', self.open):
      datastore = gcs_datastore.GCSDatastore(
          project='westley',
          bucket='buttercup',
          datastore_file='new_datastore.json')
      datastore.store_document(id='0000', document={'id': '0000'})

      expected = deepcopy(MASTER_CONFIG)
      expected.update({'0000': {'id': '0000'}})

  @mock.patch('gcsfs.GCSFileSystem')
  def test_list_documents_all(self, mock_filesystem):
    mock_filesystem.return_value.get.return_value = []
    with mock.patch(f'{CLASS_UNDER_TEST}.open', self.open):
      datastore = gcs_datastore.GCSDatastore(project='westley',
                                             bucket='buttercup')

      _docs = datastore.list_documents()
      expected = MASTER_CONFIG
      self.assertDictEqual(expected, _docs)

  @mock.patch('gcsfs.GCSFileSystem')
  def test_list_documents_auth(self, mock_filesystem):
    mock_filesystem.return_value.get.return_value = []
    with mock.patch(f'{CLASS_UNDER_TEST}.open', self.open):
      datastore = gcs_datastore.GCSDatastore(project='westley',
                                             bucket='buttercup')

      _docs = datastore.list_documents('auth')
      expected = MASTER_CONFIG.get('auth')
      self.assertEqual(expected.keys(), _docs)

  @mock.patch('gcsfs.GCSFileSystem')
  def test_list_documents_none(self, mock_filesystem):
    mock_filesystem.return_value.get.return_value = []
    with mock.patch(f'{CLASS_UNDER_TEST}.open', self.open):
      datastore = gcs_datastore.GCSDatastore(project='westley',
                                             bucket='buttercup')

      _docs = datastore.list_documents('foo')
      self.assertIsNone(_docs)

  @mock.patch('gcsfs.GCSFileSystem')
  def test_get_all_documents(self, mock_filesystem):
    mock_filesystem.return_value.get.return_value = []
    with mock.patch(f'{CLASS_UNDER_TEST}.open', self.open):
      datastore = gcs_datastore.GCSDatastore(project='westley',
                                             bucket='buttercup')

      _docs = datastore.get_all_documents()
      expected = MASTER_CONFIG
      self.assertEqual(expected, _docs)

  @mock.patch('gcsfs.GCSFileSystem')
  def test_delete_document_collection(self, mock_filesystem):
    mock_filesystem.return_value.get.return_value = []
    with mock.patch(f'{CLASS_UNDER_TEST}.open', self.open):
      datastore = gcs_datastore.GCSDatastore(project='westley',
                                             bucket='buttercup')

      datastore.delete_document(id='auth')
      self.assertEqual({}, datastore.datastore)

  @mock.patch('gcsfs.GCSFileSystem')
  def test_delete_document_key(self, mock_filesystem):
    mock_filesystem.return_value.get.return_value = []
    with mock.patch(f'{CLASS_UNDER_TEST}.open', self.open):
      datastore = gcs_datastore.GCSDatastore(project='westley',
                                             bucket='buttercup')

      datastore.delete_document(
          id='auth', key='api_key')
      self.assertEqual({
          'auth': {'bHVrZUBza3l3YWxrZXIuY29t': {
              '_key': 'luke@skywalker.com',
              'access_token': 'access_token',
                              'refresh_token': 'refresh_token'}}},
          datastore.datastore)

  @mock.patch('gcsfs.GCSFileSystem')
  def test_delete_document_key_missing(self, mock_filesystem):
    mock_filesystem.return_value.get.return_value = []
    with mock.patch(f'{CLASS_UNDER_TEST}.open', self.open):
      datastore = gcs_datastore.GCSDatastore(project='westley',
                                             bucket='buttercup')

      datastore.delete_document(
          id='auth', key='foo')
      self.assertEqual(MASTER_CONFIG,
                       datastore.datastore)

  @mock.patch('gcsfs.GCSFileSystem')
  def test_update_document_existing(self, mock_filesystem):
    mock_filesystem.return_value.get.return_value = []
    with mock.patch(f'{CLASS_UNDER_TEST}.open', self.open):
      datastore = gcs_datastore.GCSDatastore(project='westley',
                                             bucket='buttercup')

      expected = {'api_key': 'new api key'}
      datastore.update_document(id='auth',
                                new_data=expected)
      self.assertEqual(expected.get('api_key'),
                       datastore.datastore.get('auth').get('api_key'))
