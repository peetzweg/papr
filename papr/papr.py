#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import locale
import argparse
import datetime
import logging

import gi
gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

from papr.util import metrics
from papr.layouts import classic
from papr.layouts import column
from papr.layouts import oneyear
from papr.layouts import big
from papr.layouts import rows


def main():
    # SetUp OptionParser
    parser = argparse.ArgumentParser(description='Create a Calendar')

    parser.add_argument("-o", "--out", dest="out",
                        help="specify output file (format detected from extension: .pdf or .svg)", default="out.pdf")

    parser.add_argument("-A", "--abbreviate_all", action="store_true",
                        help="use abbreviations for weekdays and months", default=False)

    parser.add_argument("-a", "--abbreviate", action="store_true",
                        help="use abbreviations for weekdays", default=False)

    parser.add_argument("-b", "--brand",
                        help="assign a brand string", default="")

    parser.add_argument("-c", "--color", action="store_true",
                        help="color date numbers", default=False)

    font_map = PangoCairo.font_map_get_default()
    parser.add_argument("-f", "--fonts", choices=[f.get_name(
    ) for f in font_map.list_families()], help="choose which font(s) to use", default=['Sans'], metavar="FONT", nargs="+")

    parser.add_argument("-l", "--locale",
                        help="choose locale to use (default en_US.UTF8, check 'locale -a' for available locales)", default="en_US")

    # create date object to set default month and year to today
    td = datetime.date.today()
    parser.add_argument("-m", "--month", type=int, choices=range(1, 13), metavar="MONTH",
                        help="specify the starting month as a number (1-12), default is the current month (" + str(td.month) + ").", default=td.month)

    parser.add_argument("-y", "--year", type=int, choices=range(1990, datetime.MAXYEAR + 1), metavar="YEAR",
                        help="specify the year the calendar should start, default is the current year (" + str(td.year) + ").", default=td.year)

    # currently supported sizes of paper
    paperSizes = ("A5", "A4", "A3", "A2", "A1", "A0", "USLetter", "USTabloid", "USLedger")
    parser.add_argument("-p", "--paper", choices=paperSizes,
                        help="choose which paper dimensions should be used " + str(paperSizes) + " default is A4", default="A4")

    parser.add_argument("--margin", type=int,
                        help="specify the margin of the calendar in millimeters. Used to adapt to your printer, default ist 5mm", default=5)

    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print status messages to stdout", default=False)

    parser.add_argument("-d", "--debug", action="store_true",
                        help="print status and debug messages to stdout", default=False)
    layouts = ("classic", "column", "oneyear", "big", "rows")
    parser.add_argument("layout", choices=layouts, metavar="LAYOUT",
                        help="choose calendar layout: " + str(layouts))
    environment = parser.parse_args()

    # defining output
    if(environment.debug):
        logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    elif(environment.verbose):
        logging.basicConfig(format='%(message)s', level=logging.INFO)

    # setting locale
    try:
        logging.debug("setting locale to '%s'", environment.locale)
        locale.setlocale(locale.LC_ALL, environment.locale)
    except locale.Error:
        logging.error(
            "locale: '%s' not found!\nList all installed locales with 'locale -a' and choose locale with -l/--locale option.", environment.locale)
        sys.exit(1)

    logging.debug(
        "Adjusting width and height values according to desired paper format: " + environment.paper)
    if environment.paper == "A5":
        environment.width = 14.8 * metrics.CM
        environment.height = 21.0 * metrics.CM
    elif environment.paper == "A4":
        environment.width = 21.0 * metrics.CM
        environment.height = 29.7 * metrics.CM
    elif environment.paper == "A3":
        environment.width = 29.7 * metrics.CM
        environment.height = 42.0 * metrics.CM
    elif environment.paper == "A2":
        environment.width = 42.0 * metrics.CM
        environment.height = 59.4 * metrics.CM
    elif environment.paper == "A1":
        environment.width = 59.4 * metrics.CM
        environment.height = 84.1 * metrics.CM
    elif environment.paper == "A0":
        environment.width = 84.1 * metrics.CM
        environment.height = 118.9 * metrics.CM
    elif environment.paper == "USLetter":
        environment.width = 8.5 * metrics.INCH
        environment.height = 11.0 * metrics.INCH
    elif environment.paper == "USTabloid":
        environment.width = 11.0 * metrics.INCH
        environment.height = 17.0 * metrics.INCH
    elif environment.paper == "USLedger":
        environment.width = 11.0 * metrics.INCH
        environment.height = 17.0 * metrics.INCH


    # Setup fonts
    environment.font = environment.fonts.pop() # last provided font is used generally
    try:
        environment.fontHeading = environment.fonts.pop() # use additional provided font for headers
    except IndexError:
        environment.fontHeading = environment.font # if just one font set heading font same as general


    # env.safety margin for printing (A4 printers a unable to print on the
    # whole page)
    environment.safety = environment.margin * metrics.MM


    if (environment.debug):
        # Printing Options for Debugging
        dic = vars(environment)
        for key in dic:
            if(dic[key] != None):
                logging.debug("%s = %s", key, dic[key])

    drawCalendar = {"classic": classic.drawCalendar,
                    "column": column.drawCalendar,
                    "oneyear": oneyear.drawCalendar,
                    "big": big.drawCalendar,
                    "rows": rows.drawCalendar}
    drawCalendar[environment.layout](environment)

    return 0

if __name__ == "__main__":
    sys.exit(main())
