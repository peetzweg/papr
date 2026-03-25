#!/bin/bash
# Visual regression test: compare Rust output against Python reference
# Usage: ./regression_test.sh
# Requires: ImageMagick (magick), Python papr in parent directory, Rust papr built

DIR=$(mktemp -d)
THRESHOLD=1.0  # Allow up to 1% pixel difference (sub-pixel rendering)

echo "=== Visual Regression Test ==="
echo "Temp dir: $DIR"
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

# Build Rust binary
echo "Building Rust binary..."
cargo build --manifest-path "$SCRIPT_DIR/Cargo.toml" 2>/dev/null
RUST_BIN="$SCRIPT_DIR/target/debug/papr"

if [ ! -x "$RUST_BIN" ]; then
  echo "FATAL: Rust binary not found at $RUST_BIN"
  exit 1
fi

FAILED=0

for layout in big classic column month oneyear; do
  # Generate Python reference
  (cd "$PARENT_DIR" && uv run papr $layout -o "$DIR/python_${layout}.pdf" -p A4 -y 2026 -m 3 2>/dev/null)

  # Generate Rust output
  "$RUST_BIN" $layout -o "$DIR/rust_${layout}.pdf" -p A4 -y 2026 -m 3 2>/dev/null

  # Rasterize both at 300 DPI
  magick -density 300 "$DIR/python_${layout}.pdf" -background white -alpha remove "$DIR/python_${layout}.png"
  magick -density 300 "$DIR/rust_${layout}.pdf" -background white -alpha remove "$DIR/rust_${layout}.png"

  # Compare
  dims=$(magick identify -format "%wx%h" "$DIR/python_${layout}.png")
  total_pixels=$(echo "$dims" | awk -Fx '{print $1 * $2}')

  raw=$(magick compare -metric AE "$DIR/python_${layout}.png" "$DIR/rust_${layout}.png" "$DIR/diff_${layout}.png" 2>&1)
  diff_pixels=$(echo "$raw" | sed 's/ .*//')

  pct=$(python3 -c "print(f'{$diff_pixels / $total_pixels * 100:.4f}')")
  pass=$(python3 -c "print('PASS' if $diff_pixels / $total_pixels * 100 <= $THRESHOLD else 'FAIL')")

  if [ "$pass" = "FAIL" ]; then
    FAILED=1
  fi

  echo "$pass  $layout: $diff_pixels pixels differ ($pct%) [$dims]"
done

echo ""
rm -rf "$DIR"

if [ $FAILED -eq 1 ]; then
  echo "FAILED: Some layouts exceed ${THRESHOLD}% pixel difference"
  exit 1
else
  echo "ALL PASSED: All layouts within ${THRESHOLD}% pixel difference"
  exit 0
fi
