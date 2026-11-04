from datetime import date

from dgc.dates import find_due, parse_date

REF = date(2026, 10, 28)  # a Wednesday


def test_iso():
    assert parse_date("by 2026-10-30", REF) == date(2026, 10, 30)


def test_day_month_and_month_day():
    assert parse_date("5 Nov", REF) == date(2026, 11, 5)
    assert parse_date("Nov 6", REF) == date(2026, 11, 6)


def test_weekday_is_next_occurrence_on_or_after_reference():
    assert parse_date("Fri", REF) == date(2026, 10, 30)
    assert parse_date("Wed", REF) == REF


def test_year_rollover():
    assert parse_date("5 Jan", date(2026, 12, 20)) == date(2027, 1, 5)


def test_find_due_returns_phrase_start():
    d, start = find_due("send SOW by Fri", REF)
    assert d == date(2026, 10, 30) and "send SOW " == "send SOW by Fri"[:start]


def test_no_false_positive_on_plain_words():
    assert parse_date("monitor the month", REF) is None
