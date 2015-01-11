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
from copy import copy

# globale variables
g_options = False # command line options

# pixel to length constants (cairo 72 pixel = 1 inch)
INCH = 72 # 72 pixels (p) = 1 inch (in)
MM = INCH / 25.4 # 25.4 milimeters (mm) = 1 in
CM = INCH / 2.54 # 2.54 centimetes (cm) = 1 in


# Custom optparse options
class CalendarOption (optparse.Option):

	def check_year(option, opt, value):
		# strftime() cannot use years before 1990
		lowerLimit = 1990
		upperLimit = datetime.MAXYEAR

		# in range() the upperLimit is exclusive
		if(int(value) not in range(lowerLimit, upperLimit+1)):
			raise optparse.OptionValueError("option %s: invalid year value: %r (must be integer value in range %u - %u)" % (opt, value, lowerLimit, upperLimit))
		return int(value)

	def check_month(option, opt, value):
		if(int(value) not in range (1, 12+1)):
			raise optparse.OptionValueError("option %s: invalid month value: %r" % (opt, value))
		return int(value)

	TYPES = optparse.Option.TYPES + ("year", "month")
	TYPE_CHECKER = copy(optparse.Option.TYPE_CHECKER)
	TYPE_CHECKER["year"] = check_year
	TYPE_CHECKER["month"] = check_month

class CalendarEnviroment():
	
	def __init__(self, PaperSize):
		try:
			getattr(self, PaperSize)()
		except AttributeError:
			logging.error("Unsupported size of paper")
			sys.exit(1)
		logging.info(self.width)

	def USLetter(self):
		self.width = 8.5 * INCH
		self.height = 11.0 * INCH

	def A4(self):
		self.width = 21.0 * CM
		self.height = 29.7 * CM

	def A3(self):
		self.width = 29.7 * CM
		self.height = 42.0 * CM
	
A4_WIDTH, A4_HEIGHT = INCH * 8.3, INCH * 11.7 # DIN A4 Paper is 297mm heigh and 210mm wide

SAFTY = 5 * MM # safty margin for printing (A4 printers a unable to print on the whole page)
PAGE_WIDTH = 7.425 * CM # width of a folded page
CELL_WIDTH, CELL_HEIGHT = 3.2125 * CM, 2.375 * CM # width and height of a page cell
LINE_WIDTH = 0.01 * CM # line width of the cells

def drawText(cr, text, x, y, fontSize):
	cr.move_to(x, y)
	pc = pangocairo.CairoContext(cr)
	pc.set_antialias(cairo.ANTIALIAS_SUBPIXEL)

	layout = pc.create_layout()
	font = pango.FontDescription("%s %s" % (g_options.font, fontSize))
	layout.set_font_description(font)

	layout.set_text(text)
	logging.debug("text: '%s' font size: %s pixel_size: %s", text,fontSize, layout.get_pixel_size())
	cr.set_source_rgb(0, 0, 0)
	pc.update_layout(layout)
	pc.show_layout(layout)

def drawMonthTitle(cr, x, y, width, height, dateObject):
	# preparing month string
	style = "%B"
	if(g_options.abbreviate_all):
		style="%b"
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
		font = pango.FontDescription("%s %s" % (g_options.font, fontSize))
		layout.set_font_description(font)
		logging.debug("font size: %s pixel_size: %s",fontSize, layout.get_pixel_size())
		if(layout.get_pixel_size()[0] <= CELL_WIDTH):
			fits=True
		else:
			fontSize-=1

	# preparing cairo context
	y += ((CELL_HEIGHT / 2) - (layout.get_pixel_size()[1]/2))
	cr.move_to(x, y)
	cr.set_source_rgb(0, 0, 0)

	# drawing pango text
	pc.update_layout(layout)
	pc.show_layout(layout)

def drawDay(cr, x, y, width, height, lineWidth, dateObject):
	# font size in pixels
	FONTSIZE = 6

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
	OFFSET_X, OFFSET_Y = math.floor(FONTSIZE * 0.3333), math.floor(FONTSIZE * 0.3333)
	
	style = "%A"
	if(g_options.abbreviate or g_options.abbreviate_all):
		style = "%a"
	dayString = "%s %s" % (dateObject.day, dateObject.strftime(style))
	drawText(cr, dayString, x+OFFSET_X,y+OFFSET_Y, FONTSIZE)

def drawMonth(cr, year, month):
	# Creating a new date object with the first day of the month to draw
	date = datetime.date(year, month, 1)
	logging.info("drawing %s...", date.strftime("%B %Y"))

	# Defining a one day timedelta object to increase the date object
	one_day = datetime.timedelta(days=1)

	# draw month name in first cell
	drawMonthTitle(cr, SAFTY, SAFTY, CELL_WIDTH, CELL_HEIGHT, date)

	cellsOnPage = 1
	cellsOnPageMax = 8
	page = 0
	row = 1
	column = 0
	# for every day of the month
	while month == date.month:

		# positions on page
		x = SAFTY + (page * PAGE_WIDTH) + (column * CELL_WIDTH)
		y = SAFTY + (row * CELL_HEIGHT)

		# draw day
		drawDay(cr, x, y, CELL_WIDTH, CELL_HEIGHT, LINE_WIDTH, date)

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

def drawCalendar():
	logging.debug("Creating Cario Surface and Context")
	logging.debug("width = %sp/%scm, height = %sp/%scm", A4_HEIGHT, A4_HEIGHT / CM, A4_WIDTH, A4_WIDTH / CM)
	surface = cairo.PDFSurface(g_options.out, A4_HEIGHT, A4_WIDTH)
	cr = cairo.Context(surface)

	today = datetime.date.today()
	logging.info("drawing calendar...")
	logging.info("assuming today is %s.%s.%s",today.day,today.month,today.year)

	# draw first month
	monthToDraw = g_options.month
	yearToDraw = g_options.year
	cr.save()
	cr.translate(A4_HEIGHT, A4_WIDTH/2)
	cr.rotate(math.pi)
	drawMonth(cr, yearToDraw, monthToDraw)
	cr.restore()

	# draw second month
	cr.save()
	cr.translate(0, A4_WIDTH/2)

	# check if last month was december
	# if so set month to january and increment year
	if(monthToDraw == 12):
		monthToDraw = 1
		yearToDraw += 1
	else:
		monthToDraw += 1
	drawMonth(cr, yearToDraw, monthToDraw)
	cr.restore()

	cr.save()
	drawText(cr, g_options.brand, A4_HEIGHT - PAGE_WIDTH + SAFTY, A4_WIDTH / 2 + 3, 6)
	cr.translate(A4_HEIGHT, A4_WIDTH/2)
	cr.rotate(math.pi)
	drawText(cr, g_options.brand, A4_HEIGHT - PAGE_WIDTH + SAFTY, 0 + 3, 6)
	cr.restore()

	logging.info("Finished drawing Calendar!")

def main():
	# SetUp OptionParser
	parser = optparse.OptionParser(option_class=CalendarOption)
	
	parser.add_option("-A", "--abbreviate_all", action="store_true", 
					help="use abbreviations for weekdays and months", default=False)
	
	parser.add_option("-a", "--abbreviate", action="store_true", 
					help="use abbreviations for weekdays", default=False)
	
	parser.add_option("-b", "--brand", type="string",
					help="assign a brand string", default="")
	
	parser.add_option("-d", "--debug", action="store_true",
					help="print status and debug messages to stdout", default=False)
	
	font_map = pangocairo.cairo_font_map_get_default()
	parser.add_option("-f", "--font", type="choice", choices=[f.get_name() for f in font_map.list_families()], help="choose which font to use", default="Sans")
	
	parser.add_option("-l", "--locale", type="string",
					help="choose locale to use (default en_US.UTF8, check 'locale -a' for available locales)", default="en_US.UTF8")
	
	# create date object to set default month and year to today
	td = datetime.date.today()
	parser.add_option("-m", "--month", type="month",
					help="specify the starting month as a number (1-12), default is the current month ("+str(td.month)+").", default=td.month)
	
	parser.add_option("-o", "--out", dest="out", type="string",
					help="specify output file", default="out.pdf")

	# currently supported sizes of paper
	paperSizes = ("A4","A3","USLetter")
	parser.add_option("-p", "--paper", type="choice", choices=paperSizes, help="choose which paper dimensions should be used "+str(paperSizes)+" default is A4", default="A4")

	parser.add_option("-v", "--verbose", action="store_true",
					help="print status messages to stdout", default=False)

	parser.add_option("-y", "--year", type="year",
					help="specify the year the calendar should start, default is the current year ("+str(td.year)+").", default=td.year)
	
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

	env = CalendarEnviroment(g_options.paper)
	drawCalendar()

	return 0

if __name__ == "__main__":
    sys.exit(main())
