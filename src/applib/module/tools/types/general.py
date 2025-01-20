import os
from typing import SupportsIndex, SupportsInt, TypeAlias
from typing_extensions import Buffer

from pydantic import BaseModel

ReadableBuffer: TypeAlias = Buffer
ConvertibleToInt: TypeAlias = str | ReadableBuffer | SupportsInt | SupportsIndex
StrPath: TypeAlias = str | os.PathLike[str]
Model: TypeAlias = BaseModel
