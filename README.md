Small script to show the time around the world using [python-dateutil](https://dateutil.readthedocs.io/en/stable/)

The default list of timezones is hardcoded on top of the script - adjust it to your needs.

I'm no expert in timezones and the [tz database](https://www.iana.org/time-zones). Let me know if something is wrong in the script or can be improved.

Useful links: <https://xkcd.com/now>, <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>

# Examples

Show the current time in different time zones

``` sh
./worldclock.py
```

Show the time in different time zones at 12:00 US central time

``` sh
./worldclock.py 12:00 CST
```

Times are parsed with [`dateutil.parse.parser`](https://dateutil.readthedocs.io/en/stable/parser.html#dateutil.parser.parse) - supports different notations, e.g.

``` sh
./worldclock 2 pm CST
./worldclock 14:00 CST
./worldclock 14:00 -5
./worldclock 14:00 -5
./worldclock 2023-10-30 14:00 CST
```

Show additional time zones

``` sh
./worldclock.py --extra-list America/Mexico_City America/Cancun
```

Show only specific time zones

``` sh
./worldclock.py --only Africa/Nairobi Africa/Lagos
```

Show info on daylight saving time (if observed and until when)

``` sh
./worldclock.py --dst
```


List all timezones and their utc offsets

``` sh
./worldclock.py --list
```
