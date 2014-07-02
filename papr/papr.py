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


# globale variables
g_options = False # command line options

# constants
INCH = 72 # 72 pixels (p) = 1 inch (in)
MM = INCH / 25.4 # 25.4 milimeters (mm) = 1 in
CM = INCH / 2.54 # 2.54 centimetes (cm) = 1 in
A4_WIDTH, A4_HEIGHT = INCH * 8.3, INCH * 11.7 # DIN A4 Paper is 297mm heigh and 210mm wide

SAFTY = 5 * MM # print safty margin 
PAGE_WIDTH = 7.425 * CM # width of a folded page
CELL_WIDTH, CELL_HEIGHT = 3.2125 * CM, 2.375 * CM # width and height of a page cell
LINE_WIDTH = 0.01 * CM # line width of the cells

def drawBranding(cr, x, y):
	cr.save()
	height=24
	width=CELL_WIDTH-12
	image_surface = cairo.ImageSurface.create_from_png("branding.png")
	img_height = image_surface.get_height()
	img_width = image_surface.get_width()
	width_ratio = float(width) / float(img_width)
	height_ratio = float(height) / float(img_height)
	scale_xy = min(height_ratio, width_ratio)
	# scale image and add it
	cr.translate(x,y)
	cr.scale(scale_xy, scale_xy)
	cr.set_source_surface(image_surface)
	cr.paint()
	cr.restore()

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
		cr.set_source_rgba(0.95, 0.95, 0.95, 1.0)
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
		row=math.floor(cellsOnPage / 2)

		# positions on page
		x = SAFTY + (page * PAGE_WIDTH)
		y = SAFTY + (row * CELL_HEIGHT)

		# add cell width if date is odd
		if(date.day % 2 != 0):
			x += CELL_WIDTH

		# draw day
		drawDay(cr, x, y, CELL_WIDTH, CELL_HEIGHT, LINE_WIDTH, date)

		# increment cell counter
		cellsOnPage += 1

		# increment date by one day
		date += one_day

		# if more than 8 cells on page
		if(cellsOnPage >= cellsOnPageMax):
			# reset cells on page counter
			cellsOnPage = 0
			# increment page counter
			page += 1

def drawCalendar():
	logging.debug("Creating Cario Surface and Context")
	logging.debug("width = %sp/%scm, height = %sp/%scm", A4_HEIGHT, A4_HEIGHT / CM, A4_WIDTH, A4_WIDTH / CM)
	surface = cairo.PDFSurface(g_options.out, A4_HEIGHT, A4_WIDTH)
	cr = cairo.Context(surface)

	today = datetime.date.today()
	logging.info("drawing calendar...")
	logging.info("assuming today is %s.%s.%s",today.day,today.month,today.year)

	# draw first month
	cr.save()
	cr.translate(A4_HEIGHT, A4_WIDTH/2)
	cr.rotate(math.pi)
	drawMonth(cr, today.year, today.month)
	drawBranding(cr, SAFTY, SAFTY)
	cr.restore()

	# draw second month
	cr.save()
	cr.translate(0, A4_WIDTH/2)
	drawMonth(cr, today.year, today.month + 1)
	drawBranding(cr, SAFTY, SAFTY)
	cr.restore()

	logging.info("Finished drawing Calendar!")

def main():
	# SetUp OptionParser
	parser = optparse.OptionParser()
	parser.add_option("-o", "--out", dest="out",
					help="specify output file", default="papr.pdf")
	parser.add_option("-l", "--locale",
					help="choose locale to use (default en_US.UTF8, check 'locale -a' for available locales)", default="en_US.UTF8")
	parser.add_option("-a", "--abbreviate", action="store_true", 
					help="use abbreviations for weekdays", default=False)
	parser.add_option("-A", "--abbreviate_all", action="store_true", 
					help="use abbreviations for weekdays and months", default=False)
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

	drawCalendar()

	return 0

if __name__ == "__main__":
    sys.exit(main())
