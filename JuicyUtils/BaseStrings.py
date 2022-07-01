from __future__ import annotations


class BaseStrings:
    def __init__(self, language: str):
        self.__language = language

    @property
    def lang(self) -> str:
        return self.__language

