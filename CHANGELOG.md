# Changelog

## Unreleased

## [2.1.1](https://github.com/peetzweg/papr/compare/v2.1.0...v2.1.1) - 2026-04-06

### Fixed

- use HomePage.Root instead of HomePage in landing page MDX
- bump Node.js to 22 for docs build (vocs requires fs.globSync)

### Other

- add preview images for all layouts and fix image paths
- Merge pull request #58 from peetzweg/feature-vocs
- add Vocs documentation site with GitHub Pages deployment

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
