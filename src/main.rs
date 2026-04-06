#![allow(clippy::too_many_arguments)]

use chrono::{Datelike, NaiveDate};
use clap::{Args, Parser, Subcommand};

mod batch;
mod calendar;
mod canvas;
mod config;
mod layout;
mod style;

use config::{Config, PageSetup, PaperSize};
use layout::Layout;

/// Shared CLI options used by all layouts.
#[derive(Args)]
struct SharedArgs {
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
}

#[derive(Args)]
struct MonthArgs {
    #[command(flatten)]
    shared: SharedArgs,
}

#[derive(Args)]
struct BigArgs {
    #[command(flatten)]
    shared: SharedArgs,
}

#[derive(Args)]
struct ClassicArgs {
    #[command(flatten)]
    shared: SharedArgs,

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

#[derive(Args)]
struct ColumnArgs {
    #[command(flatten)]
    shared: SharedArgs,

    /// Abbreviate weekdays
    #[arg(short = 'a')]
    abbreviate: bool,

    /// Abbreviate weekdays and months
    #[arg(short = 'A')]
    abbreviate_all: bool,
}

#[derive(Args)]
struct OneyearArgs {
    #[command(flatten)]
    shared: SharedArgs,
}

#[derive(Parser)]
#[command(name = "papr", about = "Generate printable calendar PDFs and SVGs")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Args)]
struct BatchArgs {
    /// Path to YAML configuration file
    config: String,
}

#[derive(Subcommand)]
enum Commands {
    /// Single month portrait calendar
    Month(MonthArgs),
    /// Full year landscape, days flow in rows
    Big(BigArgs),
    /// Two months landscape, columnar layout
    Classic(ClassicArgs),
    /// Four months landscape, vertical columns
    Column(ColumnArgs),
    /// Full year on one landscape sheet
    Oneyear(OneyearArgs),
    /// Generate calendars from a YAML batch config
    Batch(BatchArgs),
}

fn build_config(shared: SharedArgs, today: &NaiveDate) -> Result<Config, Box<dyn std::error::Error>> {
    let paper = PaperSize::from_str(&shared.paper)
        .ok_or_else(|| format!("Unknown paper size: {}", shared.paper))?;

    let mut fonts = shared.font;
    let font = fonts.pop().unwrap_or_else(|| "Sans".into());
    let heading_font = fonts.pop();

    Ok(Config {
        year: shared.year.unwrap_or(today.year()),
        month: shared.month.unwrap_or(today.month()),
        output: shared.output,
        paper,
        margin_mm: shared.margin,
        font,
        heading_font,
        locale: shared.locale,
    })
}

fn render_one(layout: &dyn Layout, config: &Config) -> Result<(), Box<dyn std::error::Error>> {
    let page = PageSetup::new(config.paper, layout.orientation(), config.margin_mm);
    let canvas = canvas::Canvas::new(&config.output, &page)?;
    layout.draw(&canvas, config, &page);
    drop(canvas);
    eprintln!("Written: {}", config.output);
    Ok(())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();
    let today = chrono::Local::now().date_naive();

    match cli.command {
        Commands::Month(args) => {
            let config = build_config(args.shared, &today)?;
            render_one(&layout::month::MonthLayout, &config)
        }
        Commands::Big(args) => {
            let config = build_config(args.shared, &today)?;
            render_one(&layout::big::BigLayout, &config)
        }
        Commands::Classic(args) => {
            let config = build_config(args.shared, &today)?;
            let layout = layout::classic::ClassicLayout {
                abbreviate: args.abbreviate,
                abbreviate_all: args.abbreviate_all,
                brand: args.brand,
                color_numbers: args.color,
            };
            render_one(&layout, &config)
        }
        Commands::Column(args) => {
            let config = build_config(args.shared, &today)?;
            let layout = layout::column::ColumnLayout {
                abbreviate: args.abbreviate,
                abbreviate_all: args.abbreviate_all,
            };
            render_one(&layout, &config)
        }
        Commands::Oneyear(args) => {
            let config = build_config(args.shared, &today)?;
            render_one(&layout::oneyear::OneYearLayout, &config)
        }
        Commands::Batch(args) => batch::run_batch(&args.config),
    }
}
