# [Download](https://s3-eu-west-1.amazonaws.com/pczek.github.com/calendar/latest.pdf)

# papr
Command line tool to generate a PDF template for a small foldable paper calendar.

![ScreenShot](demo.jpg)

## Info
Papr currently only produces a PDF output. When you are printing the PDF file make sure you have to automated positioning or resizing features of your printer enabled!

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


