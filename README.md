# papr
Command line tool to generate a PDF template for a small foldable paper calendar.

## Table of contents

 - [Quick start](#quick-start)
 - [Copyright and license](#copyright-and-license)

## Quick start
	Usage: papr.py [options]

	Options:
	  -h, --help            show this help message and exit
	  -o OUT, --out=OUT     specify output file
	  -m MONTH, --month=MONTH
	                        specify from which month the calendar should start,
	                        default is the current month. (1-12)
	  -l LOCALE, --locale=LOCALE
	                        choose locale to use (default en_US.UTF8, check
	                        'locale -a' for available locales)
	  -a, --abbreviate      use abbreviations for weekdays
	  -A, --abbreviate_all  use abbreviations for weekdays and months
	  -f FONT, --font=FONT  choose which font to use
	  -v, --verbose         print status messages to stdout
	  -d, --debug           print status and debug messages to stdout

## Copyright and license
