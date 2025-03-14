# Copyright 2025 Google LLC
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

from auth import decorators
from auth.abstract_datastore import AbstractDatastore


class FileDatastore(AbstractDatastore):
  """File Datastore.

  This is the Datastore contract to be fufilled by any file storage method. It
  contains the functions common to all file-type datastores, as well as any
  abstract methods to be implemented for each specific system.

  All unimplemented functions raise a NotImplementedError() rather than
  simply 'pass'.
  """
  def persist(f: Callable) -> Any:
    """Decorator to write the key/value pairs to the storage file.

    This avoids code duplication of the `persist` behaviour, and if the
    function is wrapped in the decorator, we can't forget to persist the map!

    Args:
        f (Callable): the function to wrap

    Returns:
        Any: the return value of `f`
    """
    def f_persist(*args: Mapping[str, Any], **kw: Mapping[str, Any]) -> Any:
      datastore = args[0]
      try:
        return f(*args, **kw)
      finally:
        with datastore.storage() as storage:
          storage.write(json.dumps(datastore.datastore, indent=2))
    return f_persist

  @decorators.lazy_property
  def datastore_file(self) -> str:
    return self._datastore_file

  @datastore_file.setter
  def datastore_file(self, datastore_file: str) -> None:
    self._datastore_file = datastore_file

  def storage(self):
    """storage

    Fetches the file pointer to the appropriate file storage as a `bytestream`
    that can be used in a `write` statement to persist the storage map.
    """
    raise NotImplementedError('Must be implemented by child class.')

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

  def list_documents(self, key: Optional[str] = None) -> List[str]:
    """Lists documents in a collection.

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

    Returns:
        documents (List[DocumentReference]): list of all documents
    """
    return self.list_documents()

  @persist
  def store_document(self, id: str, document: Dict[str, Any]) -> None:
    """Stores a document.

    Args:
        id (str): report id
        report_data (Dict[str, Any]): report configuration
    """
    self.datastore.update({id: document})

  @persist
  def update_document(self, id: str, new_data: Dict[str, Any]) -> None:
    """Updates a document.

    Args:
        id (str): the id of the document within the collection.
        new_data (Dict[str, Any]): the document content.
    """
    if document := self.datastore.get(id):
      document.update(new_data)
    else:
      self.store_document(id, new_data)

  persist

  def delete_document(self, id: str, key: Optional[str] = None) -> None:
    """Deletes a document.

    This removes a document or partial document from the datastore. If a key is
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
