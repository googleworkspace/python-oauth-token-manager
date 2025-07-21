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

from contextlib import suppress

from absl import app, flags
from key_uploader import KeyUpload

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


def main(unused_argv):
  KeyUpload().upload(**FLAGS.flag_values_dict())


if __name__ == '__main__':
  with suppress(SystemExit):
    app.run(main)
