# -*- coding: utf8 -*-
"""RPGStatus

The basic status will be implemented here."""

__version__ = "0.0.1-5a Non-functional"
__author__ = "RimuEirnarn"

from abc import ABC, abstractmethod
from dataclasses import dataclass
from os.path import exists, join
from typing import Any, Iterable, Literal, NamedTuple, NoReturn, Union
from warnings import warn
from math import inf
from lib.internal import randint

from yaml import safe_dump, safe_load
from lib.htf import format
from dataclasses import dataclass

_debug_ = True
_default_unmatched_str = "Unmatched type of %s, expected %s but got %s"
structure_folder = "structures/"

# TODO: Always do runtime type checking for every Character creation. This must be affecting only Attribute, CharAttribute and ComputationalAttribute
# But only creation at .load() will use 'Literal' only to Race and Gender parameter.

# Internal classs


class NotAvailableWarning(Warning):
    """The object is set to NotAvailable constant."""

    @classmethod
    def warn(cls, attr_name: str = "", stacklevel=0, source=None):
        if attr_name != "":
            warn("Attribute %s is not available or is hereby not set. While the class initialization did not have default value, this attribute will be set to 0 or any type's default value." %
                 attr_name, cls, stacklevel, source)
        else:
            warn("An attribute is not available or is hereby not set. While the class initialization did not have default value, this attribute will be set to 0 or any type's default value.", cls, stacklevel, source)


class FrozenClassWarning(Warning):
    """Class(es) are/is in frozen state and thus, for further calculations cannot be done. Therefore, it/they cannot do anything."""

    @classmethod
    def warn(cls, for_=1, stacklevel=0, source=None):
        warn("A class is in frozen state and thus for further calculations cannot be done. Therefore, it cannot do anything."
             if for_ == 1 else
             "Some classes is in frozen state and thus for further calculations cannot be done. Therefore, they cannot do anything.", cls, stacklevel, source)


class FrozenClassError(Exception):
    """Classes that are required is a frozen classes."""


class UnableToSetAttribute(Exception):
    """An operation failed because the instance is not writable."""


class NotAvailable:
    def __init__(self):
        pass

    def __str__(self):
        return "N/A"

    def __bool__(self):
        return False

    def __repr__(self):
        return "N/A"


class ValidationReturn(NamedTuple):
    """ValidationReturn

    Usable by some internal checking functions.

    _is_valid_attribute,
    _is_valid_char_attribute,
    _is_valid_comp_attribute,
    _is_valid_everything,
    _is_valid_for_base_character

    These functions return this class or Iterable containing this class.

    :param Return: is actual function (boolean) return value.
    and other key/property/variable are for when Return is False.

    :param Error_Key: is a key of the value.
    :param Error_Value: is the value, the value that make validation returns false.
    :param Error_Reason: Reason/Description. A Error will be raised along with the reason.

    For example:

        >>> attrib_0 = Attribute(['foo']*13)
        >>> Validation = _is_valid_attribute(attrib_0)
        >>> Validation.Error_Reason
        "Unmatched type of Str, expected int but got str"
    """
    Return: Union[bool, Any]
    # Errors part
    Error_Key: Union[Any, str] = None
    Error_Value: Any = None
    Error_Reason: str = ""


class StaticTypingException(TypeError):
    """Type passed is missmatch with type hint."""


class InitializationFailed(RuntimeError):
    """Cannot initialized class."""


class FinalClassError(InitializationFailed):
    """Cannot subclass a final class."""


class _AbstractFileStructure:
    """Abstract file structure class.

    How to initialize:

     1. Subclass and fill path parameter with any folder name you want.
     2. add __new__ method
     3. Set any parameters you want.
     4. Re-define loader classmethod so that it will be supported to your class.
        Or, you can use global _AFS_loader function. (it'll fetch the struct_id, structure_folder and path, then read and convert it to dict)"""

    _correspondend_classes = {}

    def __new__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __init_subclass__(cls, path: str, final=True) -> None:
        cls._path = path
        cls._loaded_instances = []
        if final is True:
            def _n():
                raise FinalClassError("Cannot subclass a finalized class.")
            cls.__init_subclass__ = _n  # Finalizing instances.
        if not path in _AbstractFileStructure._correspondend_classes:
            _AbstractFileStructure._correspondend_classes[path] = cls
        else:
            raise Exception(
                f"{path} is already defined by {_AbstractFileStructure._correspondend_classes[path].__name__}")

    @classmethod
    def loader(cls, struct_id: str) -> Any:
        return cls(**_AFS_loader('', struct_id))

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self._name if hasattr(self, '_name') else None)

# source: http://docs.python.org/3/howto/descriptor.html
# if i'm not wrong... i use the offline docs
# offline docs: http://[IPv4]:[port]/howto/descriptor.html
#             : http://127.0.0.1:5000/howto/descriptor.html


class AbstractTypedValue(ABC):

    def __set_name__(self, owner, name):
        self.private_name = '_' + name

    def __get__(self, obj, objtype=None):
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        self.validate(value)
        setattr(obj, self.private_name, value)

    @abstractmethod
    def validate(self, value):
        pass


class Integer(AbstractTypedValue):
    def __init__(self, minvalue: int, maxvalue: int):
        if not isinstance(minvalue, int):
            raise TypeError("minvalue type must be int")
        if not isinstance(maxvalue, int):
            raise TypeError("maxvalue type must be int")
        if minvalue >= maxvalue:
            raise ValueError("minvalue must be less than maxvalue")
        self.minvalue = minvalue
        self.maxvalue = maxvalue

    def validate(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError(f'Expected {value!r} to be an int or float')
        if self.minvalue is not None and value < self.minvalue:
            raise ValueError(
                f'Expected {value!r} to be at least {self.minvalue!r}'
            )
        if self.maxvalue is not None and value > self.maxvalue:
            raise ValueError(
                f'Expected {value!r} to be no more than {self.maxvalue!r}'
            )


class String(AbstractTypedValue):
    def __init__(self):
        pass

    def validate(self, value):
        if not isinstance(value, str):
            raise TypeError(f"Expected {value!r} to be a str.")


class _EditableRepr:
    def __init__(self, string: str):
        self._string = string

    def __repr__(self):
        return self._string


class Maximum(_EditableRepr):
    def __init__(self):
        super().__init__("Max")

    def __add__(self, other: Any):
        return self

    def __sub__(self, other: Any):
        return self

    def __mul__(self, other: Any):
        return self

    def __div__(self, other: Any):
        return self


Max = Maximum()

# Internal functions


def max_exp(level: int, type_: Literal[0, 1, 2] = 0) -> Union[int, Maximum]:
    if type_ == 0:
        return (level*46)*level + randint(0, 30, 1)
    elif type_ == 1:
        if level == 5 or level >= 10:
            return Max
        return (level*200*17)*level + randint(0, 100, 1)
    elif type_ == 2:
        if level >= 10:
            return Max
        return (level*30)*level + randint(0, 60, 1)
    else:
        raise ValueError("type_ expected 0 or 1 or 2, got %s" % type_)


def setDebug(value: Any = None):
    global _debug_
    _debug_ = (not _debug_) if value is None else not not value


def _AFS_loader(path, struct_id) -> dict:
    f_path = join(structure_folder+path, struct_id.split('.'))
    id_path = f'{path}.{struct_id}'
    if not exists(f_path):
        raise FileNotFoundError(id_path)
    with open(f_path) as f:
        n = safe_load(f.read())
    if not isinstance(n, dict):
        raise TypeError("Expected dict type, got %s" % type(n))
    return n


def _is_valid_attribute(instance: Union['Attribute', 'FrozenAttribute']) -> ValidationReturn:
    for key, val in instance.__dict__.copy().items():
        if isinstance(val, NotAvailable.__class__):
            NotAvailableWarning.warn(key)
            if "Frozen" in instance.__class__.__name__:
                raise UnableToSetAttribute(
                    "Instance %s has frozen attribute or itself is frozen" % (instance.__class__.__name__))
            setattr(instance, key, 0)
            continue
        if not isinstance(val, int):
            return ValidationReturn(False, key, type(val), _default_unmatched_str % (key, "int", type(val).__name__))
    return ValidationReturn(True)


def _is_valid_comp_attribute(instance: Union['ComputationalAttribute', 'FrozenComputationalAttribute']) -> ValidationReturn:
    for key, val in instance.__dict__.copy().items():
        if isinstance(val, NotAvailable.__class__):
            NotAvailableWarning.warn(key)
            if "Frozen" in instance.__class__.__name__:
                raise UnableToSetAttribute(
                    "Instance %s has frozen attribute or itself is frozen" % (instance.__class__.__name__))
            setattr(instance, key, 0)
            continue
        if not isinstance(val, (int, float)):
            return ValidationReturn(False, key, type(val), _default_unmatched_str % (key, "int | float", type(val).__name__))
    return ValidationReturn(True)


def _is_valid_char_attribute(instance: Union['CharAttribute', 'FrozenCharAttribute']) -> ValidationReturn:
    for key, val in instance.__dict__.copy().items():
        if isinstance(val, NotAvailable.__class__):
            NotAvailableWarning.warn(key)
            if "Frozen" in instance.__class__.__name__:
                raise UnableToSetAttribute(
                    "Instance %s has frozen attribute or itself is frozen" % (instance.__class__.__name__))
            if key == "Race":
                setattr(instance, key, "Nothing")
            elif key == "Gender":
                setattr(instance, key, -1)
            elif key == 'Skills':
                setattr(instance, key, {})
            else:
                setattr(instance, key, 0)
            continue
        if key == "Race":
            if not isinstance(val, Race) and not isinstance(val, str) and not _debug_ is True:
                return ValidationReturn(False, key, type(val), _default_unmatched_str % (key, "Race | str", type(val).__name__))
        elif key == "Gender":
            if not isinstance(val, (int, str)):
                return ValidationReturn(False, key, type(val), _default_unmatched_str % (key, "int | str", type(val).__name__))
            if val < -1 or val > 3:
                return ValidationReturn(False, key, type(val), "The gender id is less than -1 or more than 3")
        elif not isinstance(val, (int, str, dict)):
            return ValidationReturn(False, key, type(val), _default_unmatched_str % (key, "int | str | dict", type(val).__name__))
        elif isinstance(val, dict):
            # Skills
            for key, val_ in val.items():
                if not isinstance(key, str) and isinstance(val_, str):
                    return ValidationReturn(False, key, type(val), _default_unmatched_str % (key, "str", type(val).__name__))
    return ValidationReturn(True)


def _is_valid_everything(instance1: Union['Attribute', 'FrozenAttribute'], instance2: Union['CharAttribute', 'FrozenAttribute'], instance3: Union['ComputationalAttribute', 'FrozenComputationalAttribute']) -> Iterable:
    n1 = _is_valid_attribute(instance1)
    n2 = _is_valid_comp_attribute(instance3)
    n3 = _is_valid_char_attribute(instance2)
    if sum((n1.Return, n2.Return, n3.Return)) != 3:
        return False, (n1, n2, n3)
    return True, (n1, n2, n3)


def _is_valid_for_base_character(instance1: Union['Attribute', 'FrozenAttribute'], instance2: Union['CharAttribute', 'FrozenAttribute']) -> Iterable[ValidationReturn]:
    n1 = _is_valid_attribute(instance1)
    n2 = _is_valid_char_attribute(instance2)
    if sum((n1.Return, n2.Return)) != 2:
        return False, (n1, n2)
    return True, (n1, n2)


def no_frozen(func):
    def wrapper(self, *args, **kwargs):
        if self._frozen is True:
            return False
        n = func(self, *args, **kwargs)
        return n
    wrapper.__name__ = func.__name__
    wrapper.__qualname__ = func.__qualname__
    return wrapper

# =================================================================


class Race(_AbstractFileStructure, path="races"):
    def __new__(cls, **kwargs) -> "Race":
        pass


class Item(_AbstractFileStructure, path="items"):
    def __new__(cls, **kwargs) -> 'Item':
        pass


class Magic(_AbstractFileStructure, path="magics"):
    def __new__(cls, **kwargs) -> 'Magic':
        pass


class Skill(_AbstractFileStructure, path="skills"):
    def __new__(cls, **kwargs) -> 'Skill':
        pass


# =================================================================

#                            Default

# =================================================================


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
    Bra: int


@dataclass(repr=True, eq=True, frozen=False, init=True)
class ComputationalAttribute:
    """Computational attribute"""
    Magical_Atk: int
    Magical_Def: int
    Critical_Percentage: Union[float, int]
    Evade_Percentage: Union[float, int]
    Atk: int
    Def: int
    Accuracy: Union[float, int]
    Speed_Acceleration: Union[float, int]
    Max_HealthPoint: int
    Max_MagicalPoint: int
    Usage_Acceleration: Union[float, int]
    Stamina_Point: int
    Resistance_Point: int
    Leadership_Point: int


@dataclass(repr=True, eq=True, frozen=False, init=True)
class CharAttribute:
    """Character Attribute"""
    Level: int
    EXP: int
    Magical_EXP: int
    Magical_Skill_EXP: int
    Magical_Level: int
    Magical_Skill_Level: int
    Name: str
    Race: 'Race'
    Age: int
    Skills: dict[str, str]
    Gender: Union[int, str]

# =================================================================

#                             Frozen

# =================================================================


@dataclass(repr=True, eq=True, frozen=True, init=True)
class FrozenAttribute:
    """Frozen Attribute class"""
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
    Bra: int


@dataclass(repr=True, eq=True, frozen=True, init=True)
class FrozenComputationalAttribute:
    """Frozen Computational attribute"""
    Magical_Atk: int
    Magical_Def: int
    Critical_Percentage: Union[float, int]
    Evade_Percentage: Union[float, int]
    Atk: int
    Def: int
    Accuracy: Union[float, int]
    Speed_Acceleration: Union[float, int]
    Max_HealthPoint: int
    Max_MagicalPoint: int
    Usage_Acceleration: Union[float, int]
    Stamina_Point: int
    Resistance_Point: int
    Leadership_Point: int


@dataclass(repr=True, eq=True, frozen=True, init=True)
class FrozenCharAttribute:
    """Frozen Character Attribute"""
    Level: int
    EXP: int
    Magical_EXP: int
    Magical_Skill_EXP: int
    Magical_Level: int
    Magical_Skill_Level: int
    Name: str
    Race: 'Race'
    Age: int
    Skills: dict[str, str]
    Gender: Union[int, str]


# =================================================================

class BaseCharacter:
    """Base class for character"""
    skill_enclosing_declose = '「 ', '」'

    def __init__(self, char_attribute: Union[CharAttribute, FrozenCharAttribute], attribute: Union[Attribute, FrozenAttribute]):
        if not isinstance(attribute, FrozenAttribute) and not isinstance(char_attribute, FrozenCharAttribute):
            isvalid = _is_valid_for_base_character(attribute, char_attribute)
            if not isvalid[0]:
                if isvalid[1][0].Error_Reason == '' and isvalid[1][1].Error_Reason == '':
                    raise StaticTypingException(
                        'Invalid attribute type. Perhaps you have put one of these attributes in wrong type. '
                        'Check your instances if they matched with type hints or not.')
                else:
                    e1 = isvalid[1][0].Error_Reason
                    e2 = isvalid[1][1].Error_Reason
                    if e1 != "" and e2 != "":
                        raise Exception(
                            f"{e1}\nAnother error also occurred:\n{e2}")
                    elif e1 == "":
                        raise Exception(e2)
                    elif e2 == "":
                        raise Exception(e1)
        self._name: str = char_attribute.Name
        self._char_attribute: Union[CharAttribute,
                                    FrozenCharAttribute] = char_attribute
        self._attribute: Union[Attribute, FrozenAttribute] = attribute
        self._comp_attribute: Union[ComputationalAttribute, FrozenComputationalAttribute] = ComputationalAttribute(*[0]*14) if not isinstance(
            attribute, FrozenAttribute) and not isinstance(char_attribute, FrozenCharAttribute) else FrozenComputationalAttribute(*[0]*14)
        self._frozen = False
        if isinstance(self._comp_attribute, FrozenComputationalAttribute):
            FrozenClassWarning.warn(2)
            self._frozen = True
        else:
            self.cls_calculate()
        self._MaxEXP = max_exp(self._char_attribute.Level)
        self._MaxMagicalEXP = max_exp(self._char_attribute.Magical_Level, 1)
        self._MaxSkillEXP = max_exp(
            self._char_attribute.Magical_Skill_Level, 2)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self._name} (Level {self._char_attribute.Level}){' (Frozen)' if self._frozen else ''}>"

    def dump(self, **options) -> str:
        """Dump the object into Yaml string. Dis-including Computational Attribute"""
        obj = self._char_attribute.__dict__.copy()
        obj.update(self._attribute.__dict__.copy())
        # trying to ignore VSCode's Python 'errors'.
        v = safe_dump(obj, **options)
        if isinstance(v, str):
            return v
        raise Exception("Failed to dump object: %s" % v)

    def dump_to_jsonable(self) -> tuple[dict]:
        """This method dumps all attributes defined in self. it returns a list, containing dicts. This method should return 3 stuffs."""
        a1 = self._attribute.__dict__.copy()
        a2 = self._char_attribute.__dict__.copy()
        a3 = self._comp_attribute.__dict__.copy()
        return a1, a2, a3

    def cls_calculate(self) -> NoReturn:
        if self._frozen:
            raise FrozenClassError(
                "Either CharAttribute or Attribute are/is a Frozen instance(s).")

        """\ 
        MaxHP    = ((Vit * 10) + (End * 3) + (Res * 2) + (Str * 1.4) / 15) * 10
        MaxMP    = ((Sta * 30) + (Will * 10) + (Wis * 3) / 10) * 1.3
        Crit%    = (((Str * 10) + (Sta * 5) + (Per * 1.2) + (Bra * 1.3) / 4) / 1.5) * 2 / 100 + (Luck / 3)
        Evade%   = (((Agi * 40) + (Dex * 20)) / 50) / 100
        Accura%  = N/A
        SpdAcc   = ((Agi * 20) + (Dex * 10)) / 400
        Atk      = ((Str * 60) + (Will * 1.5) + (Sta * 5)) / 59
        Def      = (((Vit * 40) + (End * 4.6) + (Res * 2.4) + (Str * 3.4)) / 60) * 2
        MagDef   = (MP + (Will * 10 + Wis * 2)) / 13
        MagAtk   = (MP + (Will * 10 + Wis * 2) + (Sta * 1.004)) / 13
        ResPTS   = N/A
        UsageAce = N/A
        Stamina  = Sta * 10
        LeadPTS  = (((Bra * 10) + (Wis * 2) + (Will * 1.3)) / 12) * 1.2
        """

        self._comp_attribute.Max_HealthPoint = (((self._atribute.Vit*10) + (
            self._atribute.End*3) + (self._atribute.Res*2) + (self._atribute.Str*1.4)) / 15) * 10
        self._comp_attribute.Max_MagicalPoint = (
            ((self._atribute.Sta*30) + (self._atribute.Will*10) + (self._atribute.Wis*3)) / 10) * 1.3
        self._comp_attribute.Critical_Percentage = (((self._atribute.Str*10) + (self._atribute.Sta*5) + (
            self._atribute.Per*1.2) + (self._atribute.Bra*1.3) / 4) / 1.5) * 2 / 100 + (self._atribute.Luck/3)
        self._comp_attribute.Evade_Percentage = (
            ((self._atribute.Agi*40) + (self._atribute.Dex*20)) / 50) / 100
        self._comp_attribute.Accuracy = NotAvailable
        self._comp_attribute.Speed_Acceleration = (
            (self._atribute.Agi*20) + (self._atribute.Dex*10)) / 400
        self._comp_attribute.Atk = (
            (self._atribute.Str*60) + (self._atribute.Will*1.5) + (self._atribute.Sta*5)) / 59
        self._comp_attribute.Def = (((self._atribute.Vit*40) + (self._atribute.End*4.6) + (
            self._atribute.Res*2.4) + (self._atribute.Str*3.4)) / 60) * 2
        self._comp_attribute.Magical_Def = (
            self._comp_attribute.MP + (self._atribute.Will*10 + self._atribute.Wis*2)) / 13
        self._comp_attribute.Magical_Atk = (self._comp_attribute.MP + (
            self._atribute.Will*10 + self._atribute.Wis*2) + (self._atribute.Sta*1.004)) / 13
        self._comp_attribute.Resistance_Point = NotAvailable
        self._comp_attribute.Usage_Acceleration = NotAvailable
        self._comp_attribute.Stamina_Point = self._atribute.Sta * 10
        self._comp_attribute.Leadership_Point = (((self._attribute.Bra * 10) + (
            self._attribute.Wis * 2) + (self._attribute.Will * 1.3)) / 12) * 1.2

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

        if not _is_valid_for_base_character(obj2, obj1):
            raise StaticTypingException(
                "Invalid attribute type. Perhaps you have put one of these attributes in wrong type. Check your Yaml object and try again.")

        return cls(obj1, obj2)

    @property
    def attribute(self):
        """Get the attribute, in frozen!"""
        return FrozenAttribute(**self._attribute.__dict__)

    @property
    def character_attribute(self):
        """Get the character attribute, in frozen!"""
        return FrozenCharAttribute(**self._character.__dict__)

    @property
    def computational(self):
        """Get the computational attribute, in frozen!"""
        return FrozenComputationalAttribute(**self._comp_attribute.__dict__)

    @no_frozen
    def level_up(self):
        self._char_attribute.Level += 1
        self._char_attribute.EXP = 0
        base_attr_name = ("Vit", "Str", "Sta", "Res", "Wis",
                          "Will", "End", "Dex", 'Agi', 'Int', "Per")
        for name in base_attr_name:
            setattr(self._attribute, name,
                    self._attribute[name] + randint(1, 5))

        self._MaxEXP = max_exp(self._char_attribute.Level)
        self.cls_calculate()
    
    @no_frozen
    def when_exp_eq_mexp(self):
        while self._char_attribute.EXP >= self._MaxEXP:
            self._char_attribute.Level += 1
            self._char_attribute.EXP -= self._MaxEXP
            base_attr_name = ("Vit", "Str", "Sta", "Res", "Wis",
                          "Will", "End", "Dex", 'Agi', 'Int', "Per")
            for name in base_attr_name:
                setattr(self._attribute, name,
                    self._attribute[name] + randint(1, 5))

            self._MaxEXP = max_exp(self._char_attribute.Level)
            self.cls_calculate()


# Instance initializations?


NotAvailable = NotAvailable()

__all__ = [
    "ValidationReturn", "AbstractTypedValue", "Integer", "String", "setDebug", "Race", "Item", "Magic",
    "Skill", "Attribute", "ComputationalAttribute", "CharAttribute", "FrozenComputationalAttribute",
    "FrozenAttribute", "FrozenCharAttribute", "BaseCharacter", "NotAvailable"
]
