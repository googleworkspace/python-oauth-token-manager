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
from typing import Any, Callable, Dict, List, Mapping, Optional

import gcsfs

from auth.local_datastore import LocalDatastore

from . import decorators
from .abstract_datastore import AbstractDatastore


def persist(f: Callable) -> Any:
  """Persists the datastore after internal manipulations.

  This is used to decorate functions that modify the internal json object
  containing the authentication credentials and ensures that any changes
  locally will be written back to the store automatically.

  Args:
      f (Callable): the source of the persist action

  Returns:
      Any: whatever the original function returns
  """
  def f_persist(*args: Mapping[str, Any], **kw: Mapping[str, Any]) -> Any:
    datastore = args[0]                 # 'self' in the original caller
    try:
      return f(*args, **kw)
    finally:
      fs = gcsfs.GCSFileSystem(project=datastore.project)
      file_name = f'{datastore.bucket}/{datastore.datastore_file}'
      with fs.open(file_name, 'w') as storage:
        storage.write(json.dumps(datastore.datastore, indent=2))
  return f_persist


class GCSDatastore(LocalDatastore):
  """A datastore for storing auth credentials in GCS.
  """
  @decorators.lazy_property
  def datastore(self) -> Dict[str, Any]:
    try:
      fs = gcsfs.GCSFileSystem(project=self.project)
      file_name = f'{self.bucket}/{self.datastore_file}'
      with open(file_name, 'r') as store:
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
    self._project = project
    self._email = email
    self._bucket = bucket
    self._datastore_file = datastore_file

  @decorators.lazy_property
  def datastore_file(self) -> str:
    return self._datastore_file

  @decorators.lazy_property
  def bucket(self) -> str:
    return self._bucket

  @decorators.lazy_property
  def project(self) -> str:
    return self._project

  def get_document(self, id: str, key: Optional[str] = None) -> Dict[str, Any]:
    """Fetches a document (could be anything, 'type' identifies the root.)

    Fetch a document

    Arguments:
        id (str): document id
        key: Optional(str): the document collection sub-key

    Returns:
        Dict[str, Any]: stored configuration dictionary, or None
                          if not present
    """
    if parent := self.datastore.get(id):
      if key:
        value = parent.get(key)
        return {key: value} if value else None
      else:
        return {id: parent}

  @persist
  def store_document(self, id: str, document: Dict[str, Any]) -> None:
    """Stores a document.

    Store a document in Firestore. They're all stored by Type
    (DCM/DBM/SA360/ADH) and each one within the type is keyed by the
    appropriate report id.

    Args:
        id (str): report id
        report_data (Dict[str, Any]): report configuration
    """
    self.datastore.update({id: document})

  @persist
  def update_document(self, id: str, new_data: Dict[str, Any]) -> None:
    """Updates a document.

    Update a document in Firestore. If the document is not already there, it
    will be created as a net-new document. If it is, it will be updated.

    Args:
        id (str): the id of the document within the collection.
        new_data (Dict[str, Any]): the document content.
    """
    # super().update_document(id=id, new_data=new_data)
    if document := self.datastore.get(id):
      document.update(new_data)

  @persist
  def delete_document(self, id: str, key: Optional[str] = None) -> None:
    """Deletes a document.

    This removes a document or partial document from the Firestore. If a key is
    supplied, then just that key is removed from the document. If no key is
    given, the entire document will be removed from the collection. If neither
    key is present, nothing will happen.

    Args:
        id (str): the id of the document within the collection.
        key (str, optional): the key to remove. Defaults to None.
    """
    try:
      if key:
        if doc := self.datastore.get(id):
          doc.pop(key)
      else:
        self.datastore.pop(id)

    except KeyError:
      None

  def list_documents(self, key: Optional[str] = None) -> List[str]:
    """Lists documents in a collection.

    List all the documents in the collection 'type'. If a key is give, list
    all the sub-documents of that key. For example:

    list_documents(Type.SA360_RPT) will show { '_reports', report_1, ... }
    list_documents(Type.SA360_RPT, '_reports') will return
      { 'holiday_2020', 'sa360_hourly_depleted', ...}

    Args:
        key (str, optional): the sub-key. Defaults to None.

    Returns:
        List[str]: the list
    """
    keys = None
    if self.datastore:
      if key:
        if sub_docs := self.datastore.get(key):
          keys = sub_docs.keys()
      else:
        keys = self.datastore

    return keys

  def get_all_documents(self) -> List[Dict[str, Any]]:
    """Lists all documents

    Lists all documents of a given Type

    Returns:
        documents (List[DocumentReference]): list of all documents
    """
    return self.list_documents()
