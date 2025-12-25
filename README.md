# WiFi Card Maker

A Python tool for generating printable WiFi network cards. Create beautiful, customized cards with your network credentials in SVG or PDF format.

## Features

- Generate customized WiFi network cards from an SVG template
- Automatic PDF conversion support
- Interactive or command-line modes
- Clean, printable output
- Simple shell wrapper for easy usage

## Requirements

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) package manager

## Installation

1. Clone this repository
2. Install dependencies using uv:

```bash
uv sync
```

## Usage

### Interactive Mode

Simply run the wrapper script and follow the prompts:

```bash
./wificard
```

### Command-Line Mode

Generate an SVG card:

```bash
./wificard -n "MyNetwork" -p "password123" -o mycard
```

Generate both SVG and PDF:

```bash
./wificard -n "MyNetwork" -p "password123" -o mycard --pdf
```

Convert an existing SVG to PDF:

```bash
./wificard -o mycard.svg --pdf-only
```

### Direct Python Usage

Run the Python script directly:

```bash
uv run python generate_card.py -n "MyNetwork" -p "password123" -o mycard --pdf
```

### Programmatic Usage

Import and use in your own Python code:

```python
from generate_card import generate_card, convert_to_pdf

# Generate SVG
svg_file = generate_card("NetworkName", "password123", "mycard.svg")

# Convert to PDF
pdf_file = convert_to_pdf(svg_file)
```

## Output

All generated files are automatically saved to the `output/` directory. The directory is created automatically if it doesn't exist.

## Dependencies

- **lxml** - XML/SVG parsing and manipulation
- **svglib** - SVG to ReportLab graphics conversion
- **reportlab** - PDF generation

## How It Works

The tool parses the `WIFINetworkTemplate.svg` file, updates the network name and password placeholders with your credentials, and saves the customized SVG. Optionally, it can convert the result to PDF format for easy printing.

## License

MIT
