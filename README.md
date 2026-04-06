[![codecov](https://codecov.io/gh/peetzweg/papr/branch/master/graph/badge.svg)](https://codecov.io/gh/peetzweg/papr)

# `papr` - Generate Calendar Stationeries

Command line tool to generate empty calendar templates to print. Outputs PDF and SVG.

![ScreenShot](demo.jpg)

## Quick Start

```sh
papr month -o calendar.pdf -y 2026 -p A4
papr month -o calendar.svg -y 2026 -p A4
papr big -o year.pdf -y 2026 -f 'Avenir Next' -p A3
```

## Installation

### Homebrew (macOS)

```sh
brew tap peetzweg/tap
brew install papr
```

### Cargo (from source)

Requires system libraries: Cairo and Pango.

```sh
# macOS
brew install pango cairo

# Debian/Ubuntu
apt install libpango1.0-dev libcairo2-dev

# Then install papr
cargo install --git https://github.com/peetzweg/papr
```

### From source (manual)

```sh
git clone https://github.com/peetzweg/papr.git
cd papr
cargo build --release
# Binary at ./target/release/papr
```

## Usage

Each layout is a **subcommand** with shared options and optional layout-specific flags:

```
papr <COMMAND> [OPTIONS]

Commands:
  month    Single month portrait calendar
  big      Full year landscape, days flow in rows
  classic  Two months landscape, columnar layout
  column   Four months landscape, vertical columns
  oneyear  Full year on one landscape sheet
  batch    Generate calendars from a YAML batch config
```

### Shared Options (all layout commands)

| Flag | Description | Default |
|------|-------------|---------|
| `-o, --output <FILE>` | Output file (`.pdf` or `.svg`, detected from extension) | `out.pdf` |
| `-y, --year <YEAR>` | Calendar year | current year |
| `-m, --month <MONTH>` | Starting month (1-12) | current month |
| `-p, --paper <SIZE>` | Paper size | `A4` |
| `-f, --font <FONT>` | Font family (pass twice for heading + body font) | `Sans` |
| `-l, --locale <LOCALE>` | Locale for date formatting | `en_US` |
| `--margin <MM>` | Page margin in millimeters | `5` |

**Paper sizes:** A5, A4, A3, A2, A1, A0, USLetter, USTabloid, USLedger

### Layout-Specific Options

Some layouts accept additional flags that only apply to them:

**`classic` and `column`:**

| Flag | Description |
|------|-------------|
| `-a` | Abbreviate weekday names |
| `-A` | Abbreviate both weekday and month names |

**`classic` only:**

| Flag | Description |
|------|-------------|
| `-b, --brand <TEXT>` | Brand string printed on the calendar |
| `-c, --color` | Color date numbers |

### Examples

```sh
# Portrait month calendar
papr month -o april.pdf -y 2026 -m 4 -p A4

# Full year with custom font on A3
papr big -o 2026.pdf -y 2026 -f 'Avenir Next' -p A3

# Classic layout with abbreviated weekdays and branding
papr classic -o classic.pdf -y 2026 -a -b "My Calendar" -c

# Four-month column layout, starting June
papr column -o summer.pdf -y 2026 -m 6

# One-year overview with separate heading font
papr oneyear -o overview.svg -y 2026 -f Sans -f 'Georgia'

# SVG output (detected from file extension)
papr month -o calendar.svg
```

## Layouts

### `month`

Single month on a **portrait** page. The top third is a header with year and month name. The bottom two thirds is a 7-column (Mon-Sun) grid with 6 rows. Week numbers appear on Mondays.

### `big`

Full year on a single **landscape** sheet. Days flow left-to-right in rows of 21 columns. Month boundaries are marked with colored flag labels. Supports starting at any month with year-transition labels.

### `classic`

Two months in **landscape** orientation. Uses a 4-page columnar layout designed for back-to-back printing -- the first month is rotated 180 degrees. Supports brand text, colored numbers, and weekday/month abbreviation.

### `column`

Four months in **landscape**, each in a vertical column. Includes a folding margin after day 15, so the calendar can be folded in half. Supports weekday and month abbreviation.

### `oneyear`

Full year on one **landscape** sheet as 12 mini-columns (one per month). Uses a separate heading font for month titles if provided via a second `-f` flag. Weekday names are shown as single letters.

![ScreenShot](oneyear_layout.png)

## Batch Mode

Generate many calendars at once from a single YAML file, using GitHub Actions-style **matrix expansion**:

```sh
papr batch config.yaml
```

The matrix computes the Cartesian product of all listed values, so every combination is generated. Use `exclude` to skip specific ones.

### YAML Schema

```yaml
# Default values applied to every combination
defaults:
  year: 2026
  font: "Avenir Next"
  paper: A4
  margin: 5

# Matrix axes — Cartesian product of all lists
matrix:
  layout: [month, big, classic, oneyear]
  paper: [A4, A3]
  month: [1, 6]

# Skip specific combinations (all keys in an entry must match)
exclude:
  - layout: big
    paper: A3
    month: 6

# Per-layout options for layouts with custom flags
layout_options:
  classic:
    abbreviate: true
    brand: "My Brand"
    color: true
  column:
    abbreviate_all: true

# Output path template — {key} placeholders are replaced
output: "calendars/{layout}_{year}_{month}_{paper}.pdf"
```

### Template Variables

Use `{key}` in the `output` path. Available variables: `layout`, `year`, `month`, `paper`, `font`, `locale`, `margin`. Values come from the matrix combination first, then fall back to `defaults`.

### Batch Error Handling

All combinations are attempted even if some fail. A summary is printed at the end showing successes and failures, and the exit code is non-zero if anything failed.

### Example

Given the YAML above (4 layouts x 2 papers x 2 months = 16, minus 1 excluded = 15):

```
$ papr batch config.yaml
Matrix expanded to 15 combination(s)
[1/15] calendars/month_2026_1_A4.pdf ... Written: calendars/month_2026_1_A4.pdf
[2/15] calendars/month_2026_1_A3.pdf ... Written: calendars/month_2026_1_A3.pdf
...
All 15 file(s) generated successfully.
```

Output directories are created automatically.

## Architecture

### CLI Design

The CLI uses **subcommands per layout** rather than a single flat argument list. This allows each layout to define its own flags without polluting the global namespace. Shared options (year, month, paper, font, etc.) are defined once in a `SharedArgs` struct and flattened into every subcommand via clap's `#[command(flatten)]`.

This design means adding a new layout-specific option (e.g., `--days-per-row` for `big`) only requires adding a field to that layout's args struct -- no changes to shared code.

### Project Structure

```
src/
  main.rs          CLI entry point, subcommand dispatch, render_one()
  config.rs        Config struct (shared fields), PaperSize, PageSetup
  batch.rs         YAML batch mode: parsing, matrix expansion, orchestration
  canvas.rs        Drawing API wrapping Cairo + Pango (PDF/SVG)
  calendar.rs      Date utilities (day iteration, weekends, month spans)
  style.rs         Color constants and visual defaults
  layout/
    mod.rs         Layout trait definition
    month.rs       Month layout (portrait, 7-col grid)
    big.rs         Big layout (landscape, day rows with flags)
    classic.rs     Classic layout (landscape, 2-month columnar)
    column.rs      Column layout (landscape, 4-month vertical)
    oneyear.rs     One-year layout (landscape, 12 mini-columns)
```

### Rendering Pipeline

1. **CLI parsing** -- clap parses subcommand + args into typed structs
2. **Config construction** -- `build_config()` resolves paper size, font stack, year/month defaults
3. **Layout construction** -- layout struct created with any layout-specific options
4. **Page setup** -- paper dimensions resolved for the layout's orientation (portrait/landscape)
5. **Canvas creation** -- Cairo surface created (PDF or SVG based on output file extension)
6. **Drawing** -- `layout.draw()` renders the calendar onto the canvas
7. **Output** -- canvas drops, surface finishes, file is written

In batch mode, steps 2-7 are repeated for each matrix combination.

### Layout Trait

Every layout implements a simple trait:

```rust
pub trait Layout {
    fn orientation(&self) -> Orientation;  // Portrait or Landscape
    fn draw(&self, canvas: &Canvas, config: &Config, page: &PageSetup);
}
```

The `Config` struct carries shared fields (year, month, font, paper, etc.). Layout-specific options are stored as fields on the layout struct itself and accessed via `self` during drawing. This separation keeps `Config` lean and lets each layout own its customization.

### Dependencies

| Crate | Purpose |
|-------|---------|
| `cairo-rs` | 2D rendering to PDF and SVG surfaces |
| `pango` / `pangocairo` | Text layout, shaping, and font handling |
| `clap` | CLI argument parsing with derive macros |
| `chrono` | Date calculations (weekdays, leap years, month spans) |
| `serde` / `serde_yml` | YAML deserialization for batch mode |
