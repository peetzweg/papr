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
    logging.debug("Creating Cario Surface and Context")
    logging.debug("width = %sp/%scm, height = %sp/%scm", env.height,
                  env.height / metrics.CM, env.width, env.width / metrics.CM)
    surface = cairo.PDFSurface(env.out, env.height, env.width)
    cr = cairo.Context(surface)

    # draw first month
    monthToDraw = env.month
    yearToDraw = env.year
    cr.save()
    cr.translate(env.height, env.width / 2)
    cr.rotate(math.pi)
    drawMonth(cr, env, yearToDraw, monthToDraw)
    cr.restore()

    # draw second month
    cr.save()
    cr.translate(0, env.width / 2)

    # check if last month was december
    # if so set month to january and increment year
    if(monthToDraw == 12):
        monthToDraw = 1
        yearToDraw += 1
    else:
        monthToDraw += 1
    drawMonth(cr, env, yearToDraw, monthToDraw)
    cr.restore()

    if(env.brand != ""):
        cr.save()
        drawText(cr, env, env.brand, env.height -
                 env.page_width + env.safety, env.width / 2 + 3, 6)
        cr.translate(env.height, env.width / 2)
        cr.rotate(math.pi)
        drawText(cr, env, env.brand, env.height -
                 env.page_width + env.safety, 0 + 3, 6)
        cr.restore()

    logging.info("Finished drawing Calendar!")


def drawText(cr, env, text, x, y, fontSize):
    cr.move_to(x, y)
    pc = pangocairo.CairoContext(cr)
    pc.set_antialias(cairo.ANTIALIAS_SUBPIXEL)

    # Number
    layoutNumber = pc.create_layout()
    fontNumber = pango.FontDescription("%s heavy %s" % (env.font, fontSize))
    layoutNumber.set_font_description(fontNumber)

    layoutNumber.set_text(text.split()[0])
    if env.color:
        cr.set_source_rgb(0.6, 0, 0)
    else:
        cr.set_source_rgb(0, 0, 0)
    pc.update_layout(layoutNumber)
    pc.show_layout(layoutNumber)

    # Day
    dimensions = layoutNumber.get_pixel_size()
    cr.move_to(x + dimensions[0] + fontSize / 2, y)
    layoutDay = pc.create_layout()
    fontDay = pango.FontDescription("%s %s" % (env.font, fontSize))
    layoutDay.set_font_description(fontDay)

    layoutDay.set_text(text.split()[1])
    cr.set_source_rgb(0, 0, 0)
    pc.update_layout(layoutDay)
    pc.show_layout(layoutDay)


def drawMonthTitle(cr, env, x, y, width, height, dateObject):

    # preparing month string
    style = "%B"
    if(env.abbreviate_all):
        style = "%b"
    monthString = dateObject.strftime(style)

    # preparing pango context and layout
    pc = pangocairo.CairoContext(cr)
    pc.set_antialias(cairo.ANTIALIAS_SUBPIXEL)

    layout = pc.create_layout()
    layout.set_text(monthString)

    # calculate font size
    fits = False
    fontSize = 20
    while not fits:
        font = pango.FontDescription("%s %s" % (env.font, fontSize))
        layout.set_font_description(font)
        logging.debug("font size: %s pixel_size: %s",
                      fontSize, layout.get_pixel_size())
        if(layout.get_pixel_size()[0] <= env.cell_width):
            fits = True
        else:
            fontSize -= 1

    # preparing cairo context
    y += ((env.cell_height / 2) - (layout.get_pixel_size()[1] / 2))
    cr.move_to(x, y)
    cr.set_source_rgb(0, 0, 0)

    # drawing pango text
    pc.update_layout(layout)
    pc.show_layout(layout)


def drawDay(cr, env, x, y, width, height, lineWidth, dateObject):

    # fill box if weekend
    if(dateObject.isoweekday() >= 6):
        cr.rectangle(x, y, width, height)
        cr.set_source_rgba(0.90, 0.90, 0.90, 1.0)
        cr.fill()

    # drawing the box
    cr.set_source_rgba(0, 0, 0, 1.0)
    cr.set_line_width(lineWidth)
    cr.rectangle(x, y, width, height)
    cr.stroke()

    # drawing the text
    OFFSET_X, OFFSET_Y = math.floor(
        env.font_size * 0.3333), math.floor(env.font_size * 0.3333)

    style = "%A"
    if(env.abbreviate or env.abbreviate_all):
        style = "%a"
    dayString = "%s %s" % (dateObject.day, dateObject.strftime(style))
    drawText(cr, env, dayString, x + OFFSET_X, y + OFFSET_Y, env.font_size)


def drawMonth(cr, env, year, month):

    # Creating a new date object with the first day of the month to draw
    date = datetime.date(year, month, 1)
    logging.info("drawing %s...", date.strftime("%B %Y"))

    # Defining a one day timedelta object to increase the date object
    one_day = datetime.timedelta(days=1)

    # draw month name in first cell
    drawMonthTitle(cr, env, env.safety, env.safety,
                   env.cell_width, env.cell_height, date)

    cellsOnPage = 1
    cellsOnPageMax = 8
    page = 0
    row = 1
    column = 0
    # for every day of the month
    while month == date.month:

        # positions on page
        x = env.safety + (page * env.page_width) + (column * env.cell_width)
        y = env.safety + (row * env.cell_height)

        # draw day
        drawDay(cr, env, x, y, env.cell_width,
                env.cell_height, env.line_width, date)

        # increment cell counter
        cellsOnPage += 1
        row += 1

        # increment date by one day
        date += one_day

        # if more than 8 cells on page
        if(cellsOnPage >= cellsOnPageMax):
            # reset cells on page counter
            cellsOnPage = 0
            # increment page counter
            page += 1
            column = 0
            row = 0

        if(cellsOnPage == 4):
            row = 0
            column += 1
