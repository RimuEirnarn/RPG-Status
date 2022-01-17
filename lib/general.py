from typing import Iterable, Any, Callable

default = object()


class DuplicationError(Exception):
    """An objet have a duplicate values/names."""


class SwitchCaseError(Exception):
    """Failed to do an operation. Undefined key."""

class Call:
    def __init__(self, primary: Callable, *args, **kwargs):
        self._primary = primary
        self._args = args
        self._kwargs = kwargs
    
    def __call__(self) -> Any:
        return self._primary(*self._args, **self._kwargs)


class Switch:
    def __init__(self, case: dict[str, Iterable[Any]], err_reason: str=None):
        self._case = case
        self._err_reason = err_reason if err_reason else "%s does not exists."
        if len(case) == 0:
            raise ValueError("Switch atleast require 1 case.")
        
        default_flag = False # True if default has been called.
        for ck in tuple(self._case.keys()):
            if ck == default and default_flag is False:
                default_flag = True
            elif ck == default and default_flag is True:
                raise DuplicationError("Unexpected duplicate default case.")
    
    def do(self, value: Any = default) -> Any:
        for ck, cv in self._case.items():
            if ck == value:
                if isinstance(cv, Call):
                    return cv()
                elif callable(cv):
                    return cv()
                else:
                    return cv
        
        if value not in self._case:
            raise SwitchCaseError(self._err_reason % value)
