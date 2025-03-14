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
from auth.abstract_datastore import AbstractDatastore

from google.cloud import firestore


class Firestore(AbstractDatastore):
  @decorators.lazy_property
  def client(self) -> Any:
    """The datastore client."""
    return firestore.Client()

  @decorators.lazy_property
  def collection(self) -> str:
    return self._collection

  @collection.setter
  def collection(self, collection: str) -> None:
    self._collection = collection

  def __init__(self,
               email: str = None,
               project: str = None,
               collection: str = 'administration') -> AbstractDatastore:
    self.project = project
    self.email = email
    self.collection = collection

  def get_all_documents(self) -> List[firestore.DocumentReference]:
    """Lists all documents

    Lists all documents.

    Returns:
        documents (List[DocumentReference]): list of all documents
    """
    documents = self.client.collection(self.collection).list_documents()
    return documents

  def get_document(self, id: str,
                   key: Optional[str] = None) -> Dict[str, Any]:
    """Loads a document

    Load a document

    Arguments:
        id (str): document id
        key: Optional(str): the document collection sub-key

    Returns:
        Dict[str, Any]: stored configuration dictionary, or None
                          if not present
    """
    document = None

    if report := self.client.collection(self.collection().document(id)):
      document = report.get().to_dict()

    return document.get(key) if key and document else document

  def store_document(self, id: str,
                     document: Dict[str, Any]) -> None:
    """Stores a document.

    Store a document in Firestore.

    Arguments:
        id (str): report id
        report_data (Dict[str, Any]): report configuration
    """
    report = self.client.collection(self.collection).document(id)
    report.set(document)

  def update_document(self, id: str,
                      new_data: Dict[str, Any]) -> None:
    """Updates a document.

    Update a document in Firestore. If the document is not already there, it
    will be created as a net-new document. If it is, it will be updated.

    Args:
        id (str): the id of the document within the collection.
        new_data (Dict[str, Any]): the document content.
    """
    if collection := self.client.collection(self.collection):
      if document_ref := collection.document(document_id=id):
        if document_ref.get().exists:
          document_ref.update(new_data)
        else:
          document_ref.create(new_data)

  def delete_document(self, id: str,
                      key: Optional[str] = None) -> None:
    """Deletes a document.

    This removes a document or partial document from the datastore. If a key is
    supplied, then just that key is removed from the document. If no key is
    given, the entire document will be removed from the collection.

    Args:
        id (str): the id of the document within the collection.
        key (str, optional): the key to remove. Defaults to None.
    """
    if collection := self.client.collection(self.collection):
      if document_ref := collection.document(document_id=id):
        if key:
          document_ref.update({key: firestore.DELETE_FIELD})
        else:
          document_ref.delete()

  def list_documents(self, key: str = None) -> List[str]:
    """Lists documents in a collection.

    Args:
        key (str, optional): the sub-key. Defaults to None.

    Returns:
        List[str]: the list
    """
    documents = []
    collection = self.client.collection(self.collection).list_documents()
    for document in collection:
      if key:
        if document.id == key:
          for _document in document.get().to_dict():
            documents.append(_document)
      else:
        documents.append(document.id)

    return documents
