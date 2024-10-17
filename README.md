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

Other storage locations can be added at will simply by extending the
`AbstractDatastore` class in the same way as the four examples.


## Initial Setup And Installation

## Enable the APIs on Google Cloud

In order to use the connectors to any of the Google Cloud storage methods
(Secret Manager, Firestore and Google Cloud Storage) you will have to ensure
that the relevant APIs have been enabled. Follow the instructions listed in the
[developer documentation](https://cloud.google.com/apis/docs/getting-started)
to enable the API you need.

## Ensure the app's service account has acces to the APIs

## Implementation specific

### Secret Manager

Two secrets will need to be manually added to Secret Manager before the library
can be used. These are the client id and client secret. The easiest way to do
this is using a small shell script like this:

```
#!/bin/bash

while [[ $1 == -* ]] ; do
  case $1 in
    --project*)
      IFS="=" read _cmd PROJECT <<< "$1" && [ -z ${PROJECT} ] && shift && PROJECT=$1
      ;;
    --client-id*)
      IFS="=" read _cmd CLIENT_ID <<< "$1" && [ -z ${CLIENT_ID} ] && shift && CLIENT_ID=$1
      ;;
    --client-secret*)
      IFS="=" read _cmd CLIENT_SECRET <<< "$1" && [ -z ${CLIENT_SECRET} ] && shift && CLIENT_SECRET=$1
      ;;
    *)
      usage
      echo ""
      echo "Unknown parameter $1."
      exit
  esac
  shift
done

if [ -z ${CLIENT_ID} ] || [ -z ${CLIENT_SECRET} ] || [ -z ${PROJECT} ]; then
  echo You must supply CLIENT_ID and CLIENT_SECRET.
  exit
fi

gcloud --project ${PROJECT} secrets create client_id --replication-policy=automatic 2>/dev/null
echo "{ \"client_id\": \"${CLIENT_ID}\" }" | gcloud --project ${PROJECT} secrets versions add client_id --data-file=-

gcloud --project ${PROJECT} secrets create client_secret --replication-policy=automatic 2>/dev/null
echo "{ \"client_id\": \"${CLIENT_SECRET}\" }" | gcloud --project ${PROJECT} secrets versions add client_secret --data-file=-

```

The library will create any further secrets and versions automatically. It will
also remove all but the latest secret each time an update occurs. This reduces
the usage cost of Secret Manager substantially as projects are charged based
partially on number of _active_ (ie not destroyed) secret versions.

### Firestore

Firestore requires no additional configuration.

### Google Cloud Storage

To use Google Cloud Storage you must have a bucket created in which the user
token files and project secrets are to be stored and to which the app's service
account has read/write access. This should then be locked down so that no other
non-administrators have access.

### Local files

No special configuration is required. This implementation is HIGHLY insecure,
and is provided simply for testing/development purposes.

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

### Storing a token

#### Secret Manager

```
from auth.secret_manager import SecretManager
manager = SecretManager(project='<gcp project name>')

manager.update_document(id=encode_key('<token_id>'), new_data=<token string>)
```

This will implicitly create a `secret` if there was not one already, or simply
update an existing secret with a new 'live' version of the secret.

### Removing a secret

```
from auth.secret_manager import SecretManager
manager = SecretManager(project='<gcp project name>')

manager.delete_document(id=encode_key('<token_id>'))
```

### Listing all the available secrets

```
from auth.secret_manager import SecretManager
manager = SecretManager(project='<gcp project name>')

manager.list_documents()
```
