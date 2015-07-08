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
	cr.move_to(x+dimensions[0]+fontSize/2, y)
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
		font = pango.FontDescription("%s %s" % (env.font, fontSize))
		layout.set_font_description(font)
		logging.debug("font size: %s pixel_size: %s",fontSize, layout.get_pixel_size())
		if(layout.get_pixel_size()[0] <= env.cell_width):
			fits=True
		else:
			fontSize-=1

	# preparing cairo context
	y += ((env.cell_height / 2) - (layout.get_pixel_size()[1]/2))
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
	OFFSET_X, OFFSET_Y = math.floor(env.font_size * 0.3333), math.floor(env.font_size * 0.3333)
	
	style = "%A"
	if(env.abbreviate or env.abbreviate_all):
		style = "%a"
	dayString = "%s %s" % (dateObject.day, dateObject.strftime(style))
	drawText(cr, env, dayString, x+OFFSET_X,y+OFFSET_Y, env.font_size)

def drawMonth(cr, env, year, month):

	# Creating a new date object with the first day of the month to draw
	date = datetime.date(year, month, 1)
	logging.info("drawing %s...", date.strftime("%B %Y"))

	# Defining a one day timedelta object to increase the date object
	one_day = datetime.timedelta(days=1)

	# draw month name in first cell
	drawMonthTitle(cr, env, env.safety, env.safety, env.cell_width, env.cell_height, date)

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
		drawDay(cr, env, x, y, env.cell_width, env.cell_height, env.line_width, date)

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

def drawCalendar(env):
	logging.debug("Creating Cario Surface and Context")
	logging.debug("width = %sp/%scm, height = %sp/%scm", env.height, env.height / CM, env.width, env.width / CM)
	surface = cairo.PDFSurface(env.out, env.height, env.width)
	cr = cairo.Context(surface)

	today = datetime.date.today()
	logging.info("drawing calendar...")
	logging.info("assuming today is %s.%s.%s",today.day,today.month,today.year)

	# draw first month
	monthToDraw = env.month
	yearToDraw = env.year
	cr.save()
	cr.translate(env.height, env.width/2)
	cr.rotate(math.pi)
	drawMonth(cr, env, yearToDraw, monthToDraw)
	cr.restore()

	# draw second month
	cr.save()
	cr.translate(0, env.width/2)

	# check if last month was december
	# if so set month to january and increment year
	if(monthToDraw == 12):
		monthToDraw = 1
		yearToDraw += 1
	else:
		monthToDraw += 1
	drawMonth(cr, env, yearToDraw, monthToDraw)
	cr.restore()

	if(env.brand !=""):
		cr.save()
		drawText(cr, env, env.brand, env.height - env.page_width + env.safety, env.width / 2 + 3, 6)
		cr.translate(env.height, env.width/2)
		cr.rotate(math.pi)
		drawText(cr, env, env.brand, env.height - env.page_width + env.safety, 0 + 3, 6)
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

	parser.add_option("-c", "--color", action="store_true",
					help="color date numbers", default=False)

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

	parser.add_option("--margin", type="int",
					help="specify the margin of the calendar in millimeters. Used to adapt to your printer, default ist 5mm" , default=5)
	
	parser.add_option("-o", "--out", dest="out", type="string",
					help="specify output file", default="out.pdf")

	# currently supported sizes of paper
	paperSizes = ("A4","A3","USLetter")
	parser.add_option("-p", "--paper", type="choice", choices=paperSizes, help="choose which paper dimensions should be used "+str(paperSizes)+" default is A4", default="A4")

	parser.add_option("-v", "--verbose", action="store_true",
					help="print status messages to stdout", default=False)

	parser.add_option("-y", "--year", type="year",
					help="specify the year the calendar should start, default is the current year ("+str(td.year)+").", default=td.year)
	
	(enviroment, arguments) = parser.parse_args()

	# defining output
	if(enviroment.debug):
		logging.basicConfig(format='%(message)s', level="DEBUG")
		# Printing Options for Debugging
		for option in parser.option_list:
			if(option.dest != None):
				logging.debug("%s = %s", option, getattr(enviroment, option.dest))
	elif(enviroment.verbose):
		logging.basicConfig(format='%(message)s', level="INFO")

	# setting locale
	try:
		logging.debug("setting locale to '%s'", enviroment.locale)
		locale.setlocale(locale.LC_ALL, enviroment.locale)
	except locale.Error:
		logging.error("Unsupported locale: '%s'!\nList all supported locales with 'locale -a'", enviroment.locale)
		sys.exit(1)

	logging.debug("Adjusting width and height values according to desired paper format: "+enviroment.paper)
	if(enviroment.paper=="A4"):
		enviroment.width = 21.0 * CM
		enviroment.height = 29.7 * CM
		enviroment
	elif(enviroment.paper=="A3"):
		enviroment.width = 29.7 * CM
		enviroment.height = 42.0 * CM
	elif(enviroment.paper=="USLetter"):
		enviroment.width = 8.5 * INCH
		enviroment.height = 11.0 * INCH


	# adding aditional information to enviroment
	enviroment.safety = enviroment.margin * MM # env.safety margin for printing (A4 printers a unable to print on the whole page)
	enviroment.page_width = enviroment.height / 4.0 # 4 pages in landscape
	
	enviroment.cell_width = (enviroment.page_width - 2.0 * enviroment.safety) / 2
	enviroment.cell_height = (enviroment.width / 8.0) - ((2 * enviroment.safety) / 4.0)
	enviroment.line_width = 0.01 * CM
	enviroment.font_size = 6

	drawCalendar(enviroment)

	return 0

if __name__ == "__main__":
    sys.exit(main())
