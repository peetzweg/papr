#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import locale
import math
import cairo
import optparse
import datetime
import logging

# Constants
# A4 Width and Height for PDF Surface - 1p = 1/72in
INCH = 72
MM = INCH/25.4
CM = INCH/2.54
A4_WIDTH, A4_HEIGHT = INCH*8.3, INCH*11.7

def drawMonthTitle(cr, x, y, width, height, date):
	cr.set_source_rgb(0, 0, 0)
	cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
	cr.set_font_size(height/2)

	cr.move_to(x, y+(height/2))
	cr.show_text(date.strftime("%B"))

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
	cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
	cr.set_font_size(10)
	OFFSET_X, OFFSET_Y = math.floor(FONTSIZE*0.3333),FONTSIZE
	cr.move_to((x+OFFSET_X), (y+OFFSET_Y))

	dayText = "%s %s" % (dateObject.day, dateObject.strftime("%A"))
	cr.show_text(dayText)

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
					help="choose lacal to use (default en_US.UTF8, check 'locale -a' for available locales)", default="en_US.UTF8")
	parser.add_option("-a", "--abbreviation", action="store_false",
					help="use abbreviations of months and weekdays", default=False)
	parser.add_option("-v", "--verbose", action="store_true",
					help="print status messages to stdout", default=False)
	parser.add_option("-d", "--debug", action="store_true",
					help="print status and debug messages to stdout", default=False)
	(options, arguments) = parser.parse_args()

	# defining output
	if(options.debug):
		logging.basicConfig(format='%(message)s', level="DEBUG")
		# Printing Options for Debugging
		for option in parser.option_list:
			if(option.dest != None):
				logging.debug("%s = %s", option, getattr(options, option.dest))
	elif(options.verbose):
		logging.basicConfig(format='%(message)s', level="INFO")

	# setting locale
	try:
		logging.debug("setting locale to '%s'", options.locale)
		locale.setlocale(locale.LC_ALL, options.locale)
	except locale.Error:
		logging.error("Unsupported locale:'%s'!\nList all supported locales with 'locale -a'",options.locale)
		sys.exit(1)

	logging.debug("Creating Cario Surface and Context")
	logging.debug("width=%sp/%scm, height=%sp/%scm", A4_HEIGHT, A4_HEIGHT/CM, A4_WIDTH, A4_WIDTH/CM)
	surface = cairo.PDFSurface(options.out, A4_HEIGHT, A4_WIDTH)
	cr = cairo.Context(surface)

	drawCalendar(cr)
	logging.info("Finished drawing Calendar!")

	return 0

if __name__ == "__main__":
    sys.exit(main())
