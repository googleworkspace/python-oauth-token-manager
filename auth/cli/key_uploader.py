# Copyright 2022 Google LLC
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
from __future__ import annotations

import json

import gcsfs

from auth.credentials_helpers import encode_key


class KeyUpload(object):
  def load_src(self, file: str, project: str) -> json:
    if file.startswith('gs://'):
      with gcsfs.GCSFileSystem(project=project).open(file, 'r') as data_file:
        src_data = json.loads(data_file.read())
    else:
      # Assume locally stored token file
      with open(file, 'r') as data_file:
        src_data = json.loads(data_file.read())

    return src_data

  def upload(self, **args) -> None:
    """Uploads data to firestore.

    Args:
        key (str): the data key.
        file (str): the file containing the data.
        encode_key (bool): should the key be encoded (eg is it an email).
        local_store (bool): local storage (True) or Firestore (False).
    """
    _project = args.get('project')
    _key = args.get('key')

    if file := args.get('file'):
      src_data = self.load_src(file, _project)

    if args.get('encode_key'):
      key = encode_key(_key)

    else:
      key = _key

    src_data['email'] = _key

    if args.get('local_store'):
      from auth.datastore.local_file import LocalFile
      f = LocalFile()

    if args.get('firestore'):
      from auth.datastore.firestore import Firestore
      f = Firestore()

    if args.get('secret_manager'):
      from auth.datastore.secret_manager import SecretManager
      f = SecretManager(project=_project, email=args.get('email'))

    if args.get('cloud_storage'):
      from auth.datastore.cloud_storage import CloudStorage
      f = CloudStorage(project=_project,
                       email=args.get('email'),
                       bucket=args.get('bucket'))

    f.update_document(id=key, new_data=src_data)
