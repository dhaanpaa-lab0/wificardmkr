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
   - Uses cairosvg to convert the generated SVG to PDF
   - Can be invoked together with SVG generation or standalone on existing SVG files
   - Outputs PDF with the same basename as the input SVG

## Development Setup

This project uses `uv` for dependency management (Python 3.14+).

**System dependencies:**

- **macOS:**
  ```bash
  brew install cairo
  ```

- **Windows:**
  - Install [GTK+ for Windows Runtime](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases) (recommended)
  - OR use conda: `conda install -c conda-forge cairo`
  - OR use MSYS2: `pacman -S mingw-w64-x86_64-cairo` and add to PATH

**Install Python dependencies:**
```bash
uv sync
```

**Run scripts:**
Use `uv run python <script>` to execute scripts with the proper dependencies.

### Platform-Specific Cairo Configuration

#### macOS

The `wificard` shell wrapper automatically sets `DYLD_FALLBACK_LIBRARY_PATH` to include Homebrew's library directory (`/opt/homebrew/lib` or `/usr/local/lib`). This allows `cairosvg` to find the Cairo graphics library installed by Homebrew.

If running Python scripts directly without the wrapper, you must manually set the environment variable:

```bash
export DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/lib:${DYLD_FALLBACK_LIBRARY_PATH}"
uv run python generate_card.py [arguments]
```

#### Windows

The `wificard` shell wrapper is for Unix-like systems only. On Windows, run the Python script directly:

```cmd
uv run python generate_card.py [arguments]
```

**Requirements:**
- Cairo DLLs must be in your PATH environment variable
- If using GTK+ installer with "Add to PATH" selected, this happens automatically
- If using conda, activate the conda environment first
- If using MSYS2, add the MinGW bin directory to PATH (e.g., `C:\msys64\mingw64\bin`)

## Running the Tools

### Using the Shell Wrapper (macOS/Linux)

The `wificard` shell script provides a convenient wrapper around the Python script for Unix-like systems (macOS, Linux, WSL). **Windows users should use Direct Python Invocation instead.**

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

### Direct Python Invocation (All Platforms)

You can run the Python script directly using `uv run`. **This is the required method for Windows users.**

```bash
# macOS/Linux/WSL
uv run python generate_card.py -n "MyNetwork" -p "password123" -o mycard --pdf
```

```cmd
REM Windows (Command Prompt)
uv run python generate_card.py -n "MyNetwork" -p "password123" -o mycard --pdf
```

```powershell
# Windows (PowerShell)
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
- **cairosvg** - SVG to PDF conversion using Cairo graphics library

## Important Implementation Details

### SVG Template Structure

The template file `WIFINetworkTemplate.svg` contains:

**Dynamic text elements** (updated by the script):
- `WifiNetworkNameValue` - Placeholder for WiFi network name (contains a tspan with the actual text)
- `WifiNetworkPasswordValue` - Placeholder for WiFi password (contains a tspan with the actual text)

**Static label elements** (not modified by the script):
- `text18` - "Password:" label with extra bold styling (`font-weight:900`, subtle stroke for emphasis)
- `text36` - "Network Name:" label with extra bold styling (`font-weight:900`, subtle stroke for emphasis)

### Text Element Update Strategy

When updating SVG text elements (generate_card.py:35-70):
1. Find the target `<text>` element by ID
2. Look for a `<tspan>` child element
3. If a tspan exists:
   - Update the tspan's text content (preserves styling attributes like `fill-opacity:1`, font-family, etc.)
   - Clear any direct text on the parent element
   - Remove all stroke-related properties from the tspan
   - Explicitly set `stroke:none` to prevent letter bunching
4. If no tspan exists (fallback):
   - Clear parent text and remove all children
   - Set new text directly on the parent element

**Why preserve the tspan?** The parent `<text>` element has `fill-opacity:0` (transparent fill), while the `<tspan>` child has `fill-opacity:1` (solid fill) and proper font styling. Preserving the tspan ensures the text renders with correct appearance.

**Why remove stroke?** The original tspan includes both fill and stroke (`stroke:#040404`, `stroke-width:1`). While the stroke helps in some SVG editors, when rendered to PDF via cairosvg, the stroke adds extra thickness to each character, causing letters to appear bunched together. Setting `stroke:none` ensures clean rendering with proper letter spacing.

## Output Directory

All generated files are automatically saved to the `output/` directory, which is:
- Created automatically if it doesn't exist
- Automatically prepended to output paths (so you can specify just `mycard` instead of `output/mycard`)
- Gitignored to keep the repository clean

The `ensure_output_path()` function (generate_card.py:14-33) handles this logic, ensuring consistent output location regardless of how the path is specified.

## Troubleshooting

### Cairo Library Not Found

#### macOS

**Error symptoms:**
```
OSError: no library called "cairo-2" was found
cannot load library 'libcairo.2.dylib'
```

**Solution:**

1. Install Cairo via Homebrew:
   ```bash
   brew install cairo
   ```

2. Use the `./wificard` wrapper script (recommended) - it automatically sets the library path

3. OR, if running Python directly, set the environment variable:
   ```bash
   export DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/lib:${DYLD_FALLBACK_LIBRARY_PATH}"
   ```

**Verification:**
Check that Cairo is installed and locate the library:
```bash
brew list cairo | grep -E '\.dylib$'
```

Should show `/opt/homebrew/Cellar/cairo/[version]/lib/libcairo.2.dylib`

#### Windows

**Error symptoms:**
```
OSError: no library called "cairo-2" was found
cannot load library 'cairo-2.dll'
cannot load library 'libcairo-2.dll'
```

**Solution:**

1. **Verify GTK+/Cairo installation:**
   - If using GTK+ installer: Check that it's installed in `C:\Program Files\GTK3-Runtime Win64\`
   - If using conda: Ensure the conda environment is activated
   - If using MSYS2: Check installation in MSYS2 directory

2. **Check PATH environment variable:**
   ```cmd
   echo %PATH%
   ```
   Should include one of:
   - `C:\Program Files\GTK3-Runtime Win64\bin` (GTK+ installer)
   - Your conda environment's Library\bin directory
   - `C:\msys64\mingw64\bin` (MSYS2)

3. **Add to PATH if missing:**
   - Open System Properties → Environment Variables
   - Edit the PATH variable
   - Add the appropriate bin directory from above
   - Restart your terminal/command prompt

4. **Reinstall with PATH option:**
   If using GTK+ installer, reinstall and ensure "Add to PATH" is checked

**Verification:**
Check that Cairo DLLs are accessible:
```cmd
where libcairo-2.dll
```
Should return the path to the Cairo DLL file.
