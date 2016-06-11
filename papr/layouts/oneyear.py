#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import datetime
import logging

import cairo
from gi.repository import Pango
from gi.repository import PangoCairo

from util import metrics
from util import drawing


def drawCalendar(env):
    logging.debug(
        "Adding aditional information to enviroment specific to this cal style")
    env.font_size = 6
    env.line_width = 0.01 * metrics.CM
    env.row_width = (env.height - (13.0 * env.safety)) / 12.0
    env.row_height = (env.width - (2 * env.safety)) / 32

    logging.debug('row is %smm/%spx wide', env.row_width / metrics.MM, env.row_width)
    logging.debug('row is %smm/%spx high', env.row_height / metrics.MM, env.row_height)

    logging.debug("Creating Cario Surface and Context")
    logging.debug("width = %sp/%scm, height = %sp/%scm", env.height,
                  env.height / metrics.CM, env.width, env.width / metrics.CM)
    surface = cairo.PDFSurface(env.out, env.height, env.width)
    cr = cairo.Context(surface)

    date = datetime.date(env.year, env.month, 1)
    drawMonth(cr, env, date) # TODO using it totally worng, loop here over the function not in the function itself!
    logging.info("Finished drawing Calendar!")


def drawMonth(cr, env, date):
    # Creating a new date object with the first day of the month to draw
    logging.info("drawing %s...", date.strftime("%B %Y"))

    # Defining a one day timedelta object to increase the date object
    ONE_DAY = datetime.timedelta(days=1)
    for columnNo in range(0, 12):  # Iterate over 4 Month. 4 Month fit on one page
        with drawing.restoring_transform(cr):
            # move on the page to draw next month
            cr.translate(env.safety + (columnNo * env.row_width) +
                         (columnNo * env.safety), 0)
            drawMonthTitle(cr, env, date)
            # for every day of the month
            startingMonth = date.month
            while date.month == startingMonth:
                drawDay(cr, env, date)
                # increment date by one day
                date += ONE_DAY


def drawMonthTitle(cr, env, date):
    with drawing.restoring_transform(cr):
        with drawing.layout(cr) as layout:
            size = math.ceil(env.row_height * 0.9) # calculating font-size depending on the row height
            font = Pango.FontDescription("%s %s" % (env.fontHeading, size))
            layout.set_font_description(font)

            # preparing month string
            style = "%b"
            # TODO String is always abbreviated, adjust the font-size depending on the row width for all month titles!
            # style = "%B"
            # if(env.abbreviate_all):
            #     style = "%b"
            monthString = date.strftime(style)

            layout.set_text(monthString, -1)
            xOffset = (env.row_width - layout.get_pixel_size()[0]) / 2
            yOffset = (env.safety + (1.0 * env.row_height)) - \
                layout.get_pixel_size()[1]

            cr.translate(xOffset, yOffset)


def drawDay(cr, env, date):
    with drawing.restoring_transform(cr):
        yOffset = env.safety + \
            ((date.day - 1) * env.row_height) + (1.0 * env.row_height)

        # translate to drawing point top left corner
        cr.translate(0.0, yOffset)

        # fill box if weekend
        if(date.isoweekday() >= 6):
            cr.set_source_rgba(0.90, 0.90, 0.90, 1.0)
            cr.rectangle(0, 0, env.row_width, env.row_height)
            cr.fill()

        # stroke the box
        cr.set_source_rgba(0, 0, 0, 1.0)
        cr.set_line_width(env.line_width)
        cr.rectangle(0, 0, env.row_width, env.row_height)
        cr.stroke()

        daySize = math.floor(env.row_height * 0.25)
        numberSize = math.floor(env.row_height * 0.5)
        yOffset = (env.row_height* 0.25) / 2

        dayFont = Pango.FontDescription("%s %s" % (env.font, daySize)) # day text is way smaller than number
        numberFont = Pango.FontDescription("%s %s" % (env.font, numberSize))

        style = "%a" # by default abbreviated because need of space!
        # if(env.abbreviate or env.abbreviate_all):
        #     style = "%a"
        weekdayString = "%s" % (date.strftime(style))

        with drawing.restoring_transform(cr):
            with drawing.layout(cr) as numberLayout:
                numberLayout.set_font_description(numberFont)
                numberLayout.set_text("%s" % date.day, -1) # Number

                xOffset = math.ceil((env.row_width / 8)  - (numberLayout.get_pixel_size()[0] / 2))
                # yOffset = math.floor((env.row_height - numberSize - daySize - (daySize/2)) / 2)
                numberOffset = yOffset + ((numberSize - numberLayout.get_pixel_size()[1])/2)
                cr.translate(xOffset, numberOffset)

        with drawing.restoring_transform(cr):
            with drawing.layout(cr) as dayLayout:
                dayLayout.set_font_description(dayFont)
                dayLayout.set_text(weekdayString, -1) # Weekday

                xOffset = math.ceil((env.row_width / 8)  - (dayLayout.get_pixel_size()[0] / 2))
                yOffset = env.row_height - yOffset - daySize
                cr.translate(xOffset, yOffset)

