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

import base64

from auth.exceptions import KeyEncodingError


def encode_key(key: str) -> str:
  """Creates the key to use in json oauth storage.

  Converts an string to a base64 version to use as a key both for security
  (so you can't easily see which credential goes with which key) but also as
  Secret Manager and Firestore can only have [A-Za-z0-9] in keys.
  Stripping the '=' padding is fine as the value will never have to be
  translated back.

  Returns:
      str: base64 representation of the key value.
  """
  try:
    if encoded_key := base64.b64encode(
            key.encode('utf-8')).decode('utf-8').rstrip('='):
      return encoded_key

  except KeyEncodingError:
    raise KeyEncodingError(f'Cannot encode {key}.')
