import datetime
import re
from .date import JalaliDate, PERSIAN_MONTH_NAMES

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo


class JalaliDateTime:
    """
    An object representing a specific point in time (date and time)
    in the Jalali calendar. Can be 'aware' or 'naive' of timezones.
    """
    def __init__(self, year, month, day, hour=0, minute=0, second=0, tzinfo=None):
        self._date = JalaliDate(year, month, day)
        if not (0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
            raise ValueError("Time component is out of range.")
        if tzinfo is not None and not isinstance(tzinfo, datetime.tzinfo):
            raise TypeError("tzinfo argument must be a tzinfo subclass.")
        self._time = datetime.time(hour, minute, second)
        self._tzinfo = tzinfo

    @property
    def year(self): return self._date.year
    @property
    def month(self): return self._date.month
    @property
    def day(self): return self._date.day
    @property
    def hour(self): return self._time.hour
    @property
    def minute(self): return self._time.minute
    @property
    def second(self): return self._time.second
    @property
    def tzinfo(self): return self._tzinfo

    def date(self) -> JalaliDate:
        return self._date

    def time(self) -> datetime.time:
        return self._time

    def to_12h(self) -> tuple[int, str]:
        h = self.hour
        period = "ب.ظ" if 12 <= h < 24 else "ق.ظ"
        if h == 0:
            h12 = 12
        elif 1 <= h <= 12:
            h12 = h
        else:
            h12 = h - 12
        return h12, period

    def __repr__(self) -> str:
        if self._tzinfo:
            return (
                f"JalaliDateTime({self.year}, {self.month}, {self.day}, "
                f"{self.hour}, {self.minute}, {self.second}, tzinfo={self._tzinfo!r})"
            )
        return (
            f"JalaliDateTime({self.year}, {self.month}, {self.day}, "
            f"{self.hour}, {self.minute}, {self.second})"
        )

    def __str__(self) -> str:
        s = f"{self._date} {self._time}"
        if self._tzinfo:
            g_dt = self.to_gregorian()
            tz_str = g_dt.strftime('%Z')
            if tz_str:
                s += ' ' + tz_str
        return s

    def strftime(self, fmt: str) -> str:
        date_formatted = self._date.strftime(fmt)
        h12, period = self.to_12h()
        time_formatted = date_formatted.replace('%H', f"{self.hour:02d}") \
                                       .replace('%M', f"{self.minute:02d}") \
                                       .replace('%S', f"{self.second:02d}") \
                                       .replace('%I', f"{h12:02d}") \
                                       .replace('%p', period)
        
        if self._tzinfo and ('%z' in fmt or '%Z' in fmt):
            g_dt = self.to_gregorian()
            time_formatted = time_formatted.replace('%z', g_dt.strftime('%z'))
            time_formatted = time_formatted.replace('%Z', g_dt.strftime('%Z'))
            
        return time_formatted


    @classmethod
    def now(cls, tz=None):
        if tz is not None and not isinstance(tz, datetime.tzinfo):
            raise TypeError("tz argument must be a tzinfo subclass.")
        g_now = datetime.datetime.now(tz)
        j_date = JalaliDate.from_gregorian(g_now.date())
        return cls(j_date.year, j_date.month, j_date.day,
                   g_now.hour, g_now.minute, g_now.second,
                   tzinfo=g_now.tzinfo)

    @classmethod
    def combine(cls, date: JalaliDate, time: datetime.time, tzinfo=None):
        if not isinstance(date, JalaliDate) or not isinstance(time, datetime.time):
            raise TypeError("Invalid types for date or time.")
        return cls(date.year, date.month, date.day, time.hour, time.minute, time.second, tzinfo=tzinfo)

    @classmethod
    def from_12h(cls, date: JalaliDate, hour: int, minute: int, second: int, period: str, tzinfo=None):
        if not (1 <= hour <= 12):
            raise ValueError("Hour must be between 1 and 12 for 12-hour format.")
        if period not in ("ق.ظ", "ب.ظ"):
            raise ValueError("Period must be 'ق.ظ' or 'ب.ظ'.")
        h24 = hour
        if period == "ق.ظ" and hour == 12:
            h24 = 0
        elif period == "ب.ظ" and hour != 12:
            h24 += 12
        time_part = datetime.time(h24, minute, second)
        return cls.combine(date, time_part, tzinfo=tzinfo)

    def to_gregorian(self) -> datetime.datetime:
        g_year, g_month, g_day = self._date.to_gregorian().timetuple()[:3]
        return datetime.datetime(
            g_year, g_month, g_day, self.hour,
            self.minute, self.second, tzinfo=self._tzinfo
        )

    def astimezone(self, tz=None):
        if self._tzinfo is None:
            raise ValueError("astimezone() cannot be applied to a naive datetime.")
        g_dt = self.to_gregorian()
        g_dt_new_tz = g_dt.astimezone(tz)
        new_j_date = JalaliDate.from_gregorian(g_dt_new_tz.date())
        return self.__class__(
            new_j_date.year, new_j_date.month, new_j_date.day,
            g_dt_new_tz.hour, g_dt_new_tz.minute, g_dt_new_tz.second,
            tzinfo=g_dt_new_tz.tzinfo
        )

    @classmethod
    def strptime(cls, datetime_string: str, fmt: str):
        format_map = {
            '%H': r'(?P<H>\d{1,2})', '%I': r'(?P<I>\d{1,2})',
            '%M': r'(?P<M>\d{1,2})', '%S': r'(?P<S>\d{1,2})',
            '%p': r'(?P<p>[\u0600-\u06FF\.]+|[APM\.]{2,})',
        }
        date_format_map = {
            '%Y': r'(?P<Y>\d{4})', '%y': r'(?P<y>\d{2})', '%m': r'(?P<m>\d{1,2})',
            '%-m': r'(?P<m>\d{1,2})', '%d': r'(?P<d>\d{1,2})', '%-d': r'(?P<d>\d{1,2})',
            '%B': r'(?P<B>[\u0600-\u06FF\s]+)',
        }
        full_format_map = {**date_format_map, **format_map}
        pattern = fmt
        for code, regex in full_format_map.items():
            pattern = pattern.replace(code, regex)

        match = re.match(pattern, datetime_string)
        if not match:
            raise ValueError(f"Datetime string '{datetime_string}' does not match format '{fmt}'")

        data = match.groupdict()
        year = int(data.get('Y') or f"13{data.get('y')}")
        day = int(data.get('d'))
        month_str = data.get('m')
        if month_str:
            month = int(month_str)
        else:
            month_name = data.get('B').strip()
            month = PERSIAN_MONTH_NAMES.index(month_name)

        hour_24 = data.get('H')
        hour_12 = data.get('I')
        minute = int(data.get('M', 0))
        second = int(data.get('S', 0))
        period = (data.get('p') or '').strip().replace('.', '')
        if hour_12:
            hour = int(hour_12)
            if (period in ('بظ', 'PM')) and hour != 12:
                hour += 12
            elif (period in ('قظ', 'AM')) and hour == 12:
                hour = 0
        else:
            hour = int(hour_24 or 0)
        return cls(year, month, day, hour, minute, second)