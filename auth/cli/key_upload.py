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

import json
from contextlib import suppress

import gcsfs
from absl import app, flags

from auth.credentials_helpers import encode_key

FLAGS = flags.FLAGS
flags.DEFINE_string('project', None, 'GCP Project.')
flags.DEFINE_string('email', None, 'Report owner/user email.')
flags.DEFINE_string('key', None, 'Key to create/update')
flags.DEFINE_string('file', None, 'File containing json data')
flags.DEFINE_string('bucket', None, 'GCS Bucket for the datastore.')
flags.DEFINE_bool('encode_key', False, 'Encode the key (for tokens).')
flags.DEFINE_bool('local', False, 'Local storage.')
flags.DEFINE_bool('firestore', False, 'Send to Firestore.')
flags.DEFINE_bool('secret_manager', False, 'Send to Secret Manager.')
flags.DEFINE_bool('cloud_storage', False, 'Send to GCS.')
flags.mark_flags_as_required(['file', 'key'])
flags.mark_bool_flags_as_mutual_exclusive(
    ['local', 'firestore', 'secret_manager', 'cloud_storage'], required=True)


def upload(**args) -> None:
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
    if file.startswith('gs://'):
      with gcsfs.GCSFileSystem(project=_project).open(file, 'r') as data_file:
        src_data = json.loads(data_file.read())
    else:
      # Assume locally stored token file
      with open(file, 'r') as data_file:
        src_data = json.loads(data_file.read())

  if args.get('encode_key'):
    key = encode_key(_key)

  else:
    key = _key

  src_data['email'] = _key

  if args.get('local_store'):
    from auth.datastore.local_datastore import LocalDatastore
    f = LocalDatastore()

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


def main(unused_argv):
  upload(**FLAGS.flag_values_dict())


if __name__ == '__main__':
  with suppress(SystemExit):
    app.run(main)
