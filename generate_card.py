import sys
import os
import argparse
from pathlib import Path
from lxml import etree
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF

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


def update_text_element(root, text_element_id: str, new_text: str) -> None:
    text_element = root.find(f".//svg:text[@id='{text_element_id}']", namespaces=SVG_NS)
    if text_element is None:
        print(f"Text element with id '{text_element_id}' not found.")
        return
    else:
        # 1. Clear any text sitting directly in the parent <text> tag
        text_element.text = ""

        # 2. Iterate over a COPY of the children list and remove them
        # (We use list() to create a copy so we don't break the iterator while deleting)
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
        drawing = svg2rlg(svg_file_path)
        renderPDF.drawToFile(drawing, pdf_file_path)
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
