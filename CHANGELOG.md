# Changelog

## Unreleased

### Added

- **Documentation site** using [Vocs](https://vocs.dev) with individual pages per layout, CLI reference, and batch mode guide
- GitHub Actions workflow to deploy docs to GitHub Pages (`deploy-docs.yml`)
- CLI help snapshot check in CI to detect docs/CLI drift (`docs/cli-help-snapshot.txt`)
- Helper script to regenerate CLI help snapshot (`scripts/update-help-snapshot.sh`)
- **Batch mode** with GitHub Actions-style matrix expansion (`papr batch config.yaml`) (`#51`)
- YAML schema with `defaults`, `matrix`, `exclude`, `layout_options`, and output path templates
- CI workflow for code coverage reporting using `cargo-llvm-cov` and Codecov (`#48`)
- Codecov badge in README

### Changed

- **CLI refactored to subcommands** -- each layout is now a subcommand (`papr month`, `papr big`, etc.) instead of a positional argument
- Layout-specific options (`-a`, `-A`, `-b`, `-c`) moved from global flags to only the layouts that use them (`classic`, `column`)
- `Config` struct slimmed to shared-only fields; layout-specific options stored on layout structs
