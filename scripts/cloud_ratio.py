#!/usr/bin/env python3
"""Single source of truth for upstream ratio parsing/formatting.

Both compose_report.py and cloud_content_review.py import these functions so
explicit percent strings stay byte-for-byte and numeric ratios are never
rounded or zero-padded.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Optional


def source_ratio_percent(value: Any, *, already_percent: bool = False) -> Optional[Decimal]:
    """Return a percentage as Decimal without rounding; None when unavailable.

    Accepts a 0-1 fraction, an already-percent number, a '12.3456%' string,
    or a dict. Zero is a real value; only missing/invalid input returns None.
    already_percent marks report fields whose declared unit is percentage points.
    """
    if isinstance(value, dict):
        value = value.get("value", value.get("ratio", value.get("percent")))
    if value is None or isinstance(value, bool):
        return None
    text = str(value).strip()
    if not text or text in {"-", "—"}:
        return None
    had_percent = "%" in text
    if had_percent:
        text = text.replace("%", "").strip()
    try:
        number = Decimal(text)
    except InvalidOperation:
        return None
    if not (had_percent or already_percent) and number != 0 and abs(number) <= 1:
        number *= 100
    return number


def format_source_ratio(value: Any, *, already_percent: bool = False) -> str:
    """Render an upstream ratio without rounding, zero-padding, or unit guessing.

    A percent string such as '12.3400%' is returned verbatim. Numeric 0-1
    fractions keep their original significant digits (0.123456 -> 12.3456%).
    Zero renders as '0%'; missing or invalid values render as '-'.
    """
    if isinstance(value, dict):
        value = value.get("value", value.get("ratio", value.get("percent")))
    if value is None:
        return "-"
    text = str(value).strip()
    if not text or text in {"-", "—"}:
        return "-"
    if "%" in text:
        return text
    number = source_ratio_percent(value, already_percent=already_percent)
    if number is None:
        return text
    return f"{format(number.normalize(), 'f')}%"
