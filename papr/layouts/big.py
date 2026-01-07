#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Big Layout - Full year calendar on a single sheet.
Days flow continuously with configurable columns per row.
Day/date in top-right corner. Month label flags (with pole) on first day of each month.
"""

import math
import datetime
import logging
import calendar

import cairo
from gi.repository import Pango

from papr.util import metrics
from papr.util import drawing


# =============================================================================
# CONFIGURATION - Easy to adjust values
# =============================================================================

# Number of days per row (columns)
DAYS_PER_ROW = 21
# DAYS_PER_ROW = 25

# Font size in points for day/date text
DAY_TEXT_FONT_SIZE = 4

# Font size in points for month label
MONTH_LABEL_FONT_SIZE = 4

# Border settings
BORDER_COLOR = (0.7, 0.7, 0.7)  # RGB values 0-1
BORDER_WIDTH = 0.2  # in mm

# Flag and pole settings
FLAG_COLOR = (0.3, 0.3, 0.3)  # RGB values 0-1 (same for flag background and pole)
FLAG_POLE_WIDTH = 0.5  # in mm

# =============================================================================


def drawCalendar(env):
    logging.debug("Adding additional information to environment specific to Big layout")

    # Use configurable columns
    env.columns = DAYS_PER_ROW

    # Calculate how many rows we need for a full year
    year_days = 366 if calendar.isleap(env.year) else 365
    env.rows = math.ceil(year_days / env.columns)

    # Available width and height after margins (landscape: height is page width)
    available_width = env.height - (2 * env.safety)
    available_height = env.width - (2 * env.safety)

    # Cell dimensions fill the available space
    env.cell_width = available_width / env.columns
    env.cell_height = available_height / env.rows

    # Position grid at margins
    env.offset_x = env.safety
    env.offset_y = env.safety

    # Store configurable values
    env.line_width = BORDER_WIDTH * metrics.MM
    env.border_color = BORDER_COLOR
    env.flag_color = FLAG_COLOR
    env.flag_pole_width = FLAG_POLE_WIDTH * metrics.MM
    env.day_text_size = DAY_TEXT_FONT_SIZE
    env.month_label_size = MONTH_LABEL_FONT_SIZE

    logging.debug("Cell size: %s x %s mm", env.cell_width / metrics.MM, env.cell_height / metrics.MM)
    logging.debug("Grid: %s columns x %s rows", env.columns, env.rows)

    logging.debug("Creating Cairo Surface and Context")
    logging.debug("width = %sp/%scm, height = %sp/%scm", env.height,
                  env.height / metrics.CM, env.width, env.width / metrics.CM)

    # Create landscape PDF
    surface = cairo.PDFSurface(env.out, env.height, env.width)
    cr = cairo.Context(surface)

    # Draw all days of the year
    date = datetime.date(env.year, 1, 1)
    ONE_DAY = datetime.timedelta(days=1)
    day_index = 0

    while date.year == env.year:
        col = day_index % env.columns
        row = day_index // env.columns

        x = env.offset_x + (col * env.cell_width)
        y = env.offset_y + (row * env.cell_height)

        # Check if this is the first day of a month
        is_month_start = (date.day == 1)

        drawDay(cr, env, x, y, date, is_month_start)

        date += ONE_DAY
        day_index += 1

    logging.info("Finished drawing Calendar!")


def drawDay(cr, env, x, y, date, is_month_start):
    """Draw a single day cell."""
    with drawing.restoring_transform(cr):
        cr.translate(x, y)

        # Fill background for weekends
        if date.isoweekday() >= 6:
            cr.rectangle(0, 0, env.cell_width, env.cell_height)
            cr.set_source_rgba(0.92, 0.92, 0.92, 1.0)
            cr.fill()

        # Stroke the cell border
        cr.set_source_rgba(*env.border_color, 1.0)
        cr.set_line_width(env.line_width)
        cr.rectangle(0, 0, env.cell_width, env.cell_height)
        cr.stroke()

        # Draw day info (weekday and date) in top-right corner
        # Returns the padding used for baseline alignment
        text_padding = drawDayInfo(cr, env, date)

        # Draw month label flag on the left if this is the start of a month
        if is_month_start:
            drawMonthLabel(cr, env, date, text_padding)


def drawMonthLabel(cr, env, date, text_padding):
    """Draw month abbreviation as a flag in the top-left corner with a pole to the bottom."""
    with drawing.restoring_transform(cr):
        month_str = date.strftime("%b").upper()

        font_size = env.month_label_size
        font = Pango.FontDescription("%s bold %s" % (env.font, font_size))

        # Measure text (with kerning enabled)
        temp_layout = drawing.create_layout_with_kerning(cr)
        temp_layout.set_font_description(font)
        temp_layout.set_text(month_str, -1)
        text_width, text_height = temp_layout.get_pixel_size()

        # Padding around text in flag
        padding_x = font_size * 0.4
        padding_y = font_size * 0.2

        # Flag dimensions
        flag_width = text_width + (padding_x * 2)
        flag_height = text_height + (padding_y * 2)

        # Position flag at top-left corner
        # Align text baseline with day/date text by using the same top padding
        flag_x = 0
        flag_y = text_padding - padding_y  # Adjust so text baseline aligns

        # Draw the flag pole (vertical line from top of flag to bottom of cell)
        # pole_x = env.flag_pole_width / 2
        pole_x = 0
        pole_y = env.line_width / 2
        cr.set_source_rgba(*env.flag_color, 1.0)
        cr.set_line_width(env.flag_pole_width)
        cr.move_to(pole_x, pole_y)
        cr.line_to(pole_x, env.cell_height - pole_y)
        cr.stroke()

        # Draw flag background
        cr.rectangle(flag_x, pole_y, flag_width, flag_height + flag_y - pole_y)
        cr.set_source_rgba(*env.flag_color, 1.0)
        cr.fill()

        # Draw the text in white
        with drawing.layout(cr) as layout:
            layout.set_font_description(font)
            layout.set_text(month_str, -1)
            cr.move_to(flag_x + padding_x, flag_y + padding_y)
            cr.set_source_rgb(1, 1, 1)


def drawDayInfo(cr, env, date):
    """Draw weekday abbreviation and date number in top-right corner, baseline aligned."""
    font_size = env.day_text_size

    # Half character width padding
    padding = font_size * 0.5

    weekday_str = date.strftime("%a").upper()
    day_str = str(date.day)

    with drawing.restoring_transform(cr):
        # Create fonts - same size for both
        font = Pango.FontDescription("%s %s" % (env.font, font_size))
        font_bold = Pango.FontDescription("%s bold %s" % (env.font, font_size))

        # Measure weekday (with kerning enabled)
        weekday_layout = drawing.create_layout_with_kerning(cr)
        weekday_layout.set_font_description(font)
        weekday_layout.set_text(weekday_str, -1)
        weekday_width, _ = weekday_layout.get_pixel_size()

        # Measure day number (with kerning enabled)
        day_layout = drawing.create_layout_with_kerning(cr)
        day_layout.set_font_description(font_bold)
        day_layout.set_text(day_str, -1)
        day_width, _ = day_layout.get_pixel_size()

        # Gap between weekday and day number
        gap = padding * 0.5

        # Calculate total width and position from right
        total_width = weekday_width + gap + day_width
        start_x = env.cell_width - padding - total_width

        # Draw weekday
        with drawing.layout(cr) as layout:
            layout.set_font_description(font)
            layout.set_text(weekday_str, -1)
            cr.move_to(start_x, padding)
            cr.set_source_rgb(0.4, 0.4, 0.4)

        # Draw day number after weekday, baseline aligned
        with drawing.layout(cr) as layout:
            layout.set_font_description(font_bold)
            layout.set_text(day_str, -1)
            cr.move_to(start_x + weekday_width + gap, padding)
            cr.set_source_rgb(0.1, 0.1, 0.1)

    # Return the padding used so month label can align
    return padding
