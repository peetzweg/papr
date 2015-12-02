#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import locale
import pangocairo
import optparse
import datetime
import logging
from util import metrics
from copy import copy
from style.classic import drawCalendar


# Custom optparse options
class CalendarOption (optparse.Option):

    def check_year(option, opt, value):
        # strftime() cannot use years before 1990
        lowerLimit = 1990
        upperLimit = datetime.MAXYEAR

        # in range() the upperLimit is exclusive
        if(int(value) not in range(lowerLimit, upperLimit + 1)):
            raise optparse.OptionValueError(
                "option %s: invalid year value: %r (must be integer value in range %u - %u)" % (opt, value, lowerLimit, upperLimit))
        return int(value)

    def check_month(option, opt, value):
        if(int(value) not in range(1, 12 + 1)):
            raise optparse.OptionValueError(
                "option %s: invalid month value: %r" % (opt, value))
        return int(value)

    TYPES = optparse.Option.TYPES + ("year", "month")
    TYPE_CHECKER = copy(optparse.Option.TYPE_CHECKER)
    TYPE_CHECKER["year"] = check_year
    TYPE_CHECKER["month"] = check_month


def main():
    # SetUp OptionParser
    parser = optparse.OptionParser(option_class=CalendarOption)

    parser.add_option("-A", "--abbreviate_all", action="store_true",
                      help="use abbreviations for weekdays and months", default=False)

    parser.add_option("-a", "--abbreviate", action="store_true",
                      help="use abbreviations for weekdays", default=False)

    parser.add_option("-b", "--brand", type="string",
                      help="assign a brand string", default="")

    parser.add_option("-c", "--color", action="store_true",
                      help="color date numbers", default=False)

    parser.add_option("-d", "--debug", action="store_true",
                      help="print status and debug messages to stdout", default=False)

    font_map = pangocairo.cairo_font_map_get_default()
    parser.add_option("-f", "--font", type="choice", choices=[f.get_name(
    ) for f in font_map.list_families()], help="choose which font to use", default="Sans")

    parser.add_option("-l", "--locale", type="string",
                      help="choose locale to use (default en_US.UTF8, check 'locale -a' for available locales)", default="en_US")

    # create date object to set default month and year to today
    td = datetime.date.today()
    parser.add_option("-m", "--month", type="month",
                      help="specify the starting month as a number (1-12), default is the current month (" + str(td.month) + ").", default=td.month)

    parser.add_option("--margin", type="int",
                      help="specify the margin of the calendar in millimeters. Used to adapt to your printer, default ist 5mm", default=5)

    parser.add_option("-o", "--out", dest="out", type="string",
                      help="specify output file", default="out.pdf")

    # currently supported sizes of paper
    paperSizes = ("A4", "A3", "USLetter")
    parser.add_option("-p", "--paper", type="choice", choices=paperSizes,
                      help="choose which paper dimensions should be used " + str(paperSizes) + " default is A4", default="A4")

    parser.add_option("-v", "--verbose", action="store_true",
                      help="print status messages to stdout", default=False)

    parser.add_option("-y", "--year", type="year",
                      help="specify the year the calendar should start, default is the current year (" + str(td.year) + ").", default=td.year)

    (enviroment, arguments) = parser.parse_args()

    # defining output
    if(enviroment.debug):
        logging.basicConfig(format='%(message)s', level="DEBUG")
        # Printing Options for Debugging
        for option in parser.option_list:
            if(option.dest != None):
                logging.debug("%s = %s", option, getattr(
                    enviroment, option.dest))
    elif(enviroment.verbose):
        logging.basicConfig(format='%(message)s', level="INFO")

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
    if(enviroment.paper == "A4"):
        enviroment.width = 21.0 * metrics.CM
        enviroment.height = 29.7 * metrics.CM
        enviroment
    elif(enviroment.paper == "A3"):
        enviroment.width = 29.7 * metrics.CM
        enviroment.height = 42.0 * metrics.CM
    elif(enviroment.paper == "USLetter"):
        enviroment.width = 8.5 * metrics.INCH
        enviroment.height = 11.0 * metrics.INCH

    # adding aditional information to enviroment
    # env.safety margin for printing (A4 printers a unable to print on the
    # whole page)
    enviroment.safety = enviroment.margin * metrics.MM
    enviroment.page_width = enviroment.height / 4.0  # 4 pages in landscape

    enviroment.cell_width = (enviroment.page_width -
                             2.0 * enviroment.safety) / 2
    enviroment.cell_height = (enviroment.width / 8.0) - \
        ((2 * enviroment.safety) / 4.0)
    enviroment.line_width = 0.01 * metrics.CM
    enviroment.font_size = 6

    drawCalendar(enviroment)

    return 0

if __name__ == "__main__":
    sys.exit(main())
