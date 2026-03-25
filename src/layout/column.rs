use chrono::{Datelike, NaiveDate};

use crate::calendar;
use crate::canvas::{Canvas, Font};
use crate::config::{Config, Orientation, PageSetup, CM};
use crate::style::Color;

pub struct ColumnLayout;

impl super::Layout for ColumnLayout {
    fn orientation(&self) -> Orientation {
        Orientation::Landscape
    }

    fn draw(&self, canvas: &Canvas, config: &Config, page: &PageSetup) {
        let font_size = 6.0;
        let line_width = 0.01 * CM;
        let column_width = page.width / 4.0;
        let row_width = column_width - 2.0 * page.margin;
        let row_height = (page.height - 4.0 * page.margin) / 33.0;

        let mut date = NaiveDate::from_ymd_opt(config.year, config.month, 1).unwrap();

        canvas.with_save(|c| {
            for col in 0..4 {
                c.with_save(|c| {
                    c.translate(col as f64 * column_width, 0.0);

                    // Month title
                    draw_month_title(c, config, &page, date, column_width, row_height, font_size);

                    // Days
                    let starting_month = date.month();
                    while date.month() == starting_month {
                        draw_day(c, config, &page, date, row_width, row_height, font_size, line_width);
                        date = date.succ_opt().unwrap();
                    }
                });
            }
        });
    }
}

fn draw_month_title(
    canvas: &Canvas,
    config: &Config,
    page: &PageSetup,
    date: NaiveDate,
    column_width: f64,
    row_height: f64,
    font_size: f64,
) {
    let title_font = Font::new(&config.font, font_size * 2.0);

    // Month name — full or abbreviated
    let month_str = if config.abbreviate_all {
        date.format("%b").to_string()
    } else {
        date.format("%B").to_string()
    };

    let m = canvas.measure_text(&month_str, &title_font);
    let x_offset = (column_width - m.width) / 2.0;
    let y_offset = ((row_height * 2.0 - m.height) / 2.0) + page.margin;

    canvas.draw_text(
        &month_str,
        x_offset,
        y_offset,
        &title_font,
        Color::rgb(0.0, 0.0, 0.0),
    );
}

fn draw_day(
    canvas: &Canvas,
    config: &Config,
    page: &PageSetup,
    date: NaiveDate,
    row_width: f64,
    row_height: f64,
    font_size: f64,
    line_width: f64,
) {
    canvas.with_save(|c| {
        let mut y_offset =
            page.margin + 2.0 * row_height + (date.day0() as f64 * row_height);

        // Folding margin after day 15
        if date.day() > 15 {
            y_offset += 2.0 * page.margin;
        }

        c.translate(page.margin, y_offset);

        // Weekend background
        if calendar::is_weekend(date) {
            c.fill_rect(0.0, 0.0, row_width, row_height, Color::rgb(0.90, 0.90, 0.90));
        }

        // Cell border
        c.stroke_rect(0.0, 0.0, row_width, row_height, Color::rgb(0.0, 0.0, 0.0), line_width);

        // Day text: "1 Monday" or "1 Mon"
        let day_font = Font::new(&config.font, font_size);
        let weekday_str = if config.abbreviate || config.abbreviate_all {
            date.format("%a").to_string()
        } else {
            date.format("%A").to_string()
        };
        let day_str = format!("{} {}", date.day(), weekday_str);

        let m = c.measure_text(&day_str, &day_font);
        let text_y = (row_height - m.height) / 2.0;
        c.draw_text(
            &day_str,
            font_size / 2.0,
            text_y,
            &day_font,
            Color::rgb(0.0, 0.0, 0.0),
        );
    });
}
