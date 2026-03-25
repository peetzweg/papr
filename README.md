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

```
papr <LAYOUT> [OPTIONS]

Layouts: big, classic, column, month, oneyear

Options:
  -o, --output <FILE>     Output file (.pdf or .svg) [default: out.pdf]
  -y, --year <YEAR>       Year [default: current]
  -m, --month <MONTH>     Starting month 1-12 [default: current]
  -p, --paper <SIZE>      Paper size [default: A4]
                          (A5, A4, A3, A2, A1, A0, USLetter, USTabloid, USLedger)
  -f, --font <FONT>       Font family [default: Sans]
  -a                      Abbreviate weekdays
  -A                      Abbreviate weekdays and months
  -b, --brand <TEXT>      Brand string
  -c, --color             Color date numbers
      --margin <MM>       Page margin in mm [default: 5]
```

## Layouts

### month
Single month on a portrait page. Top 1/3 header with year and month, bottom 2/3 is a 7-column weekday grid with week numbers.

### big
Full year on a single landscape sheet. Days flow in rows with month flags. Supports starting at any month.

### classic
Two months in landscape, 4-page columnar layout.

### column
4 months in landscape, vertical columns with a folding margin.

### oneyear
Full year on one landscape sheet, 12 mini-columns.

![ScreenShot](oneyear_layout.png)
