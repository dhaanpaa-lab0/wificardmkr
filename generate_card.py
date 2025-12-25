import sys
import os
import argparse
from pathlib import Path
from lxml import etree
import cairosvg
import segno
from io import BytesIO

TEMPLATE_FILE = "WIFINetworkTemplate.svg"
SVG_NS = {"svg": "http://www.w3.org/2000/svg"}
OUTPUT_DIR = "output"


def ensure_output_path(file_path: str) -> str:
    """Ensure the file path is in the output directory.

    Args:
        file_path: The desired output file path

    Returns:
        The normalized path within the output directory
    """
    path = Path(file_path)

    # Create output directory if it doesn't exist
    Path(OUTPUT_DIR).mkdir(exist_ok=True)

    # If path is absolute or already starts with output/, use as is
    if path.is_absolute() or str(path).startswith(f"{OUTPUT_DIR}/") or str(path).startswith(f"{OUTPUT_DIR}\\"):
        return str(path)

    # Otherwise, prepend output/ directory
    return str(Path(OUTPUT_DIR) / path)


def escape_wifi_string(text: str) -> str:
    """Escape special characters for WiFi QR code format.

    Args:
        text: The string to escape (SSID or password)

    Returns:
        Escaped string safe for WiFi QR code format
    """
    # Escape in order: backslash first, then other special chars
    text = text.replace("\\", "\\\\")
    text = text.replace(";", "\\;")
    text = text.replace(":", "\\:")
    text = text.replace(",", "\\,")
    return text


def generate_qr_code(network_name: str, password: str) -> etree.Element:
    """Generate WiFi QR code as SVG group element.

    Args:
        network_name: WiFi SSID
        password: WiFi password

    Returns:
        lxml Element containing QR code as a group with paths
    """
    # Escape special characters
    escaped_ssid = escape_wifi_string(network_name)
    escaped_password = escape_wifi_string(password)

    # Build WiFi QR code string (works on iOS and Android)
    wifi_string = f"WIFI:T:WPA;S:{escaped_ssid};P:{escaped_password};;"

    # Generate QR code with high error correction
    qr = segno.make(wifi_string, error='h')

    # Generate SVG output with smaller scale for more compact QR code
    buffer = BytesIO()
    qr.save(buffer, kind='svg', scale=2, border=0, xmldecl=False, svgns=False)
    buffer.seek(0)

    # Parse the generated SVG
    qr_svg = etree.parse(buffer)
    qr_root = qr_svg.getroot()

    # Create a group element for the QR code
    qr_group = etree.Element('g')
    qr_group.set('id', 'qr-code')

    # Calculate positioning (centered horizontally at bottom of card)
    # Card width with 0.20 inch side margins: 123.43 units
    # QR width with scale=2: 66 units
    # Center x position: (123.43 - 66) / 2 = 28.72
    # Position at y=180 (below password field which is at y~154, giving ~26 units gap)
    qr_x = 28.72
    qr_y = 180

    # Extract paths from QR SVG and add to group
    # Note: segno generates paths without namespace when svgns=False
    for path in qr_root.findall('.//path'):
        # Clone the path element with its attributes
        new_path = etree.Element('path')

        # Copy the path data
        if path.get('d'):
            new_path.set('d', path.get('d'))

        # Copy transform if present
        if path.get('transform'):
            new_path.set('transform', path.get('transform'))

        # Set stroke (segno uses stroke, not fill)
        new_path.set('stroke', '#000000')
        new_path.set('fill', 'none')

        # Copy stroke width if present, otherwise set default
        stroke_width = path.get('stroke-width')
        if stroke_width:
            new_path.set('stroke-width', stroke_width)

        qr_group.append(new_path)

    # Add transform for positioning
    qr_group.set('transform', f'translate({qr_x}, {qr_y})')

    return qr_group


def add_instruction_text(root) -> None:
    """Add instructional text below the QR code.

    Args:
        root: The SVG root element
    """
    # Card dimensions with 0.20 inch side margins
    # Original width: 111.95, side margins: 5.74 each, new width: 123.43
    card_width = 123.43

    # Create text element for instructions
    text_element = etree.Element('text')
    text_element.set('id', 'qr-instructions')
    text_element.set('x', '61.72')  # Center horizontally (123.43 / 2)
    text_element.set('y', '250.31')  # 0.15 inch (4.31 units) below QR code (ends at 246)
    text_element.set('text-anchor', 'middle')  # Center alignment
    text_element.set('font-family', 'Arial, sans-serif')
    text_element.set('font-size', '7')
    text_element.set('fill', '#000000')  # Black text

    # Create tspan for the instructional text
    tspan = etree.Element('tspan')
    tspan.set('x', '61.72')
    tspan.set('dy', '0')
    tspan.text = 'To quickly join this network, scan the QR code'
    text_element.append(tspan)

    # Create second line
    tspan2 = etree.Element('tspan')
    tspan2.set('x', '61.72')
    tspan2.set('dy', '9')  # Line spacing
    tspan2.text = 'with your iOS or Android device'
    text_element.append(tspan2)

    root.append(text_element)


def update_text_element(root, text_element_id: str, new_text: str) -> None:
    text_element = root.find(f".//svg:text[@id='{text_element_id}']", namespaces=SVG_NS)
    if text_element is None:
        print(f"Text element with id '{text_element_id}' not found.")
        return

    # Check if there's a tspan child element
    tspan = text_element.find("svg:tspan", namespaces=SVG_NS)

    if tspan is not None:
        # Update the tspan's text content to preserve its styling
        # (Important: tspan contains fill-opacity:1 and proper stroke color)
        tspan.text = new_text
        # Clear any direct text on the parent element
        text_element.text = ""

        # Set stroke:none to prevent letter bunching while keeping black fill
        # (stroke adds extra thickness that can make characters overlap)
        style = tspan.get('style', '')
        if style:
            # Remove stroke-related properties and add stroke:none
            style_parts = [s.strip() for s in style.split(';')]
            filtered_style = []
            for part in style_parts:
                if part and not any(part.startswith(x) for x in ['stroke:', 'stroke-width', 'stroke-opacity', 'stroke-dash', '-inkscape-stroke']):
                    filtered_style.append(part)
            # Explicitly set stroke to none
            filtered_style.append('stroke:none')
            tspan.set('style', ';'.join(filtered_style))
    else:
        # Fallback: if no tspan exists, set text directly on parent
        text_element.text = ""
        for child in list(text_element):
            text_element.remove(child)
        text_element.text = new_text

    print(f"Updated text element with id '{text_element_id}' to '{new_text}'.")


def generate_card(network_name: str, network_wifi_password: str, file_name: str) -> str:
    """Generate a WiFi card SVG file.

    Returns:
        The path to the generated SVG file
    """
    # Ensure output goes to output/ directory
    file_name = ensure_output_path(file_name)

    tree = etree.parse(TEMPLATE_FILE)
    root = tree.getroot()

    update_text_element(root, "WifiNetworkNameValue", network_name)
    update_text_element(root, "WifiNetworkPasswordValue", network_wifi_password)

    # Extend viewBox to accommodate QR code with margins
    viewBox = root.get('viewBox')
    if viewBox:
        parts = viewBox.split()
        if len(parts) == 4:
            # Add 0.20 inch (5.74 units) side margins on each side
            # Original width: 111.95, new width: 123.43
            parts[2] = '123.43'

            # Change height to accommodate QR code and instructions with margins
            # Password field at y~154, QR at y=180, QR ends at 246
            # Instructions at y=250.31, end at ~267
            # 2 inches bottom margin ≈ 57.4 units
            # New height: 267 + 57.4 ≈ 325
            parts[3] = '325'
            root.set('viewBox', ' '.join(parts))

    # Generate and insert QR code
    qr_group = generate_qr_code(network_name, network_wifi_password)
    root.append(qr_group)
    print(f"Generated WiFi QR code")

    # Add instructional text below QR code
    add_instruction_text(root)

    tree.write(file_name, pretty_print=True, xml_declaration=True, encoding="utf-8")
    print(f"Generated SVG card: {file_name}")
    return file_name


def convert_to_pdf(svg_file_path: str) -> str:
    """Convert an SVG file to PDF.

    Returns:
        The path to the generated PDF file
    """
    # Ensure output goes to output/ directory
    svg_file_path = ensure_output_path(svg_file_path)

    if not os.path.exists(svg_file_path):
        raise FileNotFoundError(f"SVG file '{svg_file_path}' not found.")

    pdf_file_path = os.path.splitext(svg_file_path)[0] + ".pdf"

    try:
        cairosvg.svg2pdf(url=svg_file_path, write_to=pdf_file_path)
        print(f"Generated PDF card: {pdf_file_path}")
        return pdf_file_path
    except Exception as e:
        raise RuntimeError(f"Failed to convert to PDF: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate WiFi network cards as SVG and optionally convert to PDF"
    )
    parser.add_argument("-n", "--name", help="WiFi network name")
    parser.add_argument("-p", "--password", help="WiFi network password")
    parser.add_argument("-o", "--output", help="Output file name (without extension)")
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Also generate a PDF version"
    )
    parser.add_argument(
        "--pdf-only",
        action="store_true",
        help="Only generate PDF (requires existing SVG file specified with -o)"
    )

    args = parser.parse_args()

    # PDF-only mode: convert existing SVG to PDF
    if args.pdf_only:
        if not args.output:
            print("Error: --pdf-only requires -o/--output to specify the SVG file")
            sys.exit(1)

        svg_path = args.output if args.output.endswith('.svg') else args.output + '.svg'
        try:
            convert_to_pdf(svg_path)
        except (FileNotFoundError, RuntimeError) as e:
            print(f"Error: {e}")
            sys.exit(1)
        return

    # Interactive mode if arguments not provided
    if not args.name or not args.password or not args.output:
        print("=== WiFi Card Generator ===")
        network_name = args.name or input("Enter network name: ")
        network_wifi_password = args.password or input("Enter network password: ")
        output_base = args.output or input("Enter output file name (without extension): ")
        generate_pdf = args.pdf or input("Generate PDF? (y/n): ").lower().startswith('y')
    else:
        network_name = args.name
        network_wifi_password = args.password
        output_base = args.output
        generate_pdf = args.pdf

    # Ensure output has .svg extension
    svg_file = output_base if output_base.endswith('.svg') else output_base + '.svg'

    # Generate the SVG card
    try:
        generate_card(network_name, network_wifi_password, svg_file)

        # Optionally convert to PDF
        if generate_pdf:
            convert_to_pdf(svg_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
