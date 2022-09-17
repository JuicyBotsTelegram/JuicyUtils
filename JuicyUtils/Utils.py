from __future__ import annotations

from typing import TypeVar, Iterable


def isTypeOf(__obj: object, class_or_tuple_or_typevar: type | TypeVar | Iterable[type | TypeVar]) -> bool:
    """
    :param __obj: Any object
    :param class_or_tuple_or_typevar: the type or list of types which will be compared with the __obj object
    :return: returns the boolean if object is instance of one of given types.

    This method extends base isinstance method, 'cause it supports TypeVars
    to check the object inherits the bound or constraints of TypeVar.
    """
    if isinstance(class_or_tuple_or_typevar, TypeVar):
        if class_or_tuple_or_typevar.__bound__ is not None:
            return isinstance(__obj, class_or_tuple_or_typevar.__bound__)
        elif class_or_tuple_or_typevar.__constraints__.__len__() != 0:
            return isinstance(__obj, class_or_tuple_or_typevar.__constraints__)

    if isinstance(class_or_tuple_or_typevar, Iterable):
        for _type in class_or_tuple_or_typevar:
            if isTypeOf(__obj, _type):
                return True
        return False
    return isinstance(__obj, class_or_tuple_or_typevar)