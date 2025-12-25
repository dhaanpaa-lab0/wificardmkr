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
- Cairo graphics library (for PDF conversion)
  - **macOS**: Install via Homebrew
  - **Windows**: Install GTK+ runtime or use conda

## Installation

1. Clone this repository

2. **Install Cairo graphics library** (required for PDF generation):

   **macOS:**
   ```bash
   brew install cairo
   ```

   **Windows:**

   Choose one of these options:

   - **Option 1 - GTK+ Runtime (Recommended)**:
     1. Download and install [GTK+ for Windows](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases)
     2. During installation, ensure "Add to PATH" is selected
     3. Restart your terminal/command prompt after installation

   - **Option 2 - Using Conda**:
     ```bash
     conda install -c conda-forge cairo
     ```

   - **Option 3 - MSYS2**:
     ```bash
     pacman -S mingw-w64-x86_64-cairo
     ```
     Then add the MSYS2 bin directory to your PATH

3. Install Python dependencies using uv:

```bash
uv sync
```

## Usage

### Interactive Mode (macOS/Linux)

Simply run the wrapper script and follow the prompts:

```bash
./wificard
```

**Windows users:** Use the Direct Python Usage method below instead.

### Command-Line Mode (macOS/Linux)

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

**Windows users:** Use the Direct Python Usage method below instead.

### Direct Python Usage

Run the Python script directly:

```bash
uv run python generate_card.py -n "MyNetwork" -p "password123" -o mycard --pdf
```

**Platform-specific notes:**

- **macOS**: If running the Python script directly (not using the `./wificard` wrapper), you need to set the library path first:
  ```bash
  export DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/lib:${DYLD_FALLBACK_LIBRARY_PATH}"
  uv run python generate_card.py -n "MyNetwork" -p "password123" -o mycard --pdf
  ```
  The `./wificard` wrapper script handles this automatically.

- **Windows**: Use the Python script directly (the shell wrapper is for Unix-like systems):
  ```cmd
  uv run python generate_card.py -n "MyNetwork" -p "password123" -o mycard --pdf
  ```
  Ensure GTK+/Cairo is in your PATH (should be automatic if you selected "Add to PATH" during installation).

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

### Python Packages

- **lxml** - XML/SVG parsing and manipulation with XPath support
- **cairosvg** - SVG to PDF conversion using Cairo graphics library

### System Libraries

- **Cairo** - Graphics library required by cairosvg for PDF generation
  - **macOS**: Install via Homebrew (`brew install cairo`)
    - The `./wificard` wrapper automatically configures the library path
  - **Windows**: Install via GTK+ runtime, conda, or MSYS2 (see Installation section)
    - Ensure Cairo DLLs are in your PATH environment variable

## How It Works

The tool processes the `WIFINetworkTemplate.svg` file to create customized WiFi cards:

1. **SVG Processing**:
   - Parses the template using lxml with XPath queries
   - Locates text elements by ID (`WifiNetworkNameValue` and `WifiNetworkPasswordValue`)
   - Preserves the nested `<tspan>` elements that contain critical styling (font, fill-opacity, etc.)
   - Updates only the text content while maintaining all formatting attributes
   - Removes stroke properties and sets `stroke:none` to ensure proper letter spacing

2. **PDF Conversion** (optional):
   - Uses cairosvg to render the SVG to PDF format
   - Produces print-ready output with correct font rendering and spacing

3. **Design Features**:
   - Bold labels ("Network Name:" and "Password:") with `font-weight:900` for emphasis
   - Clean, professional appearance with proper contrast between labels and values
   - All output automatically saved to the `output/` directory

## Troubleshooting

### Font Rendering Issues

If the generated PDF has font rendering problems (gray text, bunched letters, etc.):

1. **Ensure you're using the latest version** of the script with proper tspan handling
2. **Verify Cairo is installed** correctly (see Installation section)
3. **Check that the template** `WIFINetworkTemplate.svg` hasn't been modified

The script automatically:
- Preserves tspan styling for proper fill-opacity
- Removes stroke properties to prevent letter bunching
- Maintains correct font family (Arial) for consistent appearance

### Platform-Specific Issues

See the **Dependencies** section above for Cairo library setup on your platform (macOS or Windows).

## License

MIT
