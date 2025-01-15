import os
from typing import TypeAlias

from pydantic import BaseModel

StrPath: TypeAlias = str | os.PathLike[str]
Model: TypeAlias = BaseModel
