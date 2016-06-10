from gi.repository import PangoCairo
from contextlib import contextmanager

@contextmanager
def layout_draw(cr):
    layout = PangoCairo.create_layout(cr)
    yield layout
    PangoCairo.update_layout(cr, layout)
    PangoCairo.show_layout(cr, layout)
