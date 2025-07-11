# Persian Jalali Calendar

A simple, accurate, and lightweight Python library for the Persian (Jalali/Shamsi) calendar, now with timezone support and no external dependencies for core functionality (requires `tzdata` for timezones).

This library allows for easy conversion between Jalali and Gregorian dates, provides date arithmetic, and offers helpful methods for formatting and date information, all through an intuitive API modeled after Python's built-in `datetime` module.

## Installation

Install the library from PyPI using pip. This will automatically handle dependencies.

```bash
pip install persian-jalali-calendar
```

## In-Depth Usage

### `JalaliDate` - The Core Date Object

The `JalaliDate` object is for working with calendar dates.

```python
from jalali_calendar import JalaliDate
import datetime

# --- Creation ---
# From year, month, and day
d = JalaliDate(1404, 4, 13)

# From today's system date
today = JalaliDate.today()

# From a standard Python datetime.date object
g_date = datetime.date(2025, 7, 4)
j_date = JalaliDate.from_gregorian(g_date)

# From a formatted string using strptime
parsed_date = JalaliDate.strptime("15 تیر 1404", "%d %B %Y")
# parsed_date is now JalaliDate(1404, 4, 15)
```

### Conversion & Properties

Seamlessly convert and access date information.

```python
# Convert to a Gregorian datetime.date object
g_date = j_date.to_gregorian() # -> datetime.date(2025, 7, 4)

# Access properties
print(f"Year: {j_date.year}, Month: {j_date.month_name()}, Day: {j_date.day}")
# -> Year: 1404, Month: تیر, Day: 4

# Weekday (Saturday=0, Friday=6)
print(f"Weekday Number: {j_date.weekday()}") # -> 5
print(f"Weekday Name: {j_date.weekday_name()}") # -> پنج‌شنبه
```

### Date Arithmetic

Perform calendar-aware arithmetic.

```python
from datetime import timedelta

date = JalaliDate(1403, 1, 15)

# Add/subtract days
new_date_days = date + timedelta(days=20) # -> 1403-02-04

# NEW: Add/subtract months (handles different month lengths)
new_date_months = date.add_months(2) # -> 1403-03-15

# NEW: Add/subtract years (handles leap years correctly)
leap_day = JalaliDate(1403, 12, 30)
non_leap_year = leap_day.add_years(1) # -> 1404-12-29 (clamped)
```

### `JalaliDateTime` - For Date & Time

The `JalaliDateTime` object handles specific moments in time.

```python
from jalali_calendar import JalaliDateTime
from jalali_calendar.timezone import ZoneInfo

# --- Creation ---
dt_naive = JalaliDateTime(1404, 5, 3, 15, 30, 0)
dt_aware = JalaliDateTime(1404, 5, 3, 15, 30, 0, tzinfo=ZoneInfo("Asia/Tehran"))

# From current system time
now_local = JalaliDateTime.now()
now_utc = JalaliDateTime.now(tz=ZoneInfo("UTC"))
```

### Timezone Conversions

Effortlessly convert between timezones.

```python
tehran_time = JalaliDateTime(1403, 1, 1, 15, 30, 0, tzinfo=ZoneInfo("Asia/Tehran"))

# Convert to a different timezone
tokyo_time = tehran_time.astimezone(ZoneInfo("Asia/Tokyo"))
print(f"{tehran_time} is {tokyo_time}")
# -> 1403-01-01 15:30:00+0330 is 1403-01-01 21:00:00+0900
```

### Formatting with `strftime`

Create custom-formatted strings with extensive options.

```python
dt = JalaliDateTime(1403, 5, 10, 15, 45, 5)

# Standard formatting
dt.strftime("%A، %d %B %Y - %H:%M:%S")
# -> 'پنج‌شنبه، ۱۰ مرداد ۱۴۰۳ - 15:45:05'

# 12-hour format with AM/PM
dt.strftime("%I:%M %p") # -> '03:45 ب.ظ'

# Timezone formatting
aware_dt = JalaliDateTime.now(ZoneInfo("Asia/Tehran"))
aware_dt.strftime("%Y/%m/%d %H:%M %Z%z")
# -> '1403/04/18 10:30 IRST+0330' (example output)
```

## License

This project is licensed under the MIT License.