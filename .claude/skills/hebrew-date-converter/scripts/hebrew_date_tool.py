#!/usr/bin/env python3
"""
hebrew_date_tool.py - deterministic Hebrew calendar operations.

Subcommands:
  convert  : Gregorian <-> Hebrew date conversion
  omer     : returns sefirat ha'omer day number for a Gregorian date
  parsha   : returns the parsha for the Shabbos on or after a given date
  yahrzeit : computes future yahrzeit Gregorian dates from a Hebrew date of death

All output is JSON for the agent to parse.
Requires: pyluach (pip install pyluach)
"""

import argparse
import json
import sys
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    from pyluach import dates, parshios
except ImportError:
    print(json.dumps({"error": "pyluach not installed. Run: pip install pyluach"}))
    sys.exit(1)


HEBREW_MONTHS = {
    1: "Nisan", 2: "Iyar", 3: "Sivan", 4: "Tammuz",
    5: "Av", 6: "Elul", 7: "Tishrei", 8: "Cheshvan",
    9: "Kislev", 10: "Tevet", 11: "Shevat", 12: "Adar",
    13: "Adar II",
}


def parse_greg(s):
    parts = s.split("-")
    if len(parts) != 3:
        raise ValueError(f"Invalid Gregorian date '{s}'. Use YYYY-MM-DD.")
    y, m, d = (int(p) for p in parts)
    return dates.GregorianDate(y, m, d)


def parse_heb(s):
    parts = s.split("-")
    if len(parts) != 3:
        raise ValueError(
            f"Invalid Hebrew date '{s}'. Use YYYY-MM-DD where month is 1=Nisan..13=Adar II."
        )
    y, m, d = (int(p) for p in parts)
    return dates.HebrewDate(y, m, d)


def heb_label(hd):
    return f"{hd.day} {HEBREW_MONTHS.get(hd.month, str(hd.month))} {hd.year}"


def cmd_convert(args):
    if args.to == "hebrew":
        gd = parse_greg(args.date)
        hd = gd.to_heb()
        return {
            "input_gregorian": args.date,
            "hebrew_year": hd.year,
            "hebrew_month_number": hd.month,
            "hebrew_month_name": HEBREW_MONTHS.get(hd.month),
            "hebrew_day": hd.day,
            "hebrew_date_string": heb_label(hd),
            "hebrew_date_native": hd.hebrew_date_string(),
            "weekday": gd.to_pydate().strftime("%A"),
        }
    else:
        hd = parse_heb(args.date)
        gd = hd.to_greg()
        py = gd.to_pydate()
        return {
            "input_hebrew": args.date,
            "hebrew_date_string": heb_label(hd),
            "hebrew_date_native": hd.hebrew_date_string(),
            "gregorian_date": py.isoformat(),
            "weekday": py.strftime("%A"),
        }


def cmd_omer(args):
    gd = parse_greg(args.date)
    hd = gd.to_heb()

    candidate_year = hd.year
    omer_start = dates.HebrewDate(candidate_year, 1, 16)
    if hd < omer_start:
        omer_start = dates.HebrewDate(candidate_year - 1, 1, 16)

    diff = hd - omer_start
    omer = diff + 1

    if not (1 <= omer <= 49):
        return {
            "gregorian_date": args.date,
            "hebrew_date": heb_label(hd),
            "is_omer": False,
            "message": "This date is not during sefirat ha'omer (16 Nisan through 5 Sivan).",
        }

    weeks = omer // 7
    extra = omer % 7
    if extra == 0:
        formatted = f"Day {omer} of the Omer ({weeks} week{'s' if weeks != 1 else ''})"
    else:
        formatted = (
            f"Day {omer} of the Omer ({weeks} week{'s' if weeks != 1 else ''} "
            f"and {extra} day{'s' if extra != 1 else ''})"
        )

    return {
        "gregorian_date": args.date,
        "hebrew_date": heb_label(hd),
        "is_omer": True,
        "omer_day": omer,
        "weeks": weeks,
        "days_into_week": extra,
        "formatted": formatted,
    }


def cmd_parsha(args):
    gd = parse_greg(args.date)
    hd = gd.to_heb()
    parsha = parshios.getparsha_string(hd, israel=args.israel)
    shabbos = hd.shabbos()
    shabbos_greg = shabbos.to_greg().to_pydate()
    return {
        "gregorian_date": args.date,
        "hebrew_date": heb_label(hd),
        "shabbos_gregorian_date": shabbos_greg.isoformat(),
        "shabbos_hebrew_date": heb_label(shabbos),
        "israel_schedule": args.israel,
        "parsha": parsha if parsha else "No parsha (yom tov week or no Torah reading scheduled).",
    }


def cmd_yahrzeit(args):
    hd = parse_heb(args.hebrew_date)
    n = max(1, args.years)

    halachic_warning = None
    if hd.day == 30 and hd.month in (8, 9):
        halachic_warning = (
            f"Date of death is 30 {HEBREW_MONTHS[hd.month]}, which does not exist "
            "in every Hebrew year. Halachic practice on which day to observe the "
            "yahrzeit in short years varies by community - please consult your rabbi."
        )
    if hd.month in (12, 13):
        halachic_warning = (
            "Date of death falls in Adar. In Hebrew leap years there are two months "
            "of Adar (Adar I and Adar II), and halachic practice on which to observe "
            "the yahrzeit varies by tradition. Please consult your rabbi."
        )

    upcoming = []
    year = hd.year + 1
    cap = year + n * 4
    while len(upcoming) < n and year < cap:
        try:
            ny = hd.replace(year=year)
            gy = ny.to_greg().to_pydate()
            upcoming.append({
                "yahrzeit_hebrew_year": ny.year,
                "yahrzeit_hebrew_date": heb_label(ny),
                "yahrzeit_gregorian_date": gy.isoformat(),
                "weekday": gy.strftime("%A"),
            })
        except ValueError:
            upcoming.append({
                "yahrzeit_hebrew_year": year,
                "note": (
                    f"{hd.day} {HEBREW_MONTHS.get(hd.month)} does not exist in "
                    f"Hebrew year {year}; consult your rabbi for observance date."
                ),
            })
        year += 1

    out = {
        "death_hebrew_date": heb_label(hd),
        "upcoming_yahrzeits": upcoming,
    }
    if halachic_warning:
        out["halachic_warning"] = halachic_warning
    return out


def main():
    p = argparse.ArgumentParser(description="Hebrew calendar operations (deterministic).")
    sub = p.add_subparsers(dest="cmd", required=True)

    pc = sub.add_parser("convert", help="Convert between Gregorian and Hebrew dates.")
    pc.add_argument("--date", required=True, help="Date string YYYY-MM-DD.")
    pc.add_argument("--to", choices=["hebrew", "gregorian"], default="hebrew",
                    help="Direction of conversion (default: hebrew).")

    po = sub.add_parser("omer", help="Sefirat ha'omer day for a Gregorian date.")
    po.add_argument("--date", required=True, help="Gregorian date YYYY-MM-DD.")

    pp = sub.add_parser("parsha", help="Parsha for the Shabbos on or after a date.")
    pp.add_argument("--date", required=True, help="Gregorian date YYYY-MM-DD.")
    pp.add_argument("--israel", action="store_true", help="Use Israel reading schedule.")

    py = sub.add_parser("yahrzeit", help="Future yahrzeit dates from a Hebrew date of death.")
    py.add_argument("--hebrew-date", required=True,
                    help="Hebrew date of death YYYY-MM-DD (month 1=Nisan..13=Adar II).")
    py.add_argument("--years", type=int, default=5, help="Number of future yahrzeits (default 5).")

    args = p.parse_args()

    handlers = {
        "convert": cmd_convert,
        "omer": cmd_omer,
        "parsha": cmd_parsha,
        "yahrzeit": cmd_yahrzeit,
    }

    try:
        result = handlers[args.cmd](args)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(2)
    except Exception as e:
        print(json.dumps({"error": f"Unexpected error: {type(e).__name__}: {e}"}))
        sys.exit(3)


if __name__ == "__main__":
    main()
