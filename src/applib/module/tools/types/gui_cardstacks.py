from typing import TypeAlias

from ....app.components.cardstack import PivotCardStack, SegmentedPivotCardStack


AnyCardStack: TypeAlias = PivotCardStack | SegmentedPivotCardStack
