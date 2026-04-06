use std::f64::consts::PI;

use chrono::{Datelike, NaiveDate};

use crate::calendar;
use crate::canvas::{Canvas, Font};
use crate::config::{CM, Config, Orientation, PageSetup};
use crate::style::Color;

pub struct ClassicLayout {
    pub abbreviate: bool,
    pub abbreviate_all: bool,
    pub brand: String,
    pub color_numbers: bool,
}

impl super::Layout for ClassicLayout {
    fn orientation(&self) -> Orientation {
        Orientation::Landscape
    }

    fn draw(&self, canvas: &Canvas, config: &Config, page: &PageSetup) {
        let page_width = page.width / 4.0; // 4 pages in landscape
        let cell_width = (page_width - 2.0 * page.margin) / 2.0;
        let cell_height = (page.height / 8.0) - (2.0 * page.margin / 4.0);
        let line_width = 0.01 * CM;
        let font_size = 6.0;

        let mut month_to_draw = config.month;
        let mut year_to_draw = config.year;

        // First month: rotated 180°
        canvas.with_save(|c| {
            c.translate(page.width, page.height / 2.0);
            c.rotate(PI);
            draw_month(
                c,
                self,
                config,
                canvas,
                year_to_draw,
                month_to_draw,
                page,
                page_width,
                cell_width,
                cell_height,
                line_width,
                font_size,
            );
        });

        // Second month
        canvas.with_save(|c| {
            c.translate(0.0, page.height / 2.0);

            if month_to_draw == 12 {
                month_to_draw = 1;
                year_to_draw += 1;
            } else {
                month_to_draw += 1;
            }

            draw_month(
                c,
                self,
                config,
                canvas,
                year_to_draw,
                month_to_draw,
                page,
                page_width,
                cell_width,
                cell_height,
                line_width,
                font_size,
            );
        });

        // Brand text
        if !self.brand.is_empty() {
            canvas.with_save(|c| {
                draw_brand_text(
                    c,
                    canvas,
                    self,
                    config,
                    page.width - page_width + page.margin,
                    page.height / 2.0 + 3.0,
                    font_size,
                );
                c.translate(page.width, page.height / 2.0);
                c.rotate(PI);
                draw_brand_text(
                    c,
                    canvas,
                    self,
                    config,
                    page.width - page_width + page.margin,
                    3.0,
                    font_size,
                );
            });
        }
    }
}

fn draw_brand_text(
    _c: &Canvas,
    canvas: &Canvas,
    layout: &ClassicLayout,
    config: &Config,
    x: f64,
    y: f64,
    font_size: f64,
) {
    let parts: Vec<&str> = layout.brand.splitn(2, ' ').collect();
    if parts.is_empty() {
        return;
    }

    // Number part (first word)
    let number_font = Font::new(&config.font, font_size).heavy();
    let number_color = if layout.color_numbers {
        Color::rgb(0.6, 0.0, 0.0)
    } else {
        Color::rgb(0.0, 0.0, 0.0)
    };
    canvas.draw_text(parts[0], x, y, &number_font, number_color);

    // Day part (second word)
    if parts.len() > 1 {
        let number_m = canvas.measure_text(parts[0], &number_font);
        let day_font = Font::new(&config.font, font_size);
        canvas.draw_text(
            parts[1],
            x + number_m.width + font_size / 2.0,
            y,
            &day_font,
            Color::rgb(0.0, 0.0, 0.0),
        );
    }
}

fn draw_month(
    c: &Canvas,
    layout: &ClassicLayout,
    config: &Config,
    canvas: &Canvas,
    year: i32,
    month: u32,
    page: &PageSetup,
    page_width: f64,
    cell_width: f64,
    cell_height: f64,
    line_width: f64,
    font_size: f64,
) {
    let mut date = NaiveDate::from_ymd_opt(year, month, 1).unwrap();

    // Month title in first cell
    draw_month_title(
        c,
        canvas,
        layout,
        config,
        page.margin,
        page.margin,
        cell_width,
        cell_height,
        date,
    );

    let mut cells_on_page: u32 = 1;
    let cells_on_page_max: u32 = 8;
    let mut page_num: u32 = 0;
    let mut row: u32 = 1;
    let mut column: u32 = 0;

    while date.month() == month {
        let x = page.margin + (page_num as f64 * page_width) + (column as f64 * cell_width);
        let y = page.margin + (row as f64 * cell_height);

        draw_day(
            c,
            canvas,
            layout,
            config,
            x,
            y,
            cell_width,
            cell_height,
            line_width,
            font_size,
            date,
        );

        cells_on_page += 1;
        row += 1;
        date = date.succ_opt().unwrap();

        if cells_on_page >= cells_on_page_max {
            cells_on_page = 0;
            page_num += 1;
            column = 0;
            row = 0;
        }

        if cells_on_page == 4 {
            row = 0;
            column += 1;
        }
    }
}

fn draw_month_title(
    _c: &Canvas,
    canvas: &Canvas,
    layout: &ClassicLayout,
    config: &Config,
    x: f64,
    y: f64,
    cell_width: f64,
    cell_height: f64,
    date: NaiveDate,
) {
    let style = if layout.abbreviate_all { "%b" } else { "%B" };
    let month_str = date.format(style).to_string();

    // Find font size that fits
    let mut font_size = 20.0;
    loop {
        let font = Font::new(&config.font, font_size);
        let m = canvas.measure_text(&month_str, &font);
        if m.width <= cell_width {
            let text_y = y + (cell_height / 2.0 - m.height / 2.0);
            canvas.draw_text(&month_str, x, text_y, &font, Color::rgb(0.0, 0.0, 0.0));
            break;
        }
        font_size -= 1.0;
        if font_size <= 1.0 {
            let font = Font::new(&config.font, 1.0);
            canvas.draw_text(&month_str, x, y, &font, Color::rgb(0.0, 0.0, 0.0));
            break;
        }
    }
}

fn draw_day(
    _c: &Canvas,
    canvas: &Canvas,
    layout: &ClassicLayout,
    config: &Config,
    x: f64,
    y: f64,
    width: f64,
    height: f64,
    line_width: f64,
    font_size: f64,
    date: NaiveDate,
) {
    // Weekend fill
    if calendar::is_weekend(date) {
        canvas.fill_rect(x, y, width, height, Color::rgb(0.90, 0.90, 0.90));
    }

    // Cell border
    canvas.stroke_rect(x, y, width, height, Color::rgb(0.0, 0.0, 0.0), line_width);

    // Text
    let offset_x = (font_size * 0.3333).floor();
    let offset_y = (font_size * 0.3333).floor();

    let weekday_str = if layout.abbreviate || layout.abbreviate_all {
        date.format("%a").to_string()
    } else {
        date.format("%A").to_string()
    };
    let day_str = format!("{} {}", date.day(), weekday_str);
    let parts: Vec<&str> = day_str.splitn(2, ' ').collect();

    // Number
    let number_font = Font::new(&config.font, font_size).heavy();
    let number_color = if layout.color_numbers {
        Color::rgb(0.6, 0.0, 0.0)
    } else {
        Color::rgb(0.0, 0.0, 0.0)
    };
    canvas.draw_text(
        parts[0],
        x + offset_x,
        y + offset_y,
        &number_font,
        number_color,
    );

    // Day name
    if parts.len() > 1 {
        let number_m = canvas.measure_text(parts[0], &number_font);
        let day_font = Font::new(&config.font, font_size);
        canvas.draw_text(
            parts[1],
            x + offset_x + number_m.width + font_size / 2.0,
            y + offset_y,
            &day_font,
            Color::rgb(0.0, 0.0, 0.0),
        );
    }
}
