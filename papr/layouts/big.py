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

    # Starting date based on -m flag
    start_date = datetime.date(env.year, env.month, 1)

    # Calculate end date (12 months from start)
    # If starting in April (4), end in March (3) of next year
    # If starting in January (1), end in December (12) of same year
    if env.month == 1:
        end_month = 12
        end_year = env.year
    else:
        end_month = env.month - 1
        end_year = env.year + 1

    last_day_of_end_month = calendar.monthrange(end_year, end_month)[1]
    end_date = datetime.date(end_year, end_month, last_day_of_end_month)

    # Calculate padding to align rows so they end with SAT SUN
    # Each row should start on Monday (weekday() = 0) and end on Sunday (weekday() = 6)
    # weekday(): Monday=0, Sunday=6
    env.padding_cells = start_date.weekday()

    # If not starting in January, we'll have a year transition
    # Use exactly 7 cells (one full week) for mid-year padding to maintain
    # vertical weekend alignment across the year transition
    if env.month > 1:
        env.mid_year_padding = 7
    else:
        env.mid_year_padding = 0

    # Calculate total days in each part
    if env.month > 1:
        dec31 = datetime.date(env.year, 12, 31)
        days_first_part = (dec31 - start_date).days + 1
        jan1_next = datetime.date(env.year + 1, 1, 1)
        days_second_part = (end_date - jan1_next).days + 1
        total_cells = env.padding_cells + days_first_part + env.mid_year_padding + days_second_part
    else:
        total_days = (end_date - start_date).days + 1
        total_cells = env.padding_cells + total_days

    env.rows = math.ceil(total_cells / env.columns)

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

    logging.debug("Start date: %s, End date: %s", start_date, end_date)
    logging.debug("Padding cells: %s (%s is %s)", env.padding_cells, start_date.strftime("%b 1"), start_date.strftime("%A"))
    if env.month > 1:
        logging.debug("Mid-year padding: %s cells (one week for alignment)", env.mid_year_padding)
    logging.debug("Cell size: %s x %s mm", env.cell_width / metrics.MM, env.cell_height / metrics.MM)
    logging.debug("Grid: %s columns x %s rows", env.columns, env.rows)

    logging.debug("Creating Cairo Surface and Context")
    logging.debug("width = %sp/%scm, height = %sp/%scm", env.height,
                  env.height / metrics.CM, env.width, env.width / metrics.CM)

    # Create landscape PDF
    surface = drawing.create_surface(env.out, env.height, env.width)
    cr = cairo.Context(surface)

    # Draw the starting year in the padding space (if there is padding)
    if env.padding_cells > 0:
        drawYearLabel(cr, env, env.year, 0, env.padding_cells)

    # Draw all days of the 12-month period
    date = start_date
    ONE_DAY = datetime.timedelta(days=1)
    cell_index = env.padding_cells  # Start after padding
    drew_mid_year_label = False

    while date <= end_date:
        # Check if we're at the year transition (January 1st of next year)
        if env.month > 1 and date.month == 1 and date.day == 1 and date.year == env.year + 1 and not drew_mid_year_label:
            # Draw the new year label in the mid-year padding cells
            if env.mid_year_padding > 0:
                drawYearLabel(cr, env, env.year + 1, cell_index, env.mid_year_padding)
            cell_index += env.mid_year_padding
            drew_mid_year_label = True

        col = cell_index % env.columns
        row = cell_index // env.columns

        x = env.offset_x + (col * env.cell_width)
        y = env.offset_y + (row * env.cell_height)

        # Check if this is the first day of a month
        is_month_start = (date.day == 1)

        drawDay(cr, env, x, y, date, is_month_start)

        date += ONE_DAY
        cell_index += 1

    logging.info("Finished drawing Calendar!")


def drawYearLabel(cr, env, year, start_cell_index, padding_count):
    """Draw the year in big letters in the padding space.

    Args:
        cr: Cairo context
        env: Environment with layout settings
        year: The year number to display
        start_cell_index: The cell index where the padding starts
        padding_count: Number of padding cells available for the label
    """
    with drawing.restoring_transform(cr):
        year_str = str(year)

        # Calculate which row and column the padding starts at
        start_col = start_cell_index % env.columns
        start_row = start_cell_index // env.columns

        # Year label takes up 3 cells width, right-aligned to be adjacent to first day
        label_cells = 3
        label_width = label_cells * env.cell_width
        label_height = env.cell_height

        # Position: right-aligned within the padding area
        padding_width = padding_count * env.cell_width
        label_start_x = env.offset_x + (start_col * env.cell_width) + (padding_width - label_width)
        label_start_y = env.offset_y + (start_row * env.cell_height)

        # Find the largest font size that fits in 3 cells
        font_size = int(label_height * 0.8)
        font = Pango.FontDescription("%s bold %s" % (env.font, font_size))

        # Measure text using ink extents for proper visual centering
        temp_layout = drawing.create_layout_with_kerning(cr)
        temp_layout.set_font_description(font)
        temp_layout.set_text(year_str, -1)
        ink_rect, logical_rect = temp_layout.get_pixel_extents()
        text_width = ink_rect.width
        text_height = ink_rect.height

        # Reduce font size if text is too wide for 3 cells
        while text_width > label_width * 0.9 and font_size > 10:
            font_size -= 2
            font = Pango.FontDescription("%s bold %s" % (env.font, font_size))
            temp_layout.set_font_description(font)
            ink_rect, logical_rect = temp_layout.get_pixel_extents()
            text_width = ink_rect.width
            text_height = ink_rect.height

        # Position: centered within the 3-cell label area
        # ink_rect.x and ink_rect.y are offsets from the layout origin to the ink
        x = label_start_x + (label_width - text_width) / 2 - ink_rect.x
        y = label_start_y + (label_height - text_height) / 2 - ink_rect.y

        # Draw the year
        cr.move_to(x, y)
        with drawing.layout(cr) as layout:
            layout.set_font_description(font)
            layout.set_text(year_str, -1)
            cr.set_source_rgb(0.2, 0.2, 0.2)


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
