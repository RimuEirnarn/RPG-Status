"""RPGStatus

The basic status will be implemented here."""

from typing import Union
from yaml import safe_dump, safe_load
from lib.htf import format
from dataclasses import dataclass


# TODO: Always do runtime type checking for every Character creation. This must be affecting only Attribute, CharAttribute and ComputationalAttribute
# But only creation at .load() will use 'Literal' only to Race and Gender parameter.

# Internal classs

class StaticTypingException(TypeError):
    """Type passed is missmatch with type hint."""

# Internal functions


def _is_valid_attribute(instance: 'Attribute') -> bool:
    for key, val in instance.__dict__.items():
        if not isinstance(val, int):
            return False
    return True


def _is_valid_comp_attribute(instance: 'ComputationalAttribute') -> bool:
    for key, val in instance.__dict__.items():
        if not isinstance(val, (int, float)):
            return False
    return True


def _is_valid_char_attribute(instance: 'CharAttribute') -> bool:
    for key, val in instance.__dict__.items():
        if key == "Race":
            if not isinstance(val, Race):
                return False
        elif key == "Gender":
            if not isinstance(val, int):
                return False
            if val < 0 or val > 3:
                return False
        elif not isinstance(val, (int, str, dict)):
            return False
        elif isinstance(val, dict):
            # Skills
            for key, val_ in val.items():
                if not isinstance(key, str) and isinstance(val_, str):
                    return False
    return True


def _is_valid_everything(instance1: 'Attribute', instance2: 'CharAttribute', instance3: 'ComputationalAttribute') -> bool:
    n1 = _is_valid_attribute(instance1)
    n2 = _is_valid_comp_attribute(instance3)
    n3 = _is_valid_char_attribute(instance2)
    if sum((n1, n2, n3)) != 3:
        return False
    return True


def _is_valid_for_char_attribute(instance1: 'Attribute', instance2: 'CharAttribute'):
    n1 = _is_valid_attribute(instance1)
    n2 = _is_valid_char_attribute(instance2)
    if sum((n1, n2)) != 2:
        return False
    return True


# =================================================================

class Race:
    pass


class Item:
    pass


@dataclass(repr=True, eq=True, frozen=False, init=True)
class Attribute:
    """Attribute class"""
    Str: int
    Agi: int
    Dex: int
    Int: int
    Luck: int
    Wis: int
    Will: int
    Vit: int
    Per: int
    End: int
    Res: int
    Sta: int


@dataclass(repr=True, eq=True, frozen=False, init=True)
class ComputationalAttribute:
    """Computational attribute"""
    Magical_Atk: int
    Magical_Def: int
    Critical_Percentage: Union[float, int]
    Dodge_Percentage: Union[float, int]
    Atk: int
    Def: int
    Accuracy: Union[float, int]
    Speed_Acceleration: Union[float, int]
    Max_HitPoint: int
    Max_MagicalPoint: int


@dataclass(repr=True, eq=True, frozen=False, init=True)
class CharAttribute:
    """Character Attribute"""
    Level: int
    EXP: int
    Name: str
    Race: 'Race'
    Age: int
    Skills: dict[str, str]


class BaseCharacter:
    """Base class for character"""
    skill_enclosing_declose = '「 ', '」'
    def __init__(self, char_attribute: CharAttribute, attribute: Attribute):
        if not _is_valid_for_char_attribute(attribute, char_attribute):
            raise StaticTypingException('Invalid attribute type. Perhaps you have put one of these attributes in wrong type. Check your instances if they matched with type hints or not.')
        self._name = char_attribute.Name
        self._char_attribute = char_attribute
        self._attribute = attribute
    
    def __repr__(self):
        return f"<{self.__class__.__name__}: {self._name}>"
    
    def dump(self, **options) -> str:
        """Dump the object into Yaml string"""
        obj = self._char_attribute.__dict__.copy()
        obj.update(self._attribute.__dict__.copy())
        v = safe_dump(obj, **options) # trying to ignore VSCode's Python 'errors'.
        if isinstance(v, str):
            return v
        raise Exception("Failed to dump object: %s" % v)
    
    @classmethod
    def load(cls, filename: str):
        """Load a file into a BaseCharacter object."""
        fill_arg1 = ['Str', "Int", 'Con', "Agi", "Dex", "Wis", "Will", "Luck"]
        fill_arg2 = ["Name", "Race", "Level", 'EXP', 'Age', 'Skills']
        arg1 = {}
        arg2 = {}
        with open(filename) as file:
            obj = safe_load(file)
        for key, val in obj.items():
            if key in fill_arg1:
                arg1[key] = val
            elif key in fill_arg2:
                arg2[key] = val
        
        # Special handle for 'Race' parameter
        # Define 'string' get for all Races in Race's list
        #raise NotImplementedError

        obj1 = CharAttribute(**arg2)
        obj2 = Attribute(**arg1)

        if not _is_valid_for_char_attribute(obj2, obj1):
            raise StaticTypingException("Invalid attribute type. Perhaps you have put one of these attributes in wrong type. Check your Yaml object and try again.")

        return cls(obj1, obj2)
