# Python Library for storing OAuth credentials in many locations

## What's this for?

By their very nature, OAuth credentials are valuable and dangerous, and have
to be stored securely. As a result, the same tasks to store these tokens in a
simple and secure fashion have to be written each time, or copied and pasted
around - leading to potential issues as problems are found and not fixed
in all places.

This library will store OAuth tokens in any of the following places:

1. Secret Manager
1. Firestore
1. Google Cloud Storage files
1. A local `json` file

Other storage locations can be added at will simply by forking this library and
extending the appropriate abstract classes.


## Initial Setup And Installation

## 


## Examples

### Fetching a token from storage

```
from auth.credentials_helpers import encode_key
from auth.secret_manager import SecretManager

manager = SecretManager(project='<gcp project name>')
key = manager.get_document(encode_key('<token id>'))
```

Note the use of `encode_key`. This is because many of the storage systems
supported do not allow special characters, and the most convenient identifier
for most OAuth tokens is the email address of the user. `encode_key` is a
base64 encoder - and no decoding is necessary.

The example given uses Secret Manager (part of Google Cloud). To use (say) GCS,
the code would change like this:

```
from auth.credentials_helpers import encode_key
from auth.gcs_datastore import GCSDatastore

manager = GCSDatastore(project='<gcp project name>', bucket='<gcs bucket>')
key = manager.get_document(encode_key('<token id>'))
```

All that changes is where the datastore is!

### Storing a token in Secret Manager

```
from auth.secret_manager import SecretManager
manager = SecretManager(project='<gcp project name>')

manager.update_document(id=encode_key('<token_id>'), new_data=<token string>)
```

This will implicitly create a `secret` if there was not one already, or simply
update an existing secret with a new 'live' version of the secret.

### Listing all the available secrets

```
from auth.secret_manager import SecretManager
manager = SecretManager(project='<gcp project name>')

manager.list_documents()
```


### Removing a secret

```
from auth.secret_manager import SecretManager
manager = SecretManager(project='<gcp project name>')

manager.delete_document(id=encode_key('<token_id>'))
```
