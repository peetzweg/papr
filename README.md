# `papr` - Generate Calendar Stationeries

Command line tool to generate a empty calendar templates to print.

![ScreenShot](demo.jpg)

## Info

Papr currently only produces a PDF output. When you are printing the PDF file make sure you have to automated positioning or resizing features of your printer enabled!

## Quick start

```sh
papr -y 2023 -m 2 -f='Avenir Next' -p A3 oneyear
```

```sh
usage: papr.py [-h] [-o OUT] [-A] [-a] [-b BRAND] [-c] [-f FONT [FONT ...]]
                   [-l LOCALE] [-m MONTH] [-y YEAR]
                   [-p {A5,A4,A3,A2,A1,A0,USLetter}] [--margin MARGIN] [-v] [-d]
                   LAYOUT

    Create a Calendar

    positional arguments:
      LAYOUT                choose calendar layout: ('classic', 'column',
                            'oneyear')

    optional arguments:
      -h, --help            show this help message and exit
      -o OUT, --out OUT     specify output file
      -A, --abbreviate_all  use abbreviations for weekdays and months
      -a, --abbreviate      use abbreviations for weekdays
      -b BRAND, --brand BRAND
                            assign a brand string
      -c, --color           color date numbers
      -f FONT [FONT ...], --fonts FONT [FONT ...]
                            choose which font to use
      -l LOCALE, --locale LOCALE
                            choose locale to use (default en_US.UTF8, check
                            'locale -a' for available locales)
      -m MONTH, --month MONTH
                            specify the starting month as a number (1-12), default
                            is the current month (3).
      -y YEAR, --year YEAR  specify the year the calendar should start, default is
                            the current year (2016).
      -p {A5,A4,A3,A2,A1,A0,USLetter}, --paper {A5,A4,A3,A2,A1,A0,USLetter}
                            choose which paper dimensions should be used ('A5',
                            'A4', 'A3', 'A2', 'A1', 'A0', 'USLetter') default is
                            A4
      --margin MARGIN       specify the margin of the calendar in millimeters.
                            Used to adapt to your printer, default ist 5mm
      -v, --verbose         print status messages to stdout
      -d, --debug           print status and debug messages to stdout
```

## Installation

### Homebrew (Recommended)

The easiest way to install `papr` on macOS:

```sh
brew tap peetzweg/tap
brew install papr
```

That's it! The `papr` command is now available globally.

Note: First installation takes 3-5 minutes as it compiles dependencies.

### Using uv

[uv](https://docs.astral.sh/uv/) is a fast Python package manager for development.

1. Install system dependencies using [homebrew](https://brew.sh/):

```sh
brew install pygobject3
```

2. Install `uv` if you haven't already:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Clone the repository:

```sh
git clone https://github.com/peetzweg/papr.git
cd papr
```

4. Install the project with uv:

```sh
uv sync
```

5. Run `papr` using uv:

```sh
uv run papr -y 2023 -m 2 -f='Avenir Next' -p A3 oneyear
```

### Manual Installation

1. Install `git` and `python3` run this in your terminal:

```sh
xcode-select --install
```

2. Install `pygobject3` for python3 using [homebrew](https://brew.sh/)

```sh
brew install pygobject3
```

3. Clone repository using `git`

```sh
git clone https://github.com/peetzweg/papr.git
```

4. Use `papr` CLI arguments to create your calendar, see [Quick Start Section](#quick-start)

## Layouts

### oneyear
![ScreenShot](oneyear_layout.png)
