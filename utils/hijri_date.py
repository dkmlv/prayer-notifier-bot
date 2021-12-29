"""This module is only responsible for returning today's hijri date."""

from hijri_converter import Hijri


def get_todays_hijri_date():
    """Return today's hijri date."""
    hijri_obj = Hijri.today()

    h_day = hijri_obj.day
    h_month = hijri_obj.month_name("en")
    h_year = hijri_obj.year
    h_notation = hijri_obj.notation("en")

    hijri_date = f"<b>{h_day} {h_month} {h_year} {h_notation}</b>\n"

    return hijri_date
