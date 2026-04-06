#!/bin/sh
# Regenerates docs/cli-help-snapshot.txt from the current binary.
# Run after changing CLI arguments to keep docs in sync.
set -e

BIN="${1:-./target/release/papr}"

if [ ! -f "$BIN" ]; then
  echo "Binary not found at $BIN — run 'cargo build --release' first."
  exit 1
fi

{
  echo "=== papr ===" && "$BIN" --help && echo ""
  echo "=== papr month ===" && "$BIN" month --help && echo ""
  echo "=== papr big ===" && "$BIN" big --help && echo ""
  echo "=== papr classic ===" && "$BIN" classic --help && echo ""
  echo "=== papr column ===" && "$BIN" column --help && echo ""
  echo "=== papr oneyear ===" && "$BIN" oneyear --help && echo ""
  echo "=== papr batch ===" && "$BIN" batch --help
} > docs/cli-help-snapshot.txt

echo "Updated docs/cli-help-snapshot.txt"
