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

from dataclasses import dataclass
from datetime import datetime
import json
from typing import Any, Dict, Mapping, Type, TypeVar, Union
from io import BytesIO

import pytz
from dateutil.relativedelta import relativedelta
from google.auth.transport import requests
from google.oauth2 import credentials as oauth

from auth import decorators

from auth.abstract_datastore import AbstractDatastore
from auth.credentials_helpers import encode_key
from auth.exceptions import CredentialsError


@dataclass
class ProjectCredentials(object):
  """ProjectCredentials

  A dataclass to hold the client is and secret to be passed around within the
  functions.
  """
  client_id: str
  client_secret: str


class Credentials(object):
  """Credentials.

  This is the Credentials contract to be fufilled by any concrete version. It
  contains the OAuth functions necessary for Credentials, but none of the ways
  to fetch the credential sources or to store updated ones. These should be
  done by the 'datastore', which will be created in the concrete implementation.

  'datastore' can return a 'pass', although if it is not set, this will cause
  failures further down the line if an attempt is made to store or load
  credentials.
  """
  _datastore: AbstractDatastore = None

  TDatastore = TypeVar('TDatastore', bound=AbstractDatastore)

  def __init__(self,
               datastore: Type[TDatastore],
               email: str = None,
               project: str = None,
               **dsargs) -> Credentials:
    self.email = email
    self.project = project
    self._datastore = datastore(email=email, project=project, **dsargs)

  @property
  def email(self) -> str:
    return self._email

  @email.setter
  def email(self, email: str) -> None:
    self._email = email

  @property
  def project(self) -> str:
    return self._project

  @project.setter
  def project(self, project: str) -> None:
    self._project = project

  @property
  def datastore(self) -> AbstractDatastore:
    """The datastore property."""
    return self._datastore

  @datastore.setter
  def datastore(self, f: AbstractDatastore) -> None:
    """datastore setter

    This will always raise an exception. Once the `Credentials` object has been
    created, the datastore cannot be changed. If you need to move the object
    from one datastore to another, then create a second `Credentials` object
    pointing to the new datastore and pass in the OAuth Credentials, either
    as the OAuth credentials object or as a `Mapping[str, Any]`.

    Args:
        f (AbstractDatastore): the datastore

    Raises:
        KeyError: the datastore should be immutable
    """
    raise KeyError('Datastore can only be set on instantiation.')

  @decorators.lazy_property
  def project_credentials(self) -> ProjectCredentials:
    """The project credentials.

    This is lazy-evaluated using the decorator, so the project credentials
    are only fetched once from the datastore for the life of the object,
    reducing API calls and thus improving speed and reducing cost.

    Returns:
        ProjectCredentials: the project client id and secret as a dataclass
    """
    secrets = None
    if secrets := self.datastore.get_document(id='client_id'):
      secrets |= self.datastore.get_document(id='client_secret')

    elif client_secret := self.datastore.get_document(id='client_secret'):
      secrets = \
          client_secret.get('web') or \
          client_secret.get('installed')

    creds = \
        ProjectCredentials(client_id=secrets['client_id'],
                           client_secret=secrets['client_secret']) \
        if secrets else None

    return creds

  @decorators.lazy_property
  def token_details(self) -> Dict[str, Any]:
    """The users's OAuth token."""
    return self.datastore.get_document(id=encode_key(self._email))

  def store_credentials(self,
                        creds: Union[oauth.Credentials, Mapping[str, Any]]) -> None:
    """Stores the credentials.

    This function uses the datastore to store the user credentials for later.
    It's default behaviour is 'pass' as it relies upon the concrete
    implementation's datastore which is the only one that should be aware of
    where the creds are being stored.

    Args:
        creds (oauth.Credentials): [description]
    """
    if self._email:
      key = encode_key(self._email)

      if isinstance(creds, oauth.Credentials):
        self.datastore.update_document(id=key,
                                       new_data=self._to_dict(creds))
      else:
        self.datastore.update_document(id=key, new_data=creds)

  def _refresh_credentials(self, creds: oauth.Credentials) -> None:
    """Refreshes the Google OAuth credentials.

    Returns:
        google.oauth2.credentials.Credentials: the credentials
    """
    creds.refresh(requests.Request())
    self.store_credentials(creds)

  def _to_utc(self, last_date: datetime) -> datetime:
    """Convert a datetime to UTC

    Args:
        last_date (datetime): the date to convert

    Returns:
        datetime: the date in UTC
    """
    if (last_date.tzinfo is None or
            last_date.tzinfo.utcoffset(last_date) is None):
      last_date = pytz.UTC.localize(last_date)

    return last_date

  def _to_dict(self, credentials: oauth.Credentials) -> Mapping[str, Any]:
    """Convert an OAuth token to a dict

    Note the conversion of the expiry date (A `datetime` object) to the Zulu
    format date string. This is because the primary function of the dict is to
    be serialized to the `Datastore` and we have to ensure that all fields can
    be turned to `json` for this purpose. When reinstantiated, the OAuth
    Credentials object takes care of converting the expiry date back to a
    `datetime` for us.

    Args:
        credentials (oauth.Credentials): the OAuth credentials

    Returns:
        Mapping[str, Any]: the credentials as a `dict[str, Any]`
    """
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
            'default_scopes': credentials.default_scopes,
            'expiry': credentials.expiry.strftime('%Y-%m-%dT%H:%M:%SZ')}

  @property
  def credentials(self) -> oauth.Credentials:
    """Fetches the credentials.

    Returns:
       (google.oauth2.credentials.Credentials):  the credentials
    """
    expiry = self._to_utc(
        datetime.now().astimezone(pytz.utc) + relativedelta(minutes=60))

    if token := self.token_details:
      if isinstance(token, str):
        token = json.loads(token)

      creds = oauth.Credentials.from_authorized_user_info(token)

      if creds.expired:
        creds.expiry = expiry
        self._refresh_credentials(creds=creds)

    else:
      creds = None
      raise CredentialsError(message='credentials not found', email=self._email)

    return creds

  @property
  def auth_headers(self) -> Dict[str, Any]:
    """Returns authorized http headers.

    This function calls the 'get_credentials' to grab the latest, refreshed
    OAuth credentials for the user, and uses them to create the OAuth2 header
    dict needed for some HTTP requests.

    Returns:
      oauth2_headers (Dict[str, Any]):  the OAuth headers
    """
    oauth2_header = {}
    self.credentials.apply(oauth2_header)

    return oauth2_header
