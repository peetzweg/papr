# Changelog

## Unreleased

## [2.0.0](https://github.com/peetzweg/papr/releases/tag/v2.0.0) - 2026-03-26

### Added

- rename crate to papr-cli for crates.io publishing
- replace Python with Rust, bump to v2.0.0
- add visual regression test comparing Rust vs Python output ([#47](https://github.com/peetzweg/papr/pull/47))
- port big layout to Rust ([#46](https://github.com/peetzweg/papr/pull/46))
- port classic layout to Rust ([#45](https://github.com/peetzweg/papr/pull/45))
- port month layout to Rust ([#44](https://github.com/peetzweg/papr/pull/44))
- port oneyear layout to Rust ([#43](https://github.com/peetzweg/papr/pull/43))
- add Rust rewrite foundation with column layout (#35-#42)

### Changed

- changed small details in the demo image
- changed example picture to a more product shot like image
- changed day representation from alternating on a page to two column
- changed color scheme of the logo

### Fixed

- install system deps in release workflow
- disable crates.io publish, crate name taken
- resolve clippy warnings for CI
- fixed #18
- fixed yOffset in the column layout, which was calculated wrong and only showed on bigger paper sizes
- fixed debug option, which was not working properly since the change to argparse
- fixed an issue with the locales on osx and improved error message if locale is not found
- fixed an issue with the -b option, now works correctly again

### Other

- apply cargo fmt to all source files
- add automated release pipeline with release-plz
- add Codecov coverage reporting workflow and badge
- add .gitignore and remove target/ from tracking
- use proper color for year as well
- adds new layout 'month'
- removes not available layout rows
- big year now supports starting at a specified month
- ignore test.sh output folder
- adds script to generate permutations
- ingnore output
- script to prepare publishable product
- fallback highest dpi for home printers if needed
- makes it possible to export as svg as well
- Merge pull request #24 from peetzweg/us-sizes
- adds us tabloid & ledger sizes
- working big year layout
- big year layout
- Configure uv package mode and update documentation
- Update README to recommend Homebrew installation
- Bump version to 1.0.0
- Update author info and remove build-system config
- Migrate project to use uv package manager
- updates README with install steps for python3 on MacOS
- adds information about dependencies to readme
- Merge pull request #19 from kspi/master
- ignoring OS X spotlight files
- updated usage in readme and added oneyear layout example image
- now available to specify two fonts
- added a bunch of new DIN ISO paper formats which closes issue #13
- tweaked the design of the oneyear layout. More space for writing and bigger date numbers
- added new layout called 'oneyear', which is a whole year calendar on one page. This is the second layout request in #9. So #9 is closed
- added a new layout called 'column', the old one is called 'classic'. A Layout must now be provided as positional argument. Also replaced the deprecated optparse with argparse
- added new style, but not yet usable through commandline
- did a bit of code cleanup and used PEP8 Styleguide for indention and formating
- splitted papr in mutiple files to be able to implement new styles as mentioned in #9
- added -c/--color option to make day numbers red, very simple implementation. Not sure if i will keep it
- added the --margin option to specify the page margin of the calendar to adapt to different printers. Closes #3
- implemented the -p/--paper option to specify the paper format,
- added parts of the new -p/--paper option to specifiy the size of paper to use, but WIP
- improved option parsing, by using the choice type for fonts and implemented a CalendarOption class for year and month checks. Closes #6
- added option to specify the year, to be able to generate calendars for 2015. Closes #5
- added download link to the latest generated pdf file of the calendar
- year is now incremented if december is the first month to draw, which
- added option to add an additional branding string (-b)
- added a demo image to the repository for the README file
- Merge branch 'master' of https://github.com/Pczek/papr
- updated quick start section of the README
- implemented new cli option -m/--month to specify from which month the
- Merge branch 'master' of github.com:Pczek/papr
- added single page with smooth scroll, added donation (placeholder)
- split -a option into -a to abbreviate only weekdays and -A/--abbreviate_all to abbreviate weekdays and months
- Merge branch 'master' of github.com:pczek/papr
- month string now automatically resizes if it is to big
- now drawing the day text with pango instead of cairo toy
- formated code
- refactored main method
- added logo svg
- added web content and flask project
- turned Quick Start section content into a code block
- implemented -f/--font option, now work correctly
- * made option variable global (g_options)
- Merge branch 'master' of github.com:Pczek/papr
- new options -a/--abreviate now allows to use abbreviations of day and
- added help to readme and changed introduction sentence
- renamed date variable to dateObject to make it clear a date object is
- added support for different languages via option -l/--locale to choose
- seperated --log option into --verbose for status messages and --debug for status and debug messages
- cleaned up the code a bit and reduced output messages
- weekends are now colored gray
- calendar creation now works!
- drawing a month now works fine!
- drawing the first page kind of works
- added basic structure to the readme file
- Merge branch 'master' of github.com:pczek/papr
- Initial commit

### Removed

- removed very verbose debug information
- removed global variable g_options and introduced a new enviroment variable which is passed down
- removed table of contents
- removed web folder, maybe adding it back in the future
- removed calendar branding
- removed wip logo file

### Added

- CI workflow for code coverage reporting using `cargo-llvm-cov` and Codecov (`#48`)
- Codecov badge in README
