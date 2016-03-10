#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import locale
import pangocairo
import argparse
import datetime
import logging
from util import metrics
from layouts import classic
from layouts import column
from layouts import oneyear


def main():
    # SetUp OptionParser
    parser = argparse.ArgumentParser(description='Create a Calendar')

    parser.add_argument("-o", "--out", dest="out",
                        help="specify output file", default="out.pdf")

    parser.add_argument("-A", "--abbreviate_all", action="store_true",
                        help="use abbreviations for weekdays and months", default=False)

    parser.add_argument("-a", "--abbreviate", action="store_true",
                        help="use abbreviations for weekdays", default=False)

    parser.add_argument("-b", "--brand",
                        help="assign a brand string", default="")

    parser.add_argument("-c", "--color", action="store_true",
                        help="color date numbers", default=False)

    font_map = pangocairo.cairo_font_map_get_default()
    parser.add_argument("-f", "--font", choices=[f.get_name(
    ) for f in font_map.list_families()], help="choose which font to use", default="Sans", metavar="FONT")

    parser.add_argument("-l", "--locale",
                        help="choose locale to use (default en_US.UTF8, check 'locale -a' for available locales)", default="en_US")

    # create date object to set default month and year to today
    td = datetime.date.today()
    parser.add_argument("-m", "--month", type=int, choices=range(1, 13), metavar="MONTH",
                        help="specify the starting month as a number (1-12), default is the current month (" + str(td.month) + ").", default=td.month)

    parser.add_argument("-y", "--year", type=int, choices=range(1990, datetime.MAXYEAR + 1), metavar="YEAR",
                        help="specify the year the calendar should start, default is the current year (" + str(td.year) + ").", default=td.year)

    # currently supported sizes of paper
    paperSizes = ("A5", "A4", "A3", "A2", "A1", "A0", "USLetter")
    parser.add_argument("-p", "--paper", choices=paperSizes,
                        help="choose which paper dimensions should be used " + str(paperSizes) + " default is A4", default="A4")

    parser.add_argument("--margin", type=int,
                        help="specify the margin of the calendar in millimeters. Used to adapt to your printer, default ist 5mm", default=5)

    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print status messages to stdout", default=False)

    parser.add_argument("-d", "--debug", action="store_true",
                        help="print status and debug messages to stdout", default=False)
    layouts = ("classic", "column", 'oneyear')
    parser.add_argument("layout", choices=layouts, metavar="LAYOUT",
                        help="choose calendar layout: " + str(layouts))
    enviroment = parser.parse_args()

    # defining output
    if(enviroment.debug):
        logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    elif(enviroment.verbose):
        logging.basicConfig(format='%(message)s', level=logging.INFO)

    # setting locale
    try:
        logging.debug("setting locale to '%s'", enviroment.locale)
        locale.setlocale(locale.LC_ALL, enviroment.locale)
    except locale.Error:
        logging.error(
            "locale: '%s' not found!\nList all installed locales with 'locale -a' and choose locale with -l/--locale option.", enviroment.locale)
        sys.exit(1)

    logging.debug(
        "Adjusting width and height values according to desired paper format: " + enviroment.paper)
    if(enviroment.paper == "A5"):
        enviroment.width = 14.8 * metrics.CM
        enviroment.height = 21.0 * metrics.CM
    elif(enviroment.paper == "A4"):
        enviroment.width = 21.0 * metrics.CM
        enviroment.height = 29.7 * metrics.CM
    elif(enviroment.paper == "A3"):
        enviroment.width = 29.7 * metrics.CM
        enviroment.height = 42.0 * metrics.CM
    elif(enviroment.paper == "A2"):
        enviroment.width = 42.0 * metrics.CM
        enviroment.height = 59.4 * metrics.CM
    elif(enviroment.paper == "A1"):
        enviroment.width = 59.4 * metrics.CM
        enviroment.height = 84.1 * metrics.CM
    elif(enviroment.paper == "A0"):
        enviroment.width = 84.1 * metrics.CM
        enviroment.height = 118.9 * metrics.CM
    elif(enviroment.paper == "USLetter"):
        enviroment.width = 8.5 * metrics.INCH
        enviroment.height = 11.0 * metrics.INCH

    # env.safety margin for printing (A4 printers a unable to print on the
    # whole page)
    enviroment.safety = enviroment.margin * metrics.MM

    if (enviroment.debug):
        # Printing Options for Debugging
        dic = vars(enviroment)
        for key in dic:
            if(dic[key] != None):
                logging.debug("%s = %s", key, dic[key])

    drawCalendar = {"classic": classic.drawCalendar,
                    "column": column.drawCalendar,
                    "oneyear": oneyear.drawCalendar}
    drawCalendar[enviroment.layout](enviroment)

    return 0

if __name__ == "__main__":
    sys.exit(main())
