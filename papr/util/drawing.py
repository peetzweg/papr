import os
import logging

import cairo
from gi.repository import Pango
from gi.repository import PangoCairo
from contextlib import contextmanager


def create_surface(filename, width, height):
    """
    Create a Cairo surface based on the output file extension.
    
    Supports:
    - .pdf: PDFSurface (default)
    - .svg: SVGSurface
    
    Both surfaces use the same coordinate system (points) and produce
    visually identical output for the same drawing commands.
    
    Args:
        filename: Output file path (format detected from extension)
        width: Surface width in points
        height: Surface height in points
    
    Returns:
        A Cairo surface (PDFSurface or SVGSurface)
    """
    ext = os.path.splitext(filename)[1].lower()
    
    if ext == '.svg':
        logging.debug("Creating SVG surface: %s", filename)
        surface = cairo.SVGSurface(filename, width, height)
        # Set document unit to points for consistency with PDF
        # This ensures dimensions in the SVG match PDF coordinates exactly
        surface.set_document_unit(cairo.SVGUnit.PT)
        return surface
    else:
        # Default to PDF for .pdf or any other extension
        logging.debug("Creating PDF surface: %s", filename)
        return cairo.PDFSurface(filename, width, height)


def create_layout_with_kerning(cr):
    """Create a Pango layout with proper OpenType font features enabled (kerning, ligatures)."""
    layout = PangoCairo.create_layout(cr)

    # Enable OpenType font features for better typography
    # kern=1: enable kerning
    # liga=1: enable standard ligatures
    attr_list = Pango.AttrList()
    font_features = Pango.attr_font_features_new("kern=1,liga=1")
    font_features.start_index = 0
    font_features.end_index = 0xFFFFFFFF  # Apply to entire text (max uint32)
    attr_list.insert(font_features)
    layout.set_attributes(attr_list)

    return layout


@contextmanager
def layout(cr):
    """Context manager for creating and rendering a Pango layout with kerning enabled."""
    layout = create_layout_with_kerning(cr)
    yield layout
    PangoCairo.update_layout(cr, layout)
    PangoCairo.show_layout(cr, layout)


@contextmanager
def restoring_transform(cr):
    cr.save()
    yield
    cr.restore()
