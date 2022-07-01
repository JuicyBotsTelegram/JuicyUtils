from __future__ import annotations

import re
from typing import Optional


class TimeTransformator:
    """
    How to use:
    t = TimeTransformator("s", "m", "h", "d", "y")
    t.toStringTime(123132)
    # prints '1d 10h 12m 12s'

    # And vice versa:
    t.fromStringToTimeInSeconds('1d 10h 12m 12s')
    # prints 123132
    # So it returns the seconds parsed from string
    # Another example:
    t.fromStringToTimeInSeconds('1d 10h')
    # prints 122400
    """
    class __Tick:
        def __init__(self, tic_in_seconds: int, symbol: str):
            self.__tic_in_seconds = tic_in_seconds
            self.__raw_symbol = symbol

        @property
        def ticInSeconds(self):
            return self.__tic_in_seconds

        @property
        def rawSymbol(self):
            return self.__raw_symbol

        @property
        def symbol(self):
            return "{0:_}" + self.rawSymbol + " "

    SECONDS_UNIT: int = 1
    MINUTES_UNIT: int = 60 * SECONDS_UNIT
    HOURS_UNIT: int = 60 * MINUTES_UNIT
    DAYS_UNIT: int = 24 * HOURS_UNIT
    YEARS_UNIT: int = int(365.25 * DAYS_UNIT)

    def __init__(
            self,
            symbol_seconds: str,
            symbol_minutes: Optional[str] = None,
            symbol_hours: Optional[str] = None,
            symbol_days: Optional[str] = None,
            symbol_years: Optional[str] = None
    ):
        self.__tics = list()
        self.__tics.append(self.__Tick(self.SECONDS_UNIT, symbol_seconds))
        if symbol_minutes is not None:
            self.__tics.append(self.__Tick(self.MINUTES_UNIT, symbol_minutes))
        if symbol_hours is not None:
            self.__tics.append(self.__Tick(self.HOURS_UNIT, symbol_hours))
        if symbol_days is not None:
            self.__tics.append(self.__Tick(self.DAYS_UNIT, symbol_days))
        if symbol_years is not None:
            self.__tics.append(self.__Tick(self.YEARS_UNIT, symbol_years))

        self.__set_regex_according_to_tics()

    def __set_regex_according_to_tics(self):
        all_symbols = "".join(i.rawSymbol for i in self.__tics)
        self.__regex = re.compile(f'[_\d]+?\s?[{all_symbols}]', re.I)

    @property
    def __allowed_tics_count(self) -> int:
        return len(self.__tics) - 1

    def toStringTime(self, time_in_seconds: int) -> str:
        """
        Usually this function is used to calculate the time left to another time in future.
        In such case u have current time minus time in future
        """
        return self.__toStringTime(time_in_seconds, self.__allowed_tics_count).strip()

    def fromStringToTimeInSeconds(self, string_representative_of_time: str) -> int:
        return self.__fromStringToTimeInSeconds(string_representative_of_time, True)

    def __fromStringToTimeInSeconds(self, string_or_splitted_time_parts: str | list[str],  analiz_firstly: bool) -> int:
        if analiz_firstly and isinstance(string_or_splitted_time_parts, str):
            string_or_splitted_time_parts = string_or_splitted_time_parts.replace("_", "")
            splitted_time_parts = self.__regex.findall(string_or_splitted_time_parts)
            return self.__fromStringToTimeInSeconds(splitted_time_parts, False)
        time_in_seconds = 0
        if string_or_splitted_time_parts and isinstance(string_or_splitted_time_parts, list):
            for item in string_or_splitted_time_parts:
                item = item.lower().replace("_", "")
                for tic in self.__tics:
                    if tic.rawSymbol in item:
                        found_digits = self.__check_digit(item[:item.find(tic.rawSymbol)].strip())
                        time_in_seconds += tic.ticInSeconds * found_digits
        return time_in_seconds

    def __toStringTime(self, time_in_seconds: int, iteration: int) -> str:
        if iteration <= 0:
            return self.__tics[0].symbol.format(time_in_seconds) if time_in_seconds != 0 else ''
        i = min(iteration, self.__allowed_tics_count)
        dm = divmod(abs(time_in_seconds), self.__tics[i].ticInSeconds)
        return (self.__tics[i].symbol.format(dm[0]) if dm[0] != 0 else '') + self.__toStringTime(dm[1], i - 1)

    @classmethod
    def __check_digit(cls, str_int: str) -> int:
        if str_int.isdigit():
            return int(str_int)
        return 0