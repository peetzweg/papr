#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import locale
import math
import cairo
import pango
import pangocairo
import optparse
import datetime
import logging

# Constants
# A4 Width and Height for PDF Surface - 1p = 1/72in
INCH = 72
MM = INCH/25.4
CM = INCH/2.54
A4_WIDTH, A4_HEIGHT = INCH*8.3, INCH*11.7

# Global variables for g_options
g_options = False

def drawText(cr, text, x, y, fontSize):
	cr.move_to(x, y)
	pc = pangocairo.CairoContext(cr)
	pc.set_antialias(cairo.ANTIALIAS_SUBPIXEL)

	layout = pc.create_layout()
	font = pango.FontDescription("%s %s" % (g_options.font, fontSize))
	layout.set_font_description(font)

	layout.set_text(text)
	cr.set_source_rgb(0, 0, 0)
	pc.update_layout(layout)
	pc.show_layout(layout)

def drawMonthTitle(cr, x, y, width, height, dateObject):
#	cr.move_to(x, y+(height/2))
	style = "%B"
	if(g_options.abbreviate):
		style="%b"
	monthString = dateObject.strftime(style)
	drawText(cr,monthString, x, y, math.floor(height/3))


def drawDay(cr, x, y, width, height, lineWidth, dateObject):
	# font size in pixels
	FONTSIZE=12

	# fill box if weekend
	if(dateObject.isoweekday() >= 6):
		cr.rectangle(x, y, width, height)
		cr.set_source_rgba(0.95, 0.95, 0.95, 1.0)
		cr.fill()

	# drawing the box
	cr.set_source_rgba(0, 0, 0, 1.0)
	cr.set_line_width(lineWidth)
	cr.rectangle(x, y, width, height)
	cr.stroke()

	# drawing the text
	cr.set_source_rgb(0, 0, 0)
	cr.select_font_face(g_options.font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
	cr.set_font_size(10)
	OFFSET_X, OFFSET_Y = math.floor(FONTSIZE*0.3333),FONTSIZE
	cr.move_to((x+OFFSET_X), (y+OFFSET_Y))
	
	style = "%A"
	if(g_options.abbreviate):
		style = "%a"
	dayString = "%s %s" % (dateObject.day, dateObject.strftime(style))
	cr.show_text(dayString)

def drawMonth(cr, year, month):
	# constants
	SAFTY = 5*MM
	PAGE_WIDTH = 7.425*CM
	CELL_WIDTH, CELL_HEIGHT = 3.2125*CM, 2.375*CM
	LINE_WIDTH = 0.03*CM

	# Creating a new date object with the first day of the month to draw
	date = datetime.date(year, month, 1)
	logging.info("drawing %s...", date.strftime("%B"))

	# Defining a one day timedelta object to increase the date object
	one_day = datetime.timedelta(days=1)

	# draw month name in first cell
	drawMonthTitle(cr, SAFTY, SAFTY, CELL_WIDTH, CELL_HEIGHT, date)

	cellsOnPage = 1
	cellsOnPageMax = 8
	page = 0
	# for every day of the month
	while month == date.month:
		row=math.floor(cellsOnPage/2)

		# positions on page
		x=SAFTY+(page*PAGE_WIDTH)
		y=SAFTY+(row*CELL_HEIGHT)

		# add cell width if date is odd
		if(date.day%2!=0):
			x += CELL_WIDTH

		# draw day
		drawDay(cr, x, y, CELL_WIDTH, CELL_HEIGHT, LINE_WIDTH, date)

		# increment cell counter
		cellsOnPage+=1

		# increment date by one day
		date += one_day

		# if more than 8 cells on page
		if(cellsOnPage>=cellsOnPageMax):
			# reset cells on page counter
			cellsOnPage=0
			# increment page counter
			page+=1

def drawCalendar(cr):
	today = datetime.date.today()
	logging.info("drawing calendar...")
	logging.info("assuming today is %s.%s.%s",today.day,today.month,today.year)

	# draw first month
	cr.translate(A4_HEIGHT,A4_WIDTH/2)
	cr.rotate(math.pi)
	drawMonth(cr, today.year, today.month)

	# draw second month
	cr.translate(A4_HEIGHT, 0)
	cr.rotate(math.pi)
	drawMonth(cr, today.year, today.month+1)

def main():
	# SetUp OptionParser
	parser = optparse.OptionParser()
	parser.add_option("-o", "--out", dest="out",
					help="specify output file", default="papr.pdf")
	parser.add_option("-l", "--locale",
					help="choose locale to use (default en_US.UTF8, check 'locale -a' for available locales)", default="en_US.UTF8")
	parser.add_option("-a", "--abbreviate", action="store_true", 
					help="use abbreviations of months and weekdays", default=False)
	parser.add_option("-f", "--font",
					help="choose which font to use", default="Sans")
	parser.add_option("-v", "--verbose", action="store_true",
					help="print status messages to stdout", default=False)
	parser.add_option("-d", "--debug", action="store_true",
					help="print status and debug messages to stdout", default=False)
	global g_options
	(g_options, arguments) = parser.parse_args()

	# defining output
	if(g_options.debug):
		logging.basicConfig(format='%(message)s', level="DEBUG")
		# Printing Options for Debugging
		for option in parser.option_list:
			if(option.dest != None):
				logging.debug("%s = %s", option, getattr(g_options, option.dest))
	elif(g_options.verbose):
		logging.basicConfig(format='%(message)s', level="INFO")

	# setting locale
	try:
		logging.debug("setting locale to '%s'", g_options.locale)
		locale.setlocale(locale.LC_ALL, g_options.locale)
	except locale.Error:
		logging.error("Unsupported locale: '%s'!\nList all supported locales with 'locale -a'",g_options.locale)
		sys.exit(1)

	# check if selected font is available
	font_map = pangocairo.cairo_font_map_get_default()
	if(g_options.font not in [f.get_name() for f in   font_map.list_families()]):
		logging.error("Unsupported font: '%s'!\nInstalled fonts are:\n%s", g_options.font, [f.get_name() for f in   font_map.list_families()])
		sys.exit(1)


	logging.debug("Creating Cario Surface and Context")
	logging.debug("width = %sp/%scm, height = %sp/%scm", A4_HEIGHT, A4_HEIGHT/CM, A4_WIDTH, A4_WIDTH/CM)
	surface = cairo.PDFSurface(g_options.out, A4_HEIGHT, A4_WIDTH)
	cr = cairo.Context(surface)

	drawCalendar(cr)
	logging.info("Finished drawing Calendar!")

	return 0

if __name__ == "__main__":
    sys.exit(main())
