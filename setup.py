# Copyright 2022 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
  long_description = fh.read()

setuptools.setup(
    name='python-oauth-token-manager',
    version='0.1.3',
    description='API for managing stored OAuth credentials.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='',
    author='David Harcombe',
    author_email='david.harcombe@gmail.com',
    license='Apache 2.0',
    zip_safe=False,
    include_package_data=True,
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires=">=3.9",
    install_requires=['dataclasses-json>=0.5.2',
                      'decorator>=4.4.2',
                      'gcs-oauth2-boto-plugin>=2.7',
                      'gcsfs>=0.7.2',
                      'google-api-core>=1.26.1',
                      'google-api-python-client>=2.0.2',
                      'google-auth-httplib2>=0.1.0',
                      'google-auth-oauthlib>=0.4.3',
                      'google-auth>=1.28.0',
                      'google-cloud-core>=1.6.0',
                      'google-cloud-firestore>=2.0.2',
                      'google-cloud-secret-manager>=2.8.0',
                      'google-cloud-storage>=1.36.2',
                      'google-reauth>=0.1.1',
                      'googleapis-common-protos>=1.53.0',
                      'httplib2>=0.19.0',
                      'oauth2client>=4.1.3',
                      'oauthlib>=3.1.0',
                      'pytz>=2021.1',
                      'requests-oauthlib>=1.3.0',
                      'requests>=2.27.1',
                      ],
)
