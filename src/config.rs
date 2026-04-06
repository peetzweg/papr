/// Points per inch — Cairo's native unit.
pub const INCH: f64 = 72.0;
/// Points per millimeter.
pub const MM: f64 = INCH / 25.4;
/// Points per centimeter.
pub const CM: f64 = INCH / 2.54;

/// Supported paper sizes.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum PaperSize {
    A5,
    A4,
    A3,
    A2,
    A1,
    A0,
    UsLetter,
    UsTabloid,
    UsLedger,
}

impl PaperSize {
    /// Returns (short_edge, long_edge) in points. Always portrait orientation.
    pub fn dimensions_pt(self) -> (f64, f64) {
        match self {
            PaperSize::A5 => (14.8 * CM, 21.0 * CM),
            PaperSize::A4 => (21.0 * CM, 29.7 * CM),
            PaperSize::A3 => (29.7 * CM, 42.0 * CM),
            PaperSize::A2 => (42.0 * CM, 59.4 * CM),
            PaperSize::A1 => (59.4 * CM, 84.1 * CM),
            PaperSize::A0 => (84.1 * CM, 118.9 * CM),
            PaperSize::UsLetter => (8.5 * INCH, 11.0 * INCH),
            PaperSize::UsTabloid => (11.0 * INCH, 17.0 * INCH),
            PaperSize::UsLedger => (11.0 * INCH, 17.0 * INCH),
        }
    }

    pub fn from_str(s: &str) -> Option<Self> {
        match s.to_lowercase().as_str() {
            "a5" => Some(PaperSize::A5),
            "a4" => Some(PaperSize::A4),
            "a3" => Some(PaperSize::A3),
            "a2" => Some(PaperSize::A2),
            "a1" => Some(PaperSize::A1),
            "a0" => Some(PaperSize::A0),
            "usletter" => Some(PaperSize::UsLetter),
            "ustabloid" => Some(PaperSize::UsTabloid),
            "usledger" => Some(PaperSize::UsLedger),
            _ => None,
        }
    }
}

impl std::fmt::Display for PaperSize {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            PaperSize::A5 => write!(f, "A5"),
            PaperSize::A4 => write!(f, "A4"),
            PaperSize::A3 => write!(f, "A3"),
            PaperSize::A2 => write!(f, "A2"),
            PaperSize::A1 => write!(f, "A1"),
            PaperSize::A0 => write!(f, "A0"),
            PaperSize::UsLetter => write!(f, "USLetter"),
            PaperSize::UsTabloid => write!(f, "USTabloid"),
            PaperSize::UsLedger => write!(f, "USLedger"),
        }
    }
}

/// Page orientation.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Orientation {
    Portrait,
    Landscape,
}

/// Resolved page dimensions in points.
#[derive(Clone, Copy, Debug)]
pub struct PageSetup {
    pub width: f64,
    pub height: f64,
    pub margin: f64,
}

impl PageSetup {
    pub fn new(paper: PaperSize, orientation: Orientation, margin_mm: f64) -> Self {
        let (short, long) = paper.dimensions_pt();
        let (w, h) = match orientation {
            Orientation::Portrait => (short, long),
            Orientation::Landscape => (long, short),
        };
        PageSetup {
            width: w,
            height: h,
            margin: margin_mm * MM,
        }
    }

    pub fn available_width(&self) -> f64 {
        self.width - 2.0 * self.margin
    }

    pub fn available_height(&self) -> f64 {
        self.height - 2.0 * self.margin
    }
}

/// Shared configuration fields used by all layouts.
#[allow(dead_code)]
pub struct Config {
    pub year: i32,
    pub month: u32,
    pub output: String,
    pub paper: PaperSize,
    pub margin_mm: f64,
    pub font: String,
    pub heading_font: Option<String>,
    pub locale: String,
}

impl Config {
    pub fn heading_font(&self) -> &str {
        self.heading_font.as_deref().unwrap_or(&self.font)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a4_dimensions_match_python() {
        let (w, h) = PaperSize::A4.dimensions_pt();
        // 21.0cm and 29.7cm in points
        let expected_w = 21.0 * CM;
        let expected_h = 29.7 * CM;
        assert!((w - expected_w).abs() < 0.001);
        assert!((h - expected_h).abs() < 0.001);
    }

    #[test]
    fn portrait_width_less_than_height() {
        let page = PageSetup::new(PaperSize::A4, Orientation::Portrait, 5.0);
        assert!(page.width < page.height);
    }

    #[test]
    fn landscape_width_greater_than_height() {
        let page = PageSetup::new(PaperSize::A4, Orientation::Landscape, 5.0);
        assert!(page.width > page.height);
    }

    #[test]
    fn margin_converts_mm_to_points() {
        let page = PageSetup::new(PaperSize::A4, Orientation::Portrait, 10.0);
        let expected = 10.0 * MM;
        assert!((page.margin - expected).abs() < 0.001);
    }

    #[test]
    fn available_dimensions_subtract_margins() {
        let page = PageSetup::new(PaperSize::A4, Orientation::Portrait, 5.0);
        let margin = 5.0 * MM;
        assert!((page.available_width() - (page.width - 2.0 * margin)).abs() < 0.001);
        assert!((page.available_height() - (page.height - 2.0 * margin)).abs() < 0.001);
    }

    #[test]
    fn paper_size_from_str() {
        assert_eq!(PaperSize::from_str("A4"), Some(PaperSize::A4));
        assert_eq!(PaperSize::from_str("a4"), Some(PaperSize::A4));
        assert_eq!(PaperSize::from_str("USLetter"), Some(PaperSize::UsLetter));
        assert_eq!(PaperSize::from_str("invalid"), None);
    }

    #[test]
    fn us_letter_dimensions() {
        let (w, h) = PaperSize::UsLetter.dimensions_pt();
        assert!((w - 612.0).abs() < 0.001); // 8.5 * 72
        assert!((h - 792.0).abs() < 0.001); // 11 * 72
    }
}
