from gi.repository import Pango
from gi.repository import PangoCairo
from contextlib import contextmanager


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
