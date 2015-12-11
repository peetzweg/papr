#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import cairo
import pango
import pangocairo
import datetime
import logging
from util import metrics


def drawCalendar(env):
    logging.debug(
        "Adding aditional information to enviroment specific to this cal style")
    env.font_size = 6
    env.line_width = 0.01 * metrics.CM
    env.row_width = (env.height - (13.0 * env.safety)) / 12.0

    logging.debug('row is %smm', env.row_width / metrics.MM)

    env.row_height = (env.width - (2 * env.safety)) / 32

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
    for columnNo in range(0, 12):  # Iterate over 4 Month. 4 Month fit on one page
        # move on the page to draw next month
        cr.save()
        cr.translate(env.safety + (columnNo * env.row_width) +
                     (columnNo * env.safety), 0)
        drawMonthTitle(cr, env, date)
        # for every day of the month
        startingMonth = date.month
        while date.month == startingMonth:
            drawDay(cr, env, date)
            # increment date by one day
            date += ONE_DAY
        cr.restore()


def drawMonthTitle(cr, env, date):
    cr.save()
    pc = pangocairo.CairoContext(cr)
    pc.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
    layout = pc.create_layout()
    font = pango.FontDescription("%s %s" % (env.font, env.font_size * 2))
    layout.set_font_description(font)

    # preparing month string
    style = "%B"
    if(env.abbreviate_all):
        style = "%b"
    monthString = date.strftime(style)

    layout.set_text(monthString)
    xOffset = (env.row_width - layout.get_pixel_size()[0]) / 2
    yOffset = (env.safety + (1.0 * env.row_height)) - \
        layout.get_pixel_size()[1]

    cr.translate(xOffset, yOffset)

    pc.update_layout(layout)
    pc.show_layout(layout)
    cr.restore()


def drawDay(cr, env, date):
    cr.save()
    yOffset = env.safety + \
        ((date.day - 1) * env.row_height) + (1.0 * env.row_height)
    # translate to drawing point
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

    # Text
    pc = pangocairo.CairoContext(cr)
    pc.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
    layout = pc.create_layout()
    font = pango.FontDescription("%s %s" % (env.font, env.font_size))
    layout.set_font_description(font)

    style = "%A"
    if(env.abbreviate or env.abbreviate_all):
        style = "%a"
    dayString = "%s %s" % (date.day, date.strftime(style))
    layout.set_text(dayString)

    yOffset = (env.row_height - (layout.get_pixel_size()[1])) / 2
    cr.translate(env.font_size / 2, yOffset)
    pc.update_layout(layout)
    pc.show_layout(layout)
    cr.restore()
