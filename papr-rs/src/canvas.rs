use cairo::{Context, PdfSurface, SvgSurface, SvgUnit};
use pango::FontDescription;
use pangocairo::functions as pc;

use crate::config::PageSetup;
use crate::style::Color;

/// Result of measuring text. All values in points.
#[derive(Debug)]
pub struct TextMetrics {
    pub width: f64,
    pub height: f64,
    /// Ink offset X from layout origin (for visual centering).
    pub ink_x: f64,
    /// Ink offset Y from layout origin (for visual centering).
    pub ink_y: f64,
    /// Ink width (tighter than logical width).
    pub ink_width: f64,
    /// Ink height (tighter than logical height).
    pub ink_height: f64,
}

/// Font specification.
#[derive(Clone, Debug)]
pub struct Font {
    pub family: String,
    pub size: f64,
    pub weight: FontWeight,
}

#[derive(Clone, Debug)]
pub enum FontWeight {
    Regular,
    Bold,
    Heavy,
}

impl Font {
    pub fn new(family: &str, size: f64) -> Self {
        Font {
            family: family.to_string(),
            size,
            weight: FontWeight::Regular,
        }
    }

    pub fn bold(mut self) -> Self {
        self.weight = FontWeight::Bold;
        self
    }

    pub fn heavy(mut self) -> Self {
        self.weight = FontWeight::Heavy;
        self
    }

    pub fn to_pango_desc(&self) -> FontDescription {
        let weight_str = match self.weight {
            FontWeight::Regular => "",
            FontWeight::Bold => "bold",
            FontWeight::Heavy => "heavy",
        };
        let desc_str = format!("{} {} {}", self.family, weight_str, self.size);
        FontDescription::from_string(&desc_str)
    }
}

/// Surface type — the actual cairo surface that produces output.
/// Both variants share the same `Context` API, which is how we get
/// a single code path for PDF and SVG.
enum Surface {
    Pdf(PdfSurface),
    Svg(SvgSurface),
}

/// Drawing API wrapping cairo + pango.
/// One `Canvas` = one output file. Both PDF and SVG use the same
/// `Context` methods — the format is determined at construction.
pub struct Canvas {
    cr: Context,
    _surface: Surface,
}

impl Canvas {
    /// Create a canvas writing to the given file.
    /// Format detected from extension: `.pdf` or `.svg`.
    pub fn new(path: &str, page: &PageSetup) -> Result<Self, String> {
        let (cr, surface) = if path.ends_with(".svg") {
            let mut surface = SvgSurface::new(page.width, page.height, Some(path))
                .map_err(|e| format!("Failed to create SVG surface: {e}"))?;
            surface.set_document_unit(SvgUnit::Pt);
            let cr = Context::new(&surface)
                .map_err(|e| format!("Failed to create context: {e}"))?;
            (cr, Surface::Svg(surface))
        } else if path.ends_with(".pdf") {
            let surface = PdfSurface::new(page.width, page.height, path)
                .map_err(|e| format!("Failed to create PDF surface: {e}"))?;
            surface.set_fallback_resolution(1200.0, 1200.0);
            let cr = Context::new(&surface)
                .map_err(|e| format!("Failed to create context: {e}"))?;
            (cr, Surface::Pdf(surface))
        } else {
            return Err(format!(
                "Unsupported output format: {path}. Use .pdf or .svg"
            ));
        };

        Ok(Canvas {
            cr,
            _surface: surface,
        })
    }

    // ---- Text ----

    /// Draw text at (x, y) with the given font and color.
    pub fn draw_text(&self, text: &str, x: f64, y: f64, font: &Font, color: Color) {
        self.cr.move_to(x, y);
        self.cr.set_source_rgb(color.r, color.g, color.b);
        let layout = self.create_pango_layout();
        layout.set_font_description(Some(&font.to_pango_desc()));
        layout.set_text(text);
        pc::update_layout(&self.cr, &layout);
        pc::show_layout(&self.cr, &layout);
    }

    /// Measure text without drawing. Returns both logical and ink extents.
    pub fn measure_text(&self, text: &str, font: &Font) -> TextMetrics {
        let layout = self.create_pango_layout();
        layout.set_font_description(Some(&font.to_pango_desc()));
        layout.set_text(text);
        pc::update_layout(&self.cr, &layout);

        let (ink, logical) = layout.pixel_extents();
        TextMetrics {
            width: logical.width() as f64,
            height: logical.height() as f64,
            ink_x: ink.x() as f64,
            ink_y: ink.y() as f64,
            ink_width: ink.width() as f64,
            ink_height: ink.height() as f64,
        }
    }

    // ---- Shapes ----

    /// Fill a rectangle with a solid color.
    pub fn fill_rect(&self, x: f64, y: f64, w: f64, h: f64, color: Color) {
        self.cr.set_source_rgb(color.r, color.g, color.b);
        self.cr.rectangle(x, y, w, h);
        self.cr.fill().unwrap();
    }

    /// Stroke a rectangle outline.
    pub fn stroke_rect(&self, x: f64, y: f64, w: f64, h: f64, color: Color, line_width: f64) {
        self.cr.set_line_width(line_width);
        self.cr.set_source_rgb(color.r, color.g, color.b);
        self.cr.rectangle(x, y, w, h);
        self.cr.stroke().unwrap();
    }

    /// Draw a line from (x1,y1) to (x2,y2).
    pub fn draw_line(
        &self,
        x1: f64,
        y1: f64,
        x2: f64,
        y2: f64,
        color: Color,
        line_width: f64,
    ) {
        self.cr.set_line_width(line_width);
        self.cr.set_source_rgb(color.r, color.g, color.b);
        self.cr.move_to(x1, y1);
        self.cr.line_to(x2, y2);
        self.cr.stroke().unwrap();
    }

    // ---- Transforms ----

    /// Execute a closure with saved/restored Cairo state.
    pub fn with_save<F: FnOnce(&Canvas)>(&self, f: F) {
        self.cr.save().unwrap();
        f(self);
        self.cr.restore().unwrap();
    }

    /// Translate the coordinate origin.
    pub fn translate(&self, x: f64, y: f64) {
        self.cr.translate(x, y);
    }

    /// Rotate by angle in radians.
    pub fn rotate(&self, angle: f64) {
        self.cr.rotate(angle);
    }

    // ---- Page ----

    /// Finish the current page and start a new one (PDF only, no-op for SVG).
    pub fn show_page(&self) {
        self.cr.show_page().unwrap();
    }

    // ---- Internal ----

    fn create_pango_layout(&self) -> pango::Layout {
        let layout = pc::create_layout(&self.cr);

        // Enable kerning + ligatures, matching Python's
        // Pango.attr_font_features_new("kern=1,liga=1")
        let attrs = pango::AttrList::new();
        let font_features = pango::AttrFontFeatures::new("kern=1,liga=1");
        attrs.insert(font_features);
        layout.set_attributes(Some(&attrs));

        layout
    }
}

impl Drop for Canvas {
    fn drop(&mut self) {
        match &self._surface {
            Surface::Pdf(s) => s.finish(),
            Surface::Svg(s) => s.finish(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn font_regular_description() {
        let font = Font::new("Sans", 12.0);
        let desc = font.to_pango_desc();
        let s = desc.to_str();
        assert!(s.contains("12"), "Expected size 12 in: {s}");
    }

    #[test]
    fn font_bold_description() {
        let font = Font::new("Sans", 10.0).bold();
        let desc = font.to_pango_desc();
        let s = desc.to_str();
        // Pango normalizes "bold" to "Bold" in the description
        let lower = s.to_lowercase();
        assert!(lower.contains("bold"), "Expected 'bold' in: {s}");
    }

    #[test]
    fn canvas_pdf_creation() {
        let page = crate::config::PageSetup::new(
            crate::config::PaperSize::A4,
            crate::config::Orientation::Portrait,
            5.0,
        );
        let path = "/tmp/papr_test_skeleton.pdf";
        let canvas = Canvas::new(path, &page);
        assert!(canvas.is_ok(), "Failed to create PDF canvas: {:?}", canvas.err());
        drop(canvas);
        let meta = std::fs::metadata(path).unwrap();
        assert!(meta.len() > 0, "PDF file is empty");
        std::fs::remove_file(path).ok();
    }

    #[test]
    fn canvas_svg_creation() {
        let page = crate::config::PageSetup::new(
            crate::config::PaperSize::A4,
            crate::config::Orientation::Portrait,
            5.0,
        );
        let path = "/tmp/papr_test_skeleton.svg";
        let canvas = Canvas::new(path, &page);
        assert!(canvas.is_ok(), "Failed to create SVG canvas: {:?}", canvas.err());
        drop(canvas);
        let meta = std::fs::metadata(path).unwrap();
        assert!(meta.len() > 0, "SVG file is empty");
        std::fs::remove_file(path).ok();
    }

    #[test]
    fn canvas_unsupported_format() {
        let page = crate::config::PageSetup::new(
            crate::config::PaperSize::A4,
            crate::config::Orientation::Portrait,
            5.0,
        );
        let result = Canvas::new("/tmp/test.png", &page);
        assert!(result.is_err());
    }

    #[test]
    fn measure_text_returns_nonzero() {
        let page = crate::config::PageSetup::new(
            crate::config::PaperSize::A4,
            crate::config::Orientation::Portrait,
            5.0,
        );
        let path = "/tmp/papr_test_measure.pdf";
        let canvas = Canvas::new(path, &page).unwrap();
        let font = Font::new("Sans", 12.0);
        let m = canvas.measure_text("Hello", &font);
        assert!(m.width > 0.0, "Text width should be > 0");
        assert!(m.height > 0.0, "Text height should be > 0");
        drop(canvas);
        std::fs::remove_file(path).ok();
    }
}
