# Changelog

## Unreleased

## [2.1.0](https://github.com/peetzweg/papr/compare/v2.0.0...v2.1.0) - 2026-04-06

### Added

- add batch mode with matrix expansion and refactor CLI to subcommands

### Fixed

- resolve cargo fmt and clippy CI failures, add pre-commit hook
- drop x86_64-apple-darwin build, simplify Homebrew formula
- use macos-14 for x86_64 cross-compile, macos-13 deprecated
- add workflow_dispatch trigger to binary builds
- trigger binary builds on tag push instead of release event

### Added

- **Batch mode** with GitHub Actions-style matrix expansion (`papr batch config.yaml`) (`#51`)
- YAML schema with `defaults`, `matrix`, `exclude`, `layout_options`, and output path templates
- CI workflow for code coverage reporting using `cargo-llvm-cov` and Codecov (`#48`)
- Codecov badge in README

### Changed

- **CLI refactored to subcommands** -- each layout is now a subcommand (`papr month`, `papr big`, etc.) instead of a positional argument
- Layout-specific options (`-a`, `-A`, `-b`, `-c`) moved from global flags to only the layouts that use them (`classic`, `column`)
- `Config` struct slimmed to shared-only fields; layout-specific options stored on layout structs
