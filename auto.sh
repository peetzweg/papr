#!/bin/bash

# Configuration variables
YEAR=2026
MONTH=1
LAYOUT="big"
FONT="Avenir Next"
LOCALE="en_US"

# Array of paper sizes
sizes=("A3" "A4" "USLetter" "USLedger")

# Function to sanitize font name (remove spaces)
sanitize_font() {
    echo "$1" | tr -d ' '
}

# Function to sanitize locale name (replace special chars with hyphens)
sanitize_locale() {
    echo "$1" | tr '_.' '-' | tr '[:lower:]' '[:upper:]'
}

# Create sanitized font name for folder/file names
SANITIZED_FONT=$(sanitize_font "$FONT")

# Create sanitized locale name for folder/file names
SANITIZED_LOCALE=$(sanitize_locale "$LOCALE")

# Create folder name with encoded options
FOLDER="${YEAR}-${MONTH}-${LAYOUT}-${SANITIZED_FONT}-${SANITIZED_LOCALE}"

# Create the folder if it doesn't exist
mkdir -p "${FOLDER}"

# Initialize JSON array
json_entries=()

# Loop through each size
for size in "${sizes[@]}"; do
    pdf_filename="${YEAR}-${MONTH}-${LAYOUT}-${SANITIZED_FONT}-${SANITIZED_LOCALE}-${size}.pdf"
    svg_filename="${YEAR}-${MONTH}-${LAYOUT}-${SANITIZED_FONT}-${SANITIZED_LOCALE}-${size}.svg"
    png_filename="${YEAR}-${MONTH}-${LAYOUT}-${SANITIZED_FONT}-${SANITIZED_LOCALE}-${size}.png"
    pdf_file="${FOLDER}/${pdf_filename}"
    svg_file="${FOLDER}/${svg_filename}"
    png_file="${FOLDER}/${png_filename}"

    echo "Processing ${size}..."
    uv run python -m papr.papr "${LAYOUT}" -y "${YEAR}" -p "${size}" -m "${MONTH}" -l "${LOCALE}" -o "${pdf_file}" --font "${FONT}" && \
    uv run python -m papr.papr "${LAYOUT}" -y "${YEAR}" -p "${size}" -m "${MONTH}" -l "${LOCALE}" -o "${svg_file}" --font "${FONT}"
    magick -density 300 "${pdf_file}" -background white -alpha remove -alpha off "${png_file}"

    # Add entry to JSON array
    json_entries+=("{\"id\":\"${size}\",\"name\":\"${size}\",\"size\":\"${size}\",\"layout\":\"${LAYOUT}\",\"font\":\"${FONT}\",\"year\":${YEAR},\"month\":${MONTH},\"locale\":\"${LOCALE}\",\"png\":\"${png_filename}\",\"pdf\":\"${pdf_filename}\",\"svg\":\"${svg_filename}\"}")

done

# Generate product.json file
product_json="${FOLDER}/product.json"
echo "[" > "${product_json}"
for i in "${!json_entries[@]}"; do
    if [ $i -gt 0 ]; then
        echo "," >> "${product_json}"
    fi
    echo "  ${json_entries[$i]}" >> "${product_json}"
done
echo "]" >> "${product_json}"

echo "All sizes processed!"
echo "product.json created in ${FOLDER}/"
