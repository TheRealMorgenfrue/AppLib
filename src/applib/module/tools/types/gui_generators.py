from typing import TypeAlias

from app.generators.card_generator import CardGenerator
from app.generators.cardwidget_generator import CardWidgetGenerator

AnyCardGenerator: TypeAlias = CardGenerator | CardWidgetGenerator
