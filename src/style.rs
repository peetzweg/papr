/// RGB color with values 0.0..=1.0.
#[derive(Clone, Copy, Debug)]
pub struct Color {
    pub r: f64,
    pub g: f64,
    pub b: f64,
}

impl Color {
    pub const fn rgb(r: f64, g: f64, b: f64) -> Self {
        Color { r, g, b }
    }
}

/// Shared visual constants used by all layouts.
#[allow(dead_code)]
pub mod defaults {
    use super::Color;

    pub const WEEKEND_BG: Color = Color::rgb(0.92, 0.92, 0.92);
    pub const BORDER: Color = Color::rgb(0.7, 0.7, 0.7);
    pub const BORDER_WIDTH_MM: f64 = 0.2;
    pub const ACCENT: Color = Color::rgb(0.3, 0.3, 0.3);
    pub const ACCENT_POLE_MM: f64 = 0.5;

    pub const TEXT_PRIMARY: Color = Color::rgb(0.1, 0.1, 0.1);
    pub const TEXT_SECONDARY: Color = Color::rgb(0.4, 0.4, 0.4);
    pub const TEXT_MUTED: Color = Color::rgb(0.2, 0.2, 0.2);
    pub const TEXT_LIGHT: Color = Color::rgb(1.0, 1.0, 1.0);
}

#[cfg(test)]
mod tests {
    use super::defaults::*;

    fn assert_valid_color(c: super::Color) {
        assert!(c.r >= 0.0 && c.r <= 1.0, "r={} out of range", c.r);
        assert!(c.g >= 0.0 && c.g <= 1.0, "g={} out of range", c.g);
        assert!(c.b >= 0.0 && c.b <= 1.0, "b={} out of range", c.b);
    }

    #[test]
    fn all_default_colors_in_range() {
        assert_valid_color(WEEKEND_BG);
        assert_valid_color(BORDER);
        assert_valid_color(ACCENT);
        assert_valid_color(TEXT_PRIMARY);
        assert_valid_color(TEXT_SECONDARY);
        assert_valid_color(TEXT_MUTED);
        assert_valid_color(TEXT_LIGHT);
    }
}
