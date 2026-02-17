import os
from typing import SupportsIndex, SupportsInt, TypeAlias

from pydantic import BaseModel
from typing_extensions import Buffer

ReadableBuffer: TypeAlias = Buffer
ConvertibleToInt: TypeAlias = str | ReadableBuffer | SupportsInt | SupportsIndex
StrPath: TypeAlias = str | os.PathLike[str]
floatOrInt: TypeAlias = float | int

Model: TypeAlias = BaseModel
"""A Pydantic validation model (not constructed)"""
