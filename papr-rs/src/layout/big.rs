use chrono::{Datelike, NaiveDate};

use crate::calendar;
use crate::canvas::{Canvas, Font};
use crate::config::{Config, Orientation, PageSetup, MM};
use crate::style::Color;

/// Number of days per row (columns).
const DAYS_PER_ROW: usize = 21;

/// Font size in points for day/date text.
const DAY_TEXT_FONT_SIZE: f64 = 4.0;

/// Font size in points for month label.
const MONTH_LABEL_FONT_SIZE: f64 = 4.0;

/// Border settings.
const BORDER_COLOR: Color = Color::rgb(0.7, 0.7, 0.7);
const BORDER_WIDTH_MM: f64 = 0.2;

/// Flag and pole settings.
const FLAG_COLOR: Color = Color::rgb(0.3, 0.3, 0.3);
const FLAG_POLE_WIDTH_MM: f64 = 0.5;

pub struct BigLayout;

impl super::Layout for BigLayout {
    fn orientation(&self) -> Orientation {
        Orientation::Landscape
    }

    fn draw(&self, canvas: &Canvas, config: &Config, page: &PageSetup) {
        let columns = DAYS_PER_ROW;

        let start_date = NaiveDate::from_ymd_opt(config.year, config.month, 1).unwrap();

        // Calculate end date (12 months from start)
        let (end_year, end_month) = if config.month == 1 {
            (config.year, 12u32)
        } else {
            (config.year + 1, config.month - 1)
        };
        let last_day = calendar::last_day_of_month(end_year, end_month);
        let end_date = NaiveDate::from_ymd_opt(end_year, end_month, last_day).unwrap();

        // Padding to align rows so they end with SAT SUN
        let padding_cells = start_date.weekday().num_days_from_monday() as usize;

        // Mid-year padding for year transition alignment
        let mid_year_padding = if config.month > 1 { 7usize } else { 0 };

        // Calculate total cells
        let total_cells = if config.month > 1 {
            let dec31 = NaiveDate::from_ymd_opt(config.year, 12, 31).unwrap();
            let days_first_part = (dec31 - start_date).num_days() as usize + 1;
            let jan1_next = NaiveDate::from_ymd_opt(config.year + 1, 1, 1).unwrap();
            let days_second_part = (end_date - jan1_next).num_days() as usize + 1;
            padding_cells + days_first_part + mid_year_padding + days_second_part
        } else {
            let total_days = (end_date - start_date).num_days() as usize + 1;
            padding_cells + total_days
        };

        let rows = (total_cells + columns - 1) / columns;

        // Available area (landscape)
        let available_width = page.width - 2.0 * page.margin;
        let available_height = page.height - 2.0 * page.margin;

        let cell_width = available_width / columns as f64;
        let cell_height = available_height / rows as f64;

        let offset_x = page.margin;
        let offset_y = page.margin;
        let line_width = BORDER_WIDTH_MM * MM;
        let flag_pole_width = FLAG_POLE_WIDTH_MM * MM;

        // Draw year label in initial padding
        if padding_cells > 0 {
            draw_year_label(
                canvas, config, config.year, 0, padding_cells, columns, cell_width, cell_height,
                offset_x, offset_y,
            );
        }

        // Draw all days
        let mut date = start_date;
        let mut cell_index = padding_cells;
        let mut drew_mid_year_label = false;

        while date <= end_date {
            // Year transition: draw new year label in mid-year padding
            if config.month > 1
                && date.month() == 1
                && date.day() == 1
                && date.year() == config.year + 1
                && !drew_mid_year_label
            {
                if mid_year_padding > 0 {
                    draw_year_label(
                        canvas,
                        config,
                        config.year + 1,
                        cell_index,
                        mid_year_padding,
                        columns,
                        cell_width,
                        cell_height,
                        offset_x,
                        offset_y,
                    );
                }
                cell_index += mid_year_padding;
                drew_mid_year_label = true;
            }

            let col = cell_index % columns;
            let row = cell_index / columns;

            let x = offset_x + col as f64 * cell_width;
            let y = offset_y + row as f64 * cell_height;

            let is_month_start = date.day() == 1;

            draw_day(
                canvas, config, x, y, cell_width, cell_height, line_width, flag_pole_width, date,
                is_month_start,
            );

            date = date.succ_opt().unwrap();
            cell_index += 1;
        }
    }
}

fn draw_year_label(
    canvas: &Canvas,
    config: &Config,
    year: i32,
    start_cell_index: usize,
    padding_count: usize,
    columns: usize,
    cell_width: f64,
    cell_height: f64,
    offset_x: f64,
    offset_y: f64,
) {
    canvas.with_save(|_| {
        let year_str = year.to_string();

        let start_col = start_cell_index % columns;
        let start_row = start_cell_index / columns;

        // Year label takes up 3 cells width, right-aligned
        let label_cells = 3;
        let label_width = label_cells as f64 * cell_width;
        let label_height = cell_height;

        let padding_width = padding_count as f64 * cell_width;
        let label_start_x =
            offset_x + (start_col as f64 * cell_width) + (padding_width - label_width);
        let label_start_y = offset_y + (start_row as f64 * cell_height);

        // Find largest font size that fits
        let mut font_size = (label_height * 0.8) as f64;
        let font = Font::new(&config.font, font_size).bold();
        let mut m = canvas.measure_text(&year_str, &font);

        // Use ink extents for visual centering
        let mut ink_width = m.ink_width;
        let mut ink_height = m.ink_height;
        let mut ink_x = m.ink_x;
        let mut ink_y = m.ink_y;

        while ink_width > label_width * 0.9 && font_size > 10.0 {
            font_size -= 2.0;
            let font = Font::new(&config.font, font_size).bold();
            m = canvas.measure_text(&year_str, &font);
            ink_width = m.ink_width;
            ink_height = m.ink_height;
            ink_x = m.ink_x;
            ink_y = m.ink_y;
        }

        let font = Font::new(&config.font, font_size).bold();
        let x = label_start_x + (label_width - ink_width) / 2.0 - ink_x;
        let y = label_start_y + (label_height - ink_height) / 2.0 - ink_y;

        canvas.draw_text(&year_str, x, y, &font, Color::rgb(0.2, 0.2, 0.2));
    });
}

fn draw_day(
    canvas: &Canvas,
    config: &Config,
    x: f64,
    y: f64,
    cell_width: f64,
    cell_height: f64,
    line_width: f64,
    flag_pole_width: f64,
    date: NaiveDate,
    is_month_start: bool,
) {
    canvas.with_save(|c| {
        c.translate(x, y);

        // Weekend background
        if calendar::is_weekend(date) {
            c.fill_rect(0.0, 0.0, cell_width, cell_height, Color::rgb(0.92, 0.92, 0.92));
        }

        // Cell border
        c.stroke_rect(0.0, 0.0, cell_width, cell_height, BORDER_COLOR, line_width);

        // Day info (weekday + date) in top-right
        let text_padding = draw_day_info(c, canvas, config, date, cell_width);

        // Month label flag on first day
        if is_month_start {
            draw_month_label(c, canvas, config, date, cell_height, line_width, flag_pole_width, text_padding);
        }
    });
}

fn draw_day_info(
    c: &Canvas,
    canvas: &Canvas,
    config: &Config,
    date: NaiveDate,
    cell_width: f64,
) -> f64 {
    let font_size = DAY_TEXT_FONT_SIZE;
    let padding = font_size * 0.5;

    let weekday_str = date.format("%a").to_string().to_uppercase();
    let day_str = date.day().to_string();

    let font = Font::new(&config.font, font_size);
    let font_bold = Font::new(&config.font, font_size).bold();

    let weekday_m = canvas.measure_text(&weekday_str, &font);
    let day_m = canvas.measure_text(&day_str, &font_bold);

    let gap = padding * 0.5;
    let total_width = weekday_m.width + gap + day_m.width;
    let start_x = cell_width - padding - total_width;

    canvas.with_save(|_| {
        c.draw_text(&weekday_str, start_x, padding, &font, Color::rgb(0.4, 0.4, 0.4));
        c.draw_text(
            &day_str,
            start_x + weekday_m.width + gap,
            padding,
            &font_bold,
            Color::rgb(0.1, 0.1, 0.1),
        );
    });

    padding
}

fn draw_month_label(
    c: &Canvas,
    canvas: &Canvas,
    config: &Config,
    date: NaiveDate,
    cell_height: f64,
    line_width: f64,
    flag_pole_width: f64,
    text_padding: f64,
) {
    canvas.with_save(|_| {
        let month_str = date.format("%b").to_string().to_uppercase();

        let font_size = MONTH_LABEL_FONT_SIZE;
        let font = Font::new(&config.font, font_size).bold();

        let m = canvas.measure_text(&month_str, &font);

        let padding_x = font_size * 0.4;
        let padding_y = font_size * 0.2;

        let flag_width = m.width + padding_x * 2.0;
        let flag_height = m.height + padding_y * 2.0;

        let flag_x = 0.0;
        let flag_y = text_padding - padding_y;

        let pole_x = 0.0;
        let pole_y = line_width / 2.0;

        // Flag pole
        c.draw_line(
            pole_x,
            pole_y,
            pole_x,
            cell_height - pole_y,
            FLAG_COLOR,
            flag_pole_width,
        );

        // Flag background
        c.fill_rect(
            flag_x,
            pole_y,
            flag_width,
            flag_height + flag_y - pole_y,
            FLAG_COLOR,
        );

        // Month text in white
        c.draw_text(
            &month_str,
            flag_x + padding_x,
            flag_y + padding_y,
            &font,
            Color::rgb(1.0, 1.0, 1.0),
        );
    });
}
