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

/// Look up a layout by name.
pub fn get_layout(name: &str) -> Option<Box<dyn Layout>> {
    match name {
        "big" => Some(Box::new(big::BigLayout)),
        "classic" => Some(Box::new(classic::ClassicLayout)),
        "column" => Some(Box::new(column::ColumnLayout)),
        "month" => Some(Box::new(month::MonthLayout)),
        "oneyear" => Some(Box::new(oneyear::OneYearLayout)),
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn known_layouts_resolve() {
        for name in LAYOUT_NAMES {
            assert!(
                get_layout(name).is_some(),
                "Layout '{name}' should be registered"
            );
        }
    }

    #[test]
    fn unknown_layout_returns_none() {
        assert!(get_layout("nonexistent").is_none());
    }

    #[test]
    fn column_is_landscape() {
        let layout = get_layout("column").unwrap();
        assert_eq!(layout.orientation(), Orientation::Landscape);
    }
}
