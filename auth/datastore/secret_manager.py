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
from typing import Any, List, Mapping, Optional, Type

from google.cloud import secretmanager, secretmanager_v1
from google.cloud.secretmanager_v1.types import resources

from auth import decorators
from auth.abstract_datastore import AbstractDatastore


class SecretManager(AbstractDatastore):

  def __init__(self, email: str = None,
               project: str = None) -> AbstractDatastore:
    self._project = project
    self._email = email

  @decorators.lazy_property
  def parent(self) -> str:
    return f'projects/{self._project}'

  @property
  def client(self) -> secretmanager.SecretManagerServiceClient:
    return secretmanager.SecretManagerServiceClient()

  def list_documents(self, report_type: Optional[Type] = None,
                     key: Optional[str] = None) -> List[str]:
    request = secretmanager_v1.ListSecretsRequest(parent=self.parent)
    all_secrets = self.client.list_secrets(request=request)
    secrets = list([secret.name for secret in all_secrets])
    return secrets

  def create_secret(self, id: str,
                    **unused: Mapping[str, Any]) -> resources.Secret:
    """
    Create a new secret with the given name. A secret is a logical wrapper
    around a collection of secret versions. Secret versions hold the actual
    secret material.
    """
    try:
      secret = secretmanager.Secret(replication=secretmanager.Replication(
          automatic=secretmanager.Replication.Automatic()))
      request = secretmanager_v1.CreateSecretRequest(parent=self.parent,
                                                     secret_id=id,
                                                     secret=secret)
      response = self.client.create_secret(request=request)

    except Exception as e:
      print(e)

    return response

  @decorators.implicit_create(creator=create_secret)
  def store_document(self,  id: str, document: Mapping[str, Any],
                     type: Optional[Type] = None) -> resources.SecretVersion:
    """Stores a document.

    Store a document in Secret Manager. This will, for credentials, always be
    the OAuth token.

    Arguments:
        id (str): The document id.
        document (Dict[str, Any]): The document to store.
        type (Optional[Type]): Unused.
    """
    payload = secretmanager_v1.SecretPayload(
        data=bytes(json.dumps(document), 'utf-8'))
    request = secretmanager_v1.AddSecretVersionRequest(
        parent=self.client.secret_path(self._project, id),
        payload=payload)
    return self.client.add_secret_version(request=request)

  def update_document(self, id: str, new_data: Mapping[str, Any],
                      type: Optional[Type] = None) -> None:
    """Updates a document.

    Update a document in Secret Manager. If the document is not already there,
    it will be created as a net-new document. If it is, it will be updated.

    As this is a specific 'update' request, remove any other enabled versions.

    Args:
        id (str): the id of the document.
        new_data (Dict[str, Any]): the document content.
        type (Optional[Type]): Unused.
    """
    new_version: resources.SecretVersion = self.store_document(
        id=id, type=type, document=new_data)

    # Destroy all versions other than the latest for cost reasons..
    request = secretmanager_v1.ListSecretVersionsRequest(
        parent=self.client.secret_path(project=self._project, secret=id),
        filter='state:enabled'
    )
    version_list = self.client.list_secret_versions(request=request)
    for page in version_list.pages:
      for version in page.versions:
        # Only delete older versions
        if version.create_time < new_version.create_time:
          self.client.destroy_secret_version(
              secretmanager_v1.DestroySecretVersionRequest(
                  name=version.name
              ))

  def _get_latest(self, id: str) -> resources.SecretVersion:
    """Fetches the latest secret version.

    Arguments:
        id (str): document id.

    Returns:
        SecretVersion: the latest version of the stored secret.
    """
    secret = self.client.secret_version_path(project=self._project,
                                             secret=id,
                                             secret_version='latest')
    try:
      request = secretmanager_v1.GetSecretVersionRequest(name=secret)
      response = self.client.get_secret_version(request=request)
      return response
    except Exception as e:
      print(e)
      return None

  def get_document(self, id: str, type: Optional[Type] = None,
                   key: Optional[str] = None) -> Mapping[str, Any]:
    """Fetches a document (could be anything).

    Fetch a document

    Arguments:
        id (str): document id.
        key: Optional(str): Unused.

    Returns:
        Dict[str, Any]: stored document, or None if not present.
    """
    secret = self.client.secret_version_path(project=self._project,
                                             secret=id,
                                             secret_version='latest')
    try:
      request = secretmanager_v1.AccessSecretVersionRequest(name=secret)
      response = self.client.access_secret_version(request=request)
      document = json.loads(response.payload.data.decode('utf-8'))
      return document

    except Exception as e:
      print(e)
      return None

  def delete_document(self, id: str, type: Optional[Type] = None,
                      key: Optional[str] = None) -> None:
    """Deletes a document.

    This removes a document or version from the Secret Manager. If a key is
    supplied, then just that key (version) is removed from the document. If no
    key is given, the entire document will be removed.

    Args:
        id (str): the id of the document within the collection.
        key (str, optional): the key to remove. Defaults to None.
    """
    if key:
      request = secretmanager_v1.DestroySecretVersionRequest(
          name=self.client.secret_version_path(project=self._project,
                                               secret=id, secret_version=key))
      delete = self.client.destroy_secret_version

    else:
      request = secretmanager_v1.DeleteSecretRequest(
          name=self.client.secret_path(project=self._project, secret=id))
      delete = self.client.delete_secret

    delete(request=request)
