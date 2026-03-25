use chrono::{Datelike, NaiveDate};

use crate::calendar;
use crate::canvas::{Canvas, Font};
use crate::config::{Config, Orientation, PageSetup, MM};
use crate::style::{defaults, Color};

pub struct MonthLayout;

impl super::Layout for MonthLayout {
    fn orientation(&self) -> Orientation {
        Orientation::Portrait
    }

    fn draw(&self, canvas: &Canvas, config: &Config, page: &PageSetup) {
        let avail_w = page.available_width();
        let avail_h = page.available_height();

        // Split page: 1/3 header, 2/3 grid
        let header_height = avail_h / 3.0;
        let grid_height = avail_h * 2.0 / 3.0;

        // Grid: 7 columns, 6 rows max, plus weekday header row
        let cols = 7;
        let header_row_h = grid_height * 0.08;
        let grid_content_h = grid_height - header_row_h;
        let rows = 6;
        let cell_w = avail_w / cols as f64;
        let cell_h = grid_content_h / rows as f64;

        let offset_x = page.margin;
        let header_y = page.margin;
        let weekday_y = page.margin + header_height;
        let grid_y = weekday_y + header_row_h;

        let line_width = defaults::BORDER_WIDTH_MM * MM;
        let day_font_size = 8.0;

        let date = NaiveDate::from_ymd_opt(config.year, config.month, 1).unwrap();

        draw_header(canvas, config, offset_x, header_y, avail_w, header_height);
        draw_weekday_headers(canvas, config, offset_x, weekday_y, cell_w, header_row_h);
        draw_days_grid(
            canvas, config, date, offset_x, grid_y, cell_w, cell_h, line_width, day_font_size,
        );
    }
}

fn draw_header(
    canvas: &Canvas,
    config: &Config,
    offset_x: f64,
    header_y: f64,
    avail_w: f64,
    header_height: f64,
) {
    canvas.with_save(|_| {
        let year_str = config.year.to_string();
        let date = NaiveDate::from_ymd_opt(config.year, config.month, 1).unwrap();
        let month_str = date.format("%b").to_string().to_uppercase();

        let month_font_size = (header_height * 0.5) as f64;
        let year_font_size = (month_font_size / 5.0) as f64;

        let year_font = Font::new(&config.font, year_font_size).bold();
        let month_font = Font::new(&config.font, month_font_size).bold();

        let year_m = canvas.measure_text(&year_str, &year_font);
        let month_m = canvas.measure_text(&month_str, &month_font);

        let center_x = offset_x + avail_w / 2.0;

        // Center month in header
        let month_y = header_y + (header_height - month_m.height) / 2.0;
        let month_x = center_x - month_m.width / 2.0;

        // Year above month
        let gap = year_m.height * 0.3;
        let year_y = (month_y - gap - year_m.height).max(header_y);
        let year_x = center_x - year_m.width / 2.0;

        canvas.draw_text(&year_str, year_x, year_y, &year_font, defaults::TEXT_PRIMARY);
        canvas.draw_text(
            &month_str,
            month_x,
            month_y,
            &month_font,
            defaults::TEXT_PRIMARY,
        );
    });
}

fn draw_weekday_headers(
    canvas: &Canvas,
    config: &Config,
    offset_x: f64,
    weekday_y: f64,
    cell_w: f64,
    header_row_h: f64,
) {
    let weekdays = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"];
    let font_size = header_row_h * 0.5;
    let font = Font::new(&config.font, font_size).bold();

    for (col, name) in weekdays.iter().enumerate() {
        let x = offset_x + col as f64 * cell_w;

        canvas.with_save(|c| {
            c.translate(x, weekday_y);

            let m = canvas.measure_text(name, &font);
            let text_x = (cell_w - m.width) / 2.0;
            let text_y = (header_row_h - m.height) / 2.0;

            let color = if col >= 5 {
                defaults::TEXT_SECONDARY
            } else {
                defaults::TEXT_PRIMARY
            };
            c.draw_text(name, text_x, text_y, &font, color);
        });
    }
}

fn draw_days_grid(
    canvas: &Canvas,
    config: &Config,
    first_of_month: NaiveDate,
    offset_x: f64,
    grid_y: f64,
    cell_w: f64,
    cell_h: f64,
    line_width: f64,
    day_font_size: f64,
) {
    let first_weekday = first_of_month.weekday().num_days_from_monday() as usize;
    let days_in_month = calendar::last_day_of_month(config.year, config.month);

    let font = Font::new(&config.font, day_font_size);
    let font_bold = Font::new(&config.font, day_font_size).bold();
    let padding = day_font_size * 0.5;

    for day in 1..=days_in_month {
        let day_offset = first_weekday + day as usize - 1;
        let col = day_offset % 7;
        let row = day_offset / 7;

        let x = offset_x + col as f64 * cell_w;
        let y = grid_y + row as f64 * cell_h;

        let date = NaiveDate::from_ymd_opt(config.year, config.month, day).unwrap();
        let is_monday = date.weekday() == chrono::Weekday::Mon;

        canvas.with_save(|c| {
            c.translate(x, y);

            // Weekend background
            if calendar::is_weekend(date) {
                c.fill_rect(0.0, 0.0, cell_w, cell_h, defaults::WEEKEND_BG);
            }

            // Cell border
            c.stroke_rect(0.0, 0.0, cell_w, cell_h, defaults::BORDER, line_width);

            // Day number, top-right
            let day_str = day.to_string();
            let m = canvas.measure_text(&day_str, &font_bold);
            let day_x = cell_w - padding - m.width;
            c.draw_text(&day_str, day_x, padding, &font_bold, defaults::TEXT_PRIMARY);

            // Week number on Mondays, top-left
            if is_monday {
                let iso_week = date.iso_week().week().to_string();
                c.draw_text(&iso_week, padding, padding, &font, defaults::TEXT_SECONDARY);
            }
        });
    }
}
