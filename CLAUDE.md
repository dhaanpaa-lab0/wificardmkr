# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WiFi Card Maker is a Python tool that generates printable WiFi network cards by filling in an SVG template with network credentials and optionally converting the result to PDF format.

## Architecture

The project consists of a single unified script (**generate_card.py**) with two main capabilities:

1. **SVG Generation** - Template processor
   - Parses `WIFINetworkTemplate.svg` using lxml
   - Updates specific text elements (`WifiNetworkNameValue` and `WifiNetworkPasswordValue`) with user-provided credentials
   - Outputs a customized SVG file
   - Uses XPath with SVG namespace to locate and modify text elements

2. **PDF Conversion** - Optional post-processing
   - Uses svglib and reportlab to convert the generated SVG to PDF
   - Can be invoked together with SVG generation or standalone on existing SVG files
   - Outputs PDF with the same basename as the input SVG

## Development Setup

This project uses `uv` for dependency management (Python 3.14+).

**Install dependencies:**
```bash
uv sync
```

**Run scripts:**
Use `uv run python <script>` to execute scripts with the proper dependencies.

## Running the Tools

### Using the Shell Wrapper (Recommended)

The `wificard` shell script provides a convenient wrapper around the Python script.

**Note:** All outputs are automatically saved to the `output/` directory. The directory is created automatically if it doesn't exist. You can omit `output/` from the path - it will be added automatically.

**Interactive mode:**
```bash
./wificard
```

**Command-line mode (SVG only):**
```bash
./wificard -n "MyNetwork" -p "password123" -o mycard
```

**Command-line mode (SVG + PDF):**
```bash
./wificard -n "MyNetwork" -p "password123" -o mycard --pdf
```

**Convert existing SVG to PDF:**
```bash
./wificard -o mycard.svg --pdf-only
```

### Direct Python Invocation

Alternatively, you can run the Python script directly using `uv run`:

```bash
uv run python generate_card.py -n "MyNetwork" -p "password123" -o mycard --pdf
```

**Programmatic usage:**
```python
from generate_card import generate_card, convert_to_pdf

# Generate SVG (automatically goes to output/ directory)
svg_file = generate_card("NetworkName", "password123", "mycard.svg")

# Optionally convert to PDF
pdf_file = convert_to_pdf(svg_file)
```

## Key Dependencies

- **lxml** - XML/SVG parsing and manipulation with XPath support
- **svglib** - SVG to ReportLab graphics conversion
- **reportlab** - PDF generation

## Important Implementation Details

### SVG Template Structure

The template file `WIFINetworkTemplate.svg` must contain text elements with specific IDs:
- `WifiNetworkNameValue` - Placeholder for WiFi network name
- `WifiNetworkPasswordValue` - Placeholder for WiFi password

### Text Element Update Strategy

When updating SVG text elements (generate_card.py:7-21):
1. Clear direct text content of the parent `<text>` element
2. Remove all child elements (e.g., `<tspan>` elements) by iterating over a copy of the children list
3. Set new text value directly on the parent element

This approach ensures clean text replacement without leftover formatting artifacts.

## Output Directory

All generated files are automatically saved to the `output/` directory, which is:
- Created automatically if it doesn't exist
- Automatically prepended to output paths (so you can specify just `mycard` instead of `output/mycard`)
- Gitignored to keep the repository clean

The `ensure_output_path()` function (generate_card.py:14-33) handles this logic, ensuring consistent output location regardless of how the path is specified.
