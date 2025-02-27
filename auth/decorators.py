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

from functools import wraps
from typing import Any, Callable

from google.api_core import exceptions


def lazy_property(f: Callable):
  """Decorator that makes a property lazy-evaluated.

  Args:
    f: the function to convert to a lazy property.
  """
  attr_name = '_lazy_' + f.__name__

  @property
  def _lazy_property(self) -> Any:
    if not hasattr(self, attr_name):
      setattr(self, attr_name, f(self))
    return getattr(self, attr_name)
  return _lazy_property


def implicit_create(creator: Callable) -> Any:
  """Decorator that will run a function if an item is not found.

  Once the `creator` is run, the original function is run a second time,
  ensuring that the prerequisite is now met. This is used in secret manager to
  implicitly handle the extra actions necessary to create the first version of
  a user's token in `SecretManager`.

  Args:
      creator (Callable): the function to execute

  Returns:
      Any: the result of the main function
  """
  def the_real_decorator(f: Callable) -> Any:
    @wraps(f)
    def wrapper(*args, **kwargs) -> Any:
      ran_creator = False
      while True:
        try:
          value = f(*args, **kwargs)
          return value
        except exceptions.NotFound:
          if ran_creator:
            return None
          creator(*args, **kwargs)
          ran_creator = True
    return wrapper
  return the_real_decorator
