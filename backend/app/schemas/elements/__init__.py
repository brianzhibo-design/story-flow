"""
视觉元素属性 Schema 集合
"""

from .character import CharacterAttributes, AgeRange, BodyType
from .location import LocationAttributes, TimeOfDay, Weather, LightingType
from .prop import PropAttributes
from .costume import CostumeAttributes
from .style import StyleAttributes
from .shot import ShotAttributes, ShotType, CameraAngle, CameraMovement

__all__ = [
    # Character
    "CharacterAttributes",
    "AgeRange", 
    "BodyType",
    # Location
    "LocationAttributes",
    "TimeOfDay",
    "Weather",
    "LightingType",
    # Prop
    "PropAttributes",
    # Costume
    "CostumeAttributes",
    # Style
    "StyleAttributes",
    # Shot
    "ShotAttributes",
    "ShotType",
    "CameraAngle",
    "CameraMovement",
]
