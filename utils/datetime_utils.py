import jdatetime
from datetime import datetime


def now_iso():
    return datetime.now()


def iso_to_persian(iso_dt: datetime):
    dt = jdatetime.datetime.fromgregorian(datetime=iso_dt)
    weekdays = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه", "شنبه", "یکشنبه"]
    months = [
        "فروردین",
        "اردیبهشت",
        "خرداد",
        "تیر",
        "مرداد",
        "شهریور",
        "مهر",
        "آبان",
        "آذر",
        "دی",
        "بهمن",
        "اسفند",
    ]
    weekday_name = weekdays[dt.weekday()]
    month_name = months[dt.month - 1]
    return f"{weekday_name} {dt.day} {month_name} {dt.year} - {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"
