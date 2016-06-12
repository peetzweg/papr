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
    env.column_width = env.height / 4.0  # 4 columns in landscape
    env.row_width = (env.column_width -
                     2.0 * env.safety)
    env.row_height = (env.width - (4 * env.safety)) / 33

    logging.debug("Creating Cario Surface and Contex")
    logging.debug("width = %sp/%scm, height = %sp/%scm", env.height,
                  env.height / metrics.CM, env.width, env.width / metrics.CM)
    surface = cairo.PDFSurface(env.out, env.height, env.width)
    cr = cairo.Context(surface)

    date = datetime.date(env.year, env.month, 1)
    drawMonth(cr, env, date)
    logging.info("Finished drawing Calendar!")


def drawMonth(cr, env, date):
    # Creating a new date object with the first day of the month to draw
    logging.info("drawing %s...", date.strftime("%B %Y"))

    # Defining a one day timedelta object to increase the date object
    ONE_DAY = datetime.timedelta(days=1)
    with drawing.restoring_transform(cr):
        # artificial offset for layouting, later it will be the months title!
        for columnNo in range(0, 4):  # Iterate over 4 Month. 4 Month fit on one page
            with drawing.restoring_transform(cr):
                # move on the page to draw next month
                cr.translate(columnNo * env.column_width, 0)
                drawMonthTitle(cr, env, date)
                # for every day of the month
                startingMonth = date.month
                while date.month == startingMonth:
                    # increment date by one day
                    drawDay(cr, env, date)
                    date += ONE_DAY


def drawMonthTitle(cr, env, date):
    with drawing.restoring_transform(cr):
        with drawing.layout(cr) as layout:
            font = Pango.FontDescription("%s %s" % (env.font, env.font_size * 2))
            layout.set_font_description(font)

            # preparing month string
            style = "%B"
            if(env.abbreviate_all):
                style = "%b"
            monthString = date.strftime(style)

            layout.set_text(monthString, -1)
            xOffset = (env.column_width - layout.get_pixel_size()[0]) / 2
            yOffset = (((env.row_height * 2) -
                        layout.get_pixel_size()[1]) / 2) + env.safety

            cr.translate(xOffset, yOffset)


def drawDay(cr, env, date):
    with drawing.restoring_transform(cr):
        yOffset = env.safety + (2 * env.row_height) + ((date.day - 1) * env.row_height)
        if(date.day > 15):  # add folding margin for other half of the month
            yOffset += 2 * env.safety
        # translate to drawing point
        cr.translate(env.safety, yOffset)
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

        # Text
        with drawing.layout(cr) as layout:
            font = Pango.FontDescription("%s %s" % (env.font, env.font_size))
            layout.set_font_description(font)

            style = "%A"
            if(env.abbreviate or env.abbreviate_all):
                style = "%a"
            dayString = "%s %s" % (date.day, date.strftime(style))
            layout.set_text(dayString, -1)

            yOffset = (env.row_height - (layout.get_pixel_size()[1])) / 2
            cr.translate(env.font_size / 2, yOffset)
