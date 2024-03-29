from __future__ import annotations

from typing import TypeVar, Generic, Dict

from JuicyUtils.BaseStrings import BaseStrings

TBaseStrings = TypeVar("TBaseStrings", bound=BaseStrings)


class BaseLocale(Generic[TBaseStrings]):
    '''
    Example of use:

    # Creating new Strings-class base class with parent BaseStrings as it is required for BaseLocale
    class CarmaStrings(BaseStrings):
        HELLO_WORLD: str

    # Creating RU implementation of CarmaStrings
    class RUCarmaStrings(CarmaStrings):
        # some overrides of fields
        HELLO_WORLD = "Привет, мир!"

    # Creating EN implementation of CarmaStrings
    class ENCarmaStrings(CarmaStrings):
        # some overrides of fields
        HELLO_WORLD = "Hello, World!"

    # Creating holder class of CarmaStrings
    class CarmaLocale(BaseLocale):
        @property
        def EN(self) -> CarmaStrings: return self.LANG("en")

        @property
        def RU(self) -> CarmaStrings: return self.LANG("ru")

    # Creating an object of holder and adding RU an EN implementations of CarmaStrings
    locale = CarmaLocale()
    # Some more steps to add languages
    locale.add_language_from_strings(RUCarmaStrings("ru"))
    locale.add_language_from_strings(ENCarmaStrings("en"))

    print(locale.EN.HELLO_WORLD) # Will print "Hello, World!"
    print(locale.RU.HELLO_WORLD) # Will print "Привет, мир!"
    '''


    _lang_en = "EN"
    _lang_ru = "RU"

    _default_lang = _lang_ru

    def __init__(self, def_lang: str = _default_lang):
        self._default_lang: str = def_lang
        self._loaded_strings: Dict[str, TBaseStrings] = dict()

    def LANG(self, lang: str = _default_lang) -> TBaseStrings | None:
        if self._loaded_strings.__contains__(lang):
            return self._loaded_strings.get(lang)
        return self._loaded_strings.get(self._default_lang, None)

    def add_language_from_strings(self, strings: TBaseStrings) -> None:
        self._loaded_strings[strings.lang] = strings

