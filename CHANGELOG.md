# Changelog

## Unreleased

### Added

- **Batch mode** with GitHub Actions-style matrix expansion (`papr batch config.yaml`) (`#51`)
- YAML schema with `defaults`, `matrix`, `exclude`, `layout_options`, and output path templates
- CI workflow for code coverage reporting using `cargo-llvm-cov` and Codecov (`#48`)
- Codecov badge in README

### Changed

- **CLI refactored to subcommands** -- each layout is now a subcommand (`papr month`, `papr big`, etc.) instead of a positional argument
- Layout-specific options (`-a`, `-A`, `-b`, `-c`) moved from global flags to only the layouts that use them (`classic`, `column`)
- `Config` struct slimmed to shared-only fields; layout-specific options stored on layout structs
