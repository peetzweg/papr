#!/bin/bash

# Set libffi paths for pygobject compilation (required on macOS)
export LDFLAGS="-L/opt/homebrew/opt/libffi/lib"
export CPPFLAGS="-I/opt/homebrew/opt/libffi/include"
export PKG_CONFIG_PATH="/opt/homebrew/opt/libffi/lib/pkgconfig"

# Prevent Python from using cached bytecode (ensures latest source is always used)
export PYTHONDONTWRITEBYTECODE=1

# Configuration arrays - add/remove values as needed
years=(2026)
# months=(1 2 3 4 5 6 7 8 9 10 11 12)
months=(1 2 )
layouts=("month")
fonts=("Avenir Next")
locales=("en_US")
sizes=("A3" "USLedger")

# Output folder
OUTPUT_DIR="test"

# Maximum number of parallel jobs (adjust based on your CPU cores)
MAX_JOBS=${MAX_JOBS:-8}


# Function to sanitize font name (remove spaces)
sanitize_font() {
    echo "$1" | tr -d ' '
}

# Function to sanitize locale name (replace special chars with hyphens)
sanitize_locale() {
    echo "$1" | tr '_.' '-' | tr '[:lower:]' '[:upper:]'
}

# Function to process a single combination
process_combination() {
    local year=$1
    local month=$2
    local layout=$3
    local font=$4
    local locale=$5
    local size=$6
    local current=$7
    local total=$8

    # Create sanitized names
    local sanitized_font=$(sanitize_font "$font")
    local sanitized_locale=$(sanitize_locale "$locale")

    # Build filename with all encoded options
    local base_name="${layout}-${year}-${month}-${sanitized_font}-${sanitized_locale}-${size}"
    local pdf_filename="${base_name}.pdf"
    local svg_filename="${base_name}.svg"
    local png_filename="${base_name}.png"
    local pdf_file="${OUTPUT_DIR}/${pdf_filename}"
    local svg_file="${OUTPUT_DIR}/${svg_filename}"
    local png_file="${OUTPUT_DIR}/${png_filename}"

    echo "[${current}/${total}] Processing: ${base_name}..."

    # Generate PDF and SVG
    uv run python -m papr.papr "${layout}" -y "${year}" -p "${size}" -m "${month}" -l "${locale}" -o "${pdf_file}" --font "${font}" && \
    uv run python -m papr.papr "${layout}" -y "${year}" -p "${size}" -m "${month}" -l "${locale}" -o "${svg_file}" --font "${font}" && \
    magick -density 300 "${pdf_file}" -background white -alpha remove -alpha off "${png_file}"

    # Write JSON entry to temp file
    local json_entry="{\"id\":\"${base_name}\",\"name\":\"${base_name}\",\"size\":\"${size}\",\"layout\":\"${layout}\",\"font\":\"${font}\",\"year\":${year},\"month\":${month},\"locale\":\"${locale}\",\"png\":\"${png_filename}\",\"pdf\":\"${pdf_filename}\",\"svg\":\"${svg_filename}\"}"
    echo "${json_entry}" >> "${OUTPUT_DIR}/.json_entries.tmp"
}

# Remove existing test folder and recreate
if [ -d "${OUTPUT_DIR}" ]; then
    echo "Removing existing ${OUTPUT_DIR} folder..."
    rm -rf "${OUTPUT_DIR}"
fi
mkdir -p "${OUTPUT_DIR}"

# Initialize temp file for JSON entries
rm -f "${OUTPUT_DIR}/.json_entries.tmp"
touch "${OUTPUT_DIR}/.json_entries.tmp"

# Calculate total combinations for progress
total_combinations=$(( ${#years[@]} * ${#months[@]} * ${#layouts[@]} * ${#fonts[@]} * ${#locales[@]} * ${#sizes[@]} ))
current=0

# Export functions and variables for parallel execution
export -f sanitize_font sanitize_locale process_combination
export OUTPUT_DIR

echo "Processing ${total_combinations} combinations with up to ${MAX_JOBS} parallel jobs..."
echo ""

# Loop through all combinations and run in parallel
for year in "${years[@]}"; do
    for month in "${months[@]}"; do
        for layout in "${layouts[@]}"; do
            for font in "${fonts[@]}"; do
                for locale in "${locales[@]}"; do
                    for size in "${sizes[@]}"; do
                        current=$((current + 1))

                        # Wait if we've reached max jobs
                        while [ $(jobs -r | wc -l) -ge ${MAX_JOBS} ]; do
                            sleep 0.1
                        done

                        # Run in background
                        process_combination "${year}" "${month}" "${layout}" "${font}" "${locale}" "${size}" "${current}" "${total_combinations}" &
                    done
                done
            done
        done
    done
done

# Wait for all background jobs to complete
wait

echo ""
echo "All jobs completed. Generating product.json..."

# Generate product.json file from collected entries
product_json="${OUTPUT_DIR}/product.json"
echo "[" > "${product_json}"
first=true
while IFS= read -r line; do
    if [ "$first" = true ]; then
        first=false
    else
        echo "," >> "${product_json}"
    fi
    echo "  ${line}" >> "${product_json}"
done < "${OUTPUT_DIR}/.json_entries.tmp"
echo "]" >> "${product_json}"

# Clean up temp file
rm -f "${OUTPUT_DIR}/.json_entries.tmp"

echo ""
echo "All ${total_combinations} combinations processed!"
echo "Output saved to ${OUTPUT_DIR}/"
echo "product.json created with all entries"
