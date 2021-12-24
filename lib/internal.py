"""internal"""

# TODO: Add StaticTypesNamedTuple and StaticTypesNamespace.
# by looking at Python's typing.py about NamedTuple, then implement runtime type checking at initialization level (when __init__ is called)
# and for StaticTypesNamespace, type checking will be implemented in initialization and at __setattr__ level
# for example, raising an error if:
# namespace = StaticTypesNamespace()
# namespace.foo = 'bar'  # string type
# namespace.foo = 1      # int type
# > TypeError: foo is not a instance of str.
# But this type checking can be bypassed using set_attr(namespace, 'foo', int, 1)

from warnings import warn

warn("Internal module didn't have anything for now.")

del warn
