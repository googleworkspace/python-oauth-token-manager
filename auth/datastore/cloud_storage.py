# Copyright 2024 Google LLC
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
from typing import Any, Dict

import gcsfs
from auth import decorators
from .file_datastore import FileDatastore
from auth.abstract_datastore import AbstractDatastore


class CloudStorage(FileDatastore):
  """A datastore for storing auth credentials in GCS.
  """
  @decorators.lazy_property
  def datastore(self) -> Dict[str, Any]:
    try:
      fs = gcsfs.GCSFileSystem(project=self.project)
      file_name = f'{self.bucket}/{self.datastore_file}'
      with fs.open(file_name, 'r') as store:
        if data := store.read():
          return json.loads(data)
        else:
          return {}

    except FileNotFoundError:
      return {}

  def __init__(self,
               project: str,
               bucket: str,
               email: str = None,
               datastore_file: str = 'datastore.json') -> AbstractDatastore:
    self.project = project
    self.email = email
    self.bucket = bucket
    self.datastore_file = datastore_file

  @decorators.lazy_property
  def bucket(self) -> str:
    return self._bucket

  @bucket.setter
  def bucket(self, bucket: str) -> None:
    self._bucket = bucket

  def storage(self):
    fs = gcsfs.GCSFileSystem(project=self.project)
    file_name = f'{self.bucket}/{self.datastore_file}'
    return fs.open(file_name, 'w')
