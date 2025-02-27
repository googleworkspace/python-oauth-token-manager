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

from typing import Any, Dict, List, Optional
from auth import decorators


class AbstractDatastore(object):
  """Abstract Datastore.

  This is the Datastore contract to be fufilled by any storage method. It
  contains the functions to be implemented by the concrete versions, as well as
  helpers (that are used throughought the system) which simply recall the more
  generic functions - for example 'remove_report_runner(id)' is the same as
  'delete_document(id)' but in the context of where it is used
  is clearer than the latter.

  All unimplemented functions raise a NotImplementedError() rather than
  simply 'pass'.
  """
  @decorators.lazy_property
  def project(self) -> str:
    return self._project

  @project.setter
  def project(self, project: str) -> None:
    self._project = project

  @decorators.lazy_property
  def email(self) -> str:
    return self._email

  @email.setter
  def email(self, email: str) -> None:
    self._email = email

  def get_document(self, key: Optional[str] = None) -> Dict[str, Any]:
    """Fetches a document (could be anything, 'type' identifies the root.)

    Fetch a document

    Arguments:
        id (str): document id
        key: Optional(str): the document collection sub-key

    Returns:
        Dict[str, Any]: stored configuration dictionary, or None
                          if not present
    """
    raise NotImplementedError('Must be implemented by child class.')

  def store_document(self, id: str,
                     document: Dict[str, Any]) -> None:
    """Stores a document.

    Store a document in the datastore.

    Arguments:
        id (str): report id
        report_data (Dict[str, Any]): report configuration
    """
    raise NotImplementedError('Must be implemented by child class.')

  def update_document(self, id: str, new_data: Dict[str, Any]) -> None:
    """Updates a document.

    Update a document in the datastore. If the document is not already there, it
    will be created as a net-new document. If it is, it will be updated.

    Args:
        id (str): the id of the document within the collection.
        new_data (Dict[str, Any]): the document content.
    """
    raise NotImplementedError('Must be implemented by child class.')

  def delete_document(self, id: str, key: Optional[str] = None) -> None:
    """Deletes a document.

    This removes a document or partial document from the datastore. If a key is
    supplied, then just that key is removed from the document. If no key is
    given, the entire document will be removed from the collection.

    Args:
        id (str): the id of the document within the collection.
        key (str, optional): the key to remove. Defaults to None.
    """
    raise NotImplementedError('Must be implemented by child class.')

  def list_documents(self, key: str = None) -> List[str]:
    """Lists documents in a collection.

    List all the documents.

    Args:
        key (str, optional): the sub-key. Defaults to None.

    Returns:
        List[str]: the list
    """
    raise NotImplementedError('Must be implemented by child class.')

  def get_all_documents(self) -> List[Dict[str, Any]]:
    """Fetches all documents

    Fetches all documents.

    Returns:
        runners (List[Dict[str, Any]]): contents of all documents
    """
    raise NotImplementedError('Must be implemented by child class.')
