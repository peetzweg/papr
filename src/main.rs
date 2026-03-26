#![allow(clippy::too_many_arguments)]

use chrono::Datelike;
use clap::Parser;

mod calendar;
mod canvas;
mod config;
mod layout;
mod style;

use config::{Config, PageSetup, PaperSize};

#[derive(Parser)]
#[command(name = "papr", about = "Generate printable calendar PDFs and SVGs")]
struct Cli {
    /// Calendar layout
    layout: String,

    /// Output file (.pdf or .svg)
    #[arg(short, long, default_value = "out.pdf")]
    output: String,

    /// Year
    #[arg(short, long)]
    year: Option<i32>,

    /// Starting month (1-12)
    #[arg(short, long, value_parser = clap::value_parser!(u32).range(1..=12))]
    month: Option<u32>,

    /// Paper size (A5, A4, A3, A2, A1, A0, USLetter, USTabloid, USLedger)
    #[arg(short, long, default_value = "A4")]
    paper: String,

    /// Font family
    #[arg(short, long, default_value = "Sans")]
    font: Vec<String>,

    /// Locale
    #[arg(short, long, default_value = "en_US")]
    locale: String,

    /// Page margin in mm
    #[arg(long, default_value = "5")]
    margin: f64,

    /// Abbreviate weekdays
    #[arg(short = 'a')]
    abbreviate: bool,

    /// Abbreviate weekdays and months
    #[arg(short = 'A')]
    abbreviate_all: bool,

    /// Brand string
    #[arg(short, long, default_value = "")]
    brand: String,

    /// Color date numbers
    #[arg(short, long)]
    color: bool,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();
    let today = chrono::Local::now().date_naive();

    let paper = PaperSize::from_str(&cli.paper)
        .ok_or_else(|| format!("Unknown paper size: {}", cli.paper))?;

    let mut fonts = cli.font;
    let font = fonts.pop().unwrap_or_else(|| "Sans".into());
    let heading_font = fonts.pop();

    let config = Config {
        year: cli.year.unwrap_or(today.year()),
        month: cli.month.unwrap_or(today.month()),
        output: cli.output,
        paper,
        margin_mm: cli.margin,
        font,
        heading_font,
        locale: cli.locale,
        abbreviate: cli.abbreviate,
        abbreviate_all: cli.abbreviate_all,
        brand: cli.brand,
        color_numbers: cli.color,
    };

    let layout = layout::get_layout(&cli.layout).ok_or_else(|| {
        format!(
            "Unknown layout: {}. Available: {:?}",
            cli.layout,
            layout::LAYOUT_NAMES
        )
    })?;

    let page = PageSetup::new(config.paper, layout.orientation(), config.margin_mm);

    let canvas = canvas::Canvas::new(&config.output, &page)?;

    layout.draw(&canvas, &config, &page);

    // Canvas drops here, finishing the surface and writing the file
    drop(canvas);

    eprintln!("Written: {}", config.output);
    Ok(())
}
