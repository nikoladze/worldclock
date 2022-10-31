#!/usr/bin/env python3

from argparse import ArgumentParser
import dateutil
import dateutil.parser
from datetime import datetime, timedelta
from dateutil.zoneinfo import getzoneinfofile_stream, ZoneInfoFile
from collections import defaultdict

# opinionated list of timezones
# and (for this list) unambiguous abbreviations
# adjust to your needs
TIMEZONES = {
    "UTC": "UTC",
    "HST": "Pacific/Honolulu",
    "PST": "America/Tijuana",
    "CST": "America/Chicago",
    "EST": "America/Thunder_Bay",
    "WET": "Europe/Lisbon",
    "CET": "Europe/Berlin",
    "EET": "Europe/Kyiv",
    "+0330": "Asia/Tehran",
    "IST": "Asia/Kolkata",
    "+07": "Asia/Novosibirsk",
    "HKT": "Asia/Hong_Kong",
    "JST": "Asia/Tokyo",
    "AEST": "Australia/Sydney",
}


def main(args=None):
    timezones = TIMEZONES.copy()

    parser = ArgumentParser()
    parser.add_argument("time", nargs="*")
    parser.add_argument("--extra-list", nargs="+", help="also show these timezones")
    parser.add_argument("--only-list", nargs="+", help="only show these timezones")
    parser.add_argument("--list-timezones", action="store_true")
    parser.add_argument(
        "--fold",
        type=int,
        choices={0, 1},
        help="Explicitely choose earlier (0) or later (1) time for ambiguous times",
    )
    parser.add_argument(
        "--dst-info",
        action="store_true",
        help=(
            "show if times are daylight-saving-times (dst) "
            "and until when if there is a change in the next 366 days"
        ),
    )
    parser.add_argument(
        "--also-in",
        action="store_true",
        help="Show list of other time zones with the same time at the reference time",
    )
    parser.add_argument(
        "--long",
        action="store_true",
        help="Don't shorten the list of other time zones shown through --also-in",
    )
    args = parser.parse_args(args)

    timezones_for_parser = {k: dateutil.tz.gettz(v) for k, v in timezones.items()}
    if len(args.time) > 0:
        time = " ".join(args.time)
        reftime = dateutil.parser.parse(time, tzinfos=timezones_for_parser)
    else:
        reftime = datetime.now()
    if reftime.tzinfo is None:
        reftime = reftime.replace(tzinfo=dateutil.tz.tzlocal())

    if args.fold is not None:
        reftime = dateutil.tz.enfold(reftime, args.fold)

    if args.list_timezones:
        print_timezones(reftime)
        return

    if args.extra_list is not None:
        for abbr in args.extra_list:
            timezones[abbr] = abbr

    if args.only_list is not None:
        timezones = {abbr: abbr for abbr in args.only_list}

    print_table(
        timezones, reftime, long=args.long, dst_info=args.dst_info, also_in=args.also_in
    )


def format_utcoffset(tz, reftime):
    utcoffset = tz.utcoffset(reftime)
    midnight = dateutil.parser.parse("00:00")
    if utcoffset.total_seconds() >= 0:
        utcoffset = f"+{midnight + utcoffset:%H:%M}"
    else:
        utcoffset = f"-{midnight - utcoffset:%H:%M}"
    return utcoffset


def all_timezones():
    return ZoneInfoFile(getzoneinfofile_stream()).zones.keys()


def print_timezones(reftime):
    for timezone_str in all_timezones():
        tz = dateutil.tz.gettz(timezone_str)
        utcoffset = format_utcoffset(tz, reftime)
        print(f"{timezone_str:<30} UTC{utcoffset}")


def print_table(timezones, reftime, long=False, dst_info=False, also_in=False):
    timezones_per_utcoffset = defaultdict(list)
    utcoffset_for_timezone = {}
    for timezone_str in all_timezones():
        tz = dateutil.tz.gettz(timezone_str)
        timezones_per_utcoffset[format_utcoffset(tz, reftime)].append(timezone_str)
        utcoffset_for_timezone[timezone_str] = format_utcoffset(tz, reftime)
    max_len_also = 110 if dst_info else 120
    header = ["Name", "Abbr", "UTC offset", "Time"]
    if dst_info:
        header += ["DST", "until"]
    if also_in:
        header.append("Same time also in")
    rows = []
    for abbr, timezone in timezones.items():
        if len(abbr) > 5:
            # in this case we probably don't have an abbreviation
            # but a region name that is already printed
            abbr = ""
        tz = dateutil.tz.gettz(timezone)
        if tz is None:
            tz = dateutil.parser.parse("00:00 " + timezone).tzinfo
        utcoffset = format_utcoffset(tz, reftime)
        also_in_str = ", ".join(sorted(timezones_per_utcoffset[utcoffset]))
        if len(also_in_str) > max_len_also and not long:
            also_in_str = also_in_str[:max_len_also] + "..."
        dt = reftime.astimezone(tz)
        row = [timezone, abbr, "UTC" + utcoffset, f"{dt:%Y-%m-%d %H:%M}"]
        if dst_info:
            dt_dst_until = until_when_dst(dt)
            until_str = f"{dt_dst_until:%Y-%m-%d}" if dt_dst_until is not None else ""
            row.append("yes" if dt.dst() else "no")
            row.append(until_str)
        if also_in:
            row.append(also_in_str)
        rows.append(row)
    tabulate(header, rows)


def until_when_dst(dt):
    """
    I don't know how to query programatically when dst/non-dst ends
    so i fall back to this hack:
    - scan through the next 366 days
    - then go back up to 24 hours to find the day/hour when it changed

    let me know if there is a better way :)
    """
    dst_flag = bool(dt.dst())
    for d in range(366):
        dt += timedelta(days=1)
        if bool(dt.dst()) != dst_flag:
            for h in range(24):
                dt -= timedelta(hours=1)
                if bool(dt.dst()) == dst_flag:
                    return dt.replace(minute=0)


def tabulate(header, rows):
    col_widths = [
        max(len(row[i]) for row in [header] + rows) for i in range(len(rows[0]))
    ]

    def format_row(row):
        return "  ".join(f"{field:<{width}}" for field, width in zip(row, col_widths))

    header_str = format_row(header)
    print(header_str)
    print("=" * len(header_str))
    for row in rows:
        print(format_row(row))


if __name__ == "__main__":
    main()
