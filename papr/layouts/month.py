#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Month Layout - Single month calendar on a portrait page.
Top 1/3: Year (small) and month abbreviation (large).
Bottom 2/3: 7-column grid (Mon-Sun) with weekday headers.
"""

import calendar
import datetime
import logging

import cairo
from gi.repository import Pango

from papr.util import drawing, metrics, styles


def drawCalendar(env):
    logging.debug(
        "Adding additional information to environment specific to Month layout"
    )

    # Portrait orientation - use dimensions as-is
    page_width = env.width
    page_height = env.height

    # Available area after margins
    available_width = page_width - (2 * env.safety)
    available_height = page_height - (2 * env.safety)

    # Split page: 1/3 header, 2/3 grid
    env.header_height = available_height / 3
    env.grid_height = available_height * 2 / 3

    # Grid setup: 7 columns (Mon-Sun)
    env.columns = 7

    # Calculate rows needed (max 6 weeks + 1 header row)
    env.header_row_height = env.grid_height * 0.08  # weekday header row
    env.grid_content_height = env.grid_height - env.header_row_height
    env.rows = 6  # max weeks in a month view
    env.cell_width = available_width / env.columns
    env.cell_height = env.grid_content_height / env.rows

    # Offsets
    env.offset_x = env.safety
    env.header_offset_y = env.safety
    env.weekday_header_y = env.safety + env.header_height
    env.grid_offset_y = env.weekday_header_y + env.header_row_height

    # Style settings from central config
    env.line_width = styles.BORDER_WIDTH * metrics.MM
    env.border_color = styles.BORDER_COLOR
    env.weekend_bg_color = styles.WEEKEND_BG_COLOR
    env.text_color_primary = styles.TEXT_COLOR_PRIMARY
    env.text_color_secondary = styles.TEXT_COLOR_SECONDARY
    env.text_color_muted = styles.TEXT_COLOR_MUTED

    # Font sizes
    env.day_text_size = 8
    env.weekday_header_font_size = env.header_row_height * 0.5

    logging.debug("Page: %s x %s mm", page_width / metrics.MM, page_height / metrics.MM)
    logging.debug("Header height: %s mm", env.header_height / metrics.MM)
    logging.debug("Grid: %s cols x %s rows", env.columns, env.rows)
    logging.debug(
        "Cell size: %s x %s mm",
        env.cell_width / metrics.MM,
        env.cell_height / metrics.MM,
    )

    # Create PDF surface (portrait)
    surface = drawing.create_surface(env.out, page_width, page_height)
    cr = cairo.Context(surface)

    # Draw components
    date = datetime.date(env.year, env.month, 1)
    drawHeader(cr, env, date)
    drawWeekdayHeaders(cr, env)
    drawDaysGrid(cr, env, date)

    logging.info("Finished drawing Calendar!")


def drawHeader(cr, env, date):
    """Draw year (small) and month abbreviation (large) in top 1/3."""
    with drawing.restoring_transform(cr):
        year_str = str(date.year)
        month_str = date.strftime("%b").upper()

        # Calculate font sizes - month is 5x year
        # Start with month taking ~60% of header height
        month_font_size = int(env.header_height * 0.5)
        year_font_size = int(month_font_size / 5)

        year_font = Pango.FontDescription("%s bold %s" % (env.font, year_font_size))
        month_font = Pango.FontDescription("%s bold %s" % (env.font, month_font_size))

        # Measure year text
        year_layout = drawing.create_layout_with_kerning(cr)
        year_layout.set_font_description(year_font)
        year_layout.set_text(year_str, -1)
        year_width, year_height = year_layout.get_pixel_size()

        # Measure month text
        month_layout = drawing.create_layout_with_kerning(cr)
        month_layout.set_font_description(month_font)
        month_layout.set_text(month_str, -1)
        month_width, month_height = month_layout.get_pixel_size()

        # Center horizontally
        available_width = env.width - (2 * env.safety)
        center_x = env.offset_x + available_width / 2

        # Center month in header area (vertically and horizontally)
        month_y = env.header_offset_y + (env.header_height - month_height) / 2
        month_x = center_x - month_width / 2

        # Place year above month with fixed padding
        year_month_gap = year_height * 0.3
        year_y = month_y - year_month_gap - year_height
        year_x = center_x - year_width / 2

        # Ensure year doesn't go above the top margin
        if year_y < env.header_offset_y:
            year_y = env.header_offset_y

        # Draw year (above month)
        cr.move_to(year_x, year_y)
        with drawing.layout(cr) as layout:
            layout.set_font_description(year_font)
            layout.set_text(year_str, -1)
            cr.set_source_rgb(*env.text_color_muted)

        # Draw month (centered in header)
        cr.move_to(month_x, month_y)
        with drawing.layout(cr) as layout:
            layout.set_font_description(month_font)
            layout.set_text(month_str, -1)
            cr.set_source_rgb(*env.text_color_primary)


def drawWeekdayHeaders(cr, env):
    """Draw weekday abbreviations as column headers (MON TUE WED THU FRI SAT SUN)."""
    weekdays = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

    font = Pango.FontDescription(
        "%s bold %s" % (env.font, int(env.weekday_header_font_size))
    )

    for col, day_name in enumerate(weekdays):
        x = env.offset_x + (col * env.cell_width)
        y = env.weekday_header_y

        with drawing.restoring_transform(cr):
            cr.translate(x, y)

            # Measure text for centering
            temp_layout = drawing.create_layout_with_kerning(cr)
            temp_layout.set_font_description(font)
            temp_layout.set_text(day_name, -1)
            text_width, text_height = temp_layout.get_pixel_size()

            # Center in cell
            text_x = (env.cell_width - text_width) / 2
            text_y = (env.header_row_height - text_height) / 2

            cr.move_to(text_x, text_y)
            with drawing.layout(cr) as layout:
                layout.set_font_description(font)
                layout.set_text(day_name, -1)
                # Weekend headers slightly different color
                if col >= 5:
                    cr.set_source_rgb(*env.text_color_secondary)
                else:
                    cr.set_source_rgb(*env.text_color_primary)


def drawDaysGrid(cr, env, first_of_month):
    """Draw the days grid with date numbers and week numbers."""
    # Find first day position (Monday = 0)
    first_weekday = first_of_month.weekday()

    # Get number of days in month
    days_in_month = calendar.monthrange(first_of_month.year, first_of_month.month)[1]

    ONE_DAY = datetime.timedelta(days=1)
    date = first_of_month

    for day in range(1, days_in_month + 1):
        # Calculate cell position
        day_offset = first_weekday + day - 1
        col = day_offset % 7
        row = day_offset // 7

        x = env.offset_x + (col * env.cell_width)
        y = env.grid_offset_y + (row * env.cell_height)

        # Check if Monday (start of week) - show week number
        is_monday = date.weekday() == 0

        drawDayCell(cr, env, x, y, date, is_monday)
        date += ONE_DAY


def drawDayCell(cr, env, x, y, date, show_week_number):
    """Draw a single day cell with date number (top-right) and week number (top-left)."""
    with drawing.restoring_transform(cr):
        cr.translate(x, y)

        # Fill background for weekends
        if date.isoweekday() >= 6:
            cr.rectangle(0, 0, env.cell_width, env.cell_height)
            cr.set_source_rgba(*env.weekend_bg_color, 1.0)
            cr.fill()

        # Stroke cell border
        cr.set_source_rgba(*env.border_color, 1.0)
        cr.set_line_width(env.line_width)
        cr.rectangle(0, 0, env.cell_width, env.cell_height)
        cr.stroke()

        font_size = env.day_text_size
        padding = font_size * 0.5

        font = Pango.FontDescription("%s %s" % (env.font, font_size))
        font_bold = Pango.FontDescription("%s bold %s" % (env.font, font_size))

        # Draw day number in top-right corner
        day_str = str(date.day)

        day_layout = drawing.create_layout_with_kerning(cr)
        day_layout.set_font_description(font_bold)
        day_layout.set_text(day_str, -1)
        day_width, _ = day_layout.get_pixel_size()

        day_x = env.cell_width - padding - day_width

        with drawing.layout(cr) as layout:
            layout.set_font_description(font_bold)
            layout.set_text(day_str, -1)
            cr.move_to(day_x, padding)
            cr.set_source_rgb(*env.text_color_primary)

        # Draw week number in top-left corner (Monday only)
        if show_week_number:
            iso_week = date.isocalendar()[1]
            week_str = str(iso_week)

            with drawing.layout(cr) as layout:
                layout.set_font_description(font)
                layout.set_text(week_str, -1)
                cr.move_to(padding, padding)
                cr.set_source_rgb(*env.text_color_secondary)
