use chrono::{Datelike, NaiveDate};

use crate::calendar;
use crate::canvas::{Canvas, Font};
use crate::config::{CM, Config, Orientation, PageSetup};
use crate::style::Color;

pub struct OneYearLayout;

impl super::Layout for OneYearLayout {
    fn orientation(&self) -> Orientation {
        Orientation::Landscape
    }

    fn draw(&self, canvas: &Canvas, config: &Config, page: &PageSetup) {
        let font_size = 6.0;
        let line_width = 0.01 * CM;
        // 12 columns with 13 margins (safety between each column + edges)
        let row_width = (page.width - 13.0 * page.margin) / 12.0;
        let row_height = (page.height - 2.0 * page.margin) / 32.0;

        let mut date = NaiveDate::from_ymd_opt(config.year, config.month, 1).unwrap();

        for col in 0..12 {
            canvas.with_save(|c| {
                c.translate(
                    page.margin + (col as f64 * row_width) + (col as f64 * page.margin),
                    0.0,
                );

                // Month title
                draw_month_title(c, config, page, date, row_width, row_height);

                // Days
                let starting_month = date.month();
                while date.month() == starting_month {
                    draw_day(
                        c, config, date, row_width, row_height, font_size, line_width, page,
                    );
                    date = date.succ_opt().unwrap();
                }
            });
        }
    }
}

fn draw_month_title(
    canvas: &Canvas,
    config: &Config,
    page: &PageSetup,
    date: NaiveDate,
    row_width: f64,
    row_height: f64,
) {
    canvas.with_save(|c| {
        let size = (row_height * 0.9).ceil();
        let font = Font::new(config.heading_font(), size);

        // Always abbreviated and uppercased
        let month_str = date.format("%b").to_string().to_uppercase();

        let m = c.measure_text(&month_str, &font);
        let x_offset = (row_width - m.width) / 2.0;
        let y_offset = (page.margin + row_height) - m.height;

        c.draw_text(
            &month_str,
            x_offset,
            y_offset,
            &font,
            Color::rgb(0.0, 0.0, 0.0),
        );
    });
}

fn draw_day(
    canvas: &Canvas,
    config: &Config,
    date: NaiveDate,
    row_width: f64,
    row_height: f64,
    _font_size: f64,
    line_width: f64,
    page: &PageSetup,
) {
    canvas.with_save(|c| {
        let y_offset = page.margin + (date.day0() as f64 * row_height) + row_height;
        c.translate(0.0, y_offset);

        // Weekend background
        if calendar::is_weekend(date) {
            c.fill_rect(
                0.0,
                0.0,
                row_width,
                row_height,
                Color::rgb(0.90, 0.90, 0.90),
            );
        }

        // Bottom line (not full rectangle stroke, matching Python)
        c.draw_line(
            0.0,
            row_height,
            row_width,
            row_height,
            Color::rgb(0.0, 0.0, 0.0),
            line_width,
        );

        // Text sizes based on row height
        let number_size = (row_height * 0.4).floor();
        let day_size = (row_height * 0.25).floor();

        let number_font = Font::new(&config.font, number_size);
        let day_font = Font::new(&config.font, day_size);

        let weekday_str = date.format("%a").to_string();

        // Day number
        let day_str = date.day().to_string();
        let number_m = c.measure_text(&day_str, &number_font);
        let number_y = (row_height - number_size) / 2.0;

        canvas.with_save(|c| {
            c.translate(0.0, number_y);
            c.draw_text(&day_str, 0.0, 0.0, &number_font, Color::rgb(0.0, 0.0, 0.0));
        });

        // Weekday letter (first character)
        let weekday_char = &weekday_str[..1];
        let x_offset = number_m.width * 1.025;
        let day_y = (row_height - number_size) / 2.0 + (day_size * 0.8);

        canvas.with_save(|c| {
            c.translate(x_offset, day_y);
            c.draw_text(weekday_char, 0.0, 0.0, &day_font, Color::rgb(0.0, 0.0, 0.0));
        });
    });
}
