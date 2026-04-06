use crate::canvas::Canvas;
use crate::config::{Config, Orientation, PageSetup};

pub mod big;
pub mod classic;
pub mod column;
pub mod month;
pub mod oneyear;

/// Every layout implements this trait.
pub trait Layout {
    /// What orientation does this layout need?
    fn orientation(&self) -> Orientation;

    /// Draw the calendar onto the canvas.
    fn draw(&self, canvas: &Canvas, config: &Config, page: &PageSetup);
}

/// All available layout names.
pub const LAYOUT_NAMES: &[&str] = &["big", "classic", "column", "month", "oneyear"];

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn column_is_landscape() {
        let layout = column::ColumnLayout {
            abbreviate: false,
            abbreviate_all: false,
        };
        assert_eq!(layout.orientation(), Orientation::Landscape);
    }
}
