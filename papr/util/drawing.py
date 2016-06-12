from gi.repository import PangoCairo
from contextlib import contextmanager

@contextmanager
def layout(cr):
    layout = PangoCairo.create_layout(cr)
    yield layout
    PangoCairo.update_layout(cr, layout)
    PangoCairo.show_layout(cr, layout)

@contextmanager
def restoring_transform(cr):
    cr.save()
    yield
    cr.restore()
