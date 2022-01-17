"""internal"""

from random import Random, randint as _randint
from secrets import SystemRandom

# TODO: Add StaticTypesNamedTuple and StaticTypesNamespace.
# by looking at Python's typing.py about NamedTuple, then implement runtime type checking at initialization level (when __init__ is called)
# and for StaticTypesNamespace, type checking will be implemented in initialization and at __setattr__ level
# for example, raising an error if:
# namespace = StaticTypesNamespace()
# namespace.foo = 'bar'  # string type
# namespace.foo = 1      # int type
# > TypeError: foo is not a instance of str.
# But this type checking can be bypassed using set_attr(namespace, 'foo', int, 1)

_Module_Seed = _randint(0, 99999)

class StaticNamespace:
    """Readonly namespace"""
    def __new__(cls, **kwargs):
        new = object.__new__(cls)
        new._flag = False
        for key,val in kwargs.items():
            setattr(new, key, val)
        new._flag = True
        return new

    def __setattr__(self, name, value):
        if not hasattr(self, "_flag"):
            object.__setattr__(self, name, value)
            return
        if self._flag is True:
            return
        object.__setattr__(self, name, value)

    def __repr__(self):
        return "<StaticNamespace>"

class Struct:
    """Change-able attributes but without new additions. (and with matching type.)"""
    pass
# TODO: define __setattr__ that checks type of instances. (but if the thing is using typing's stuff. raise StructException )

def randint(minvalue: int, maxvalue: int, loops: int=5):
    if not isinstance(minvalue, int) and not isinstance(maxvalue, int):
        raise TypeError("Both minvalue or maxvalue must be integer")
    
    ret = 0
    while loops > 0:
        n = Random.randint(0, 100)
        if n >= 50:
            ret = SystemRandom(Random(_Module_Seed).randint(0, 99999)).randint(minvalue, maxvalue)
        if n < 50:
            ret = Random(SystemRandom(_Module_Seed).randint(0, 99999)).randint(minvalue, maxvalue)
        loops -= 1
    return ret
