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
    size = math.ceil(env.row_height * 0.9) # calculating font-size depending on the row height
    font = pango.FontDescription("%s %s" % (env.fontHeading, size))
    layout.set_font_description(font)

    # preparing month string
    style = "%b"
    # TODO String is always abbreviated, adjust the font-size depending on the row width for all month titles!
    # style = "%B"
    # if(env.abbreviate_all):
    #     style = "%b"
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
    cr.save() # save matrix

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

    # Setting Text
    pc = pangocairo.CairoContext(cr)
    pc.set_antialias(cairo.ANTIALIAS_SUBPIXEL)

    dayLayout = pc.create_layout()
    numberLayout = pc.create_layout()

    daySize = math.floor(env.row_height * 0.25)
    numberSize = math.floor(env.row_height * 0.5)
    yOffset = (env.row_height* 0.25) / 2

    dayFont = pango.FontDescription("%s %s" % (env.font, daySize)) # day text is way smaller than number
    numberFont = pango.FontDescription("%s %s" % (env.font, numberSize))

    dayLayout.set_font_description(dayFont)
    numberLayout.set_font_description(numberFont)

    style = "%a" # by default abbreviated because need of space!
    # if(env.abbreviate or env.abbreviate_all):
    #     style = "%a"
    weekdayString = "%s" % (date.strftime(style))
    dayLayout.set_text(weekdayString) # Weekday
    numberLayout.set_text("%s" % date.day) # Number

    # draw Number
    cr.save()
    xOffset = math.ceil((env.row_width / 8)  - (numberLayout.get_pixel_size()[0] / 2))
    # yOffset = math.floor((env.row_height - numberSize - daySize - (daySize/2)) / 2)
    numberOffset = yOffset + ((numberSize - numberLayout.get_pixel_size()[1])/2)

    cr.translate(xOffset, numberOffset)
    pc.update_layout(numberLayout)
    pc.show_layout(numberLayout)
    cr.restore()

    # draw Weekday
    cr.save()
    xOffset = math.ceil((env.row_width / 8)  - (dayLayout.get_pixel_size()[0] / 2))
    yOffset = env.row_height - yOffset - daySize
    cr.translate(xOffset, yOffset)
    pc.update_layout(dayLayout)
    pc.show_layout(dayLayout)
    cr.restore()

    cr.restore() # restore matrix
