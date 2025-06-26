#!/usr/bin/env python3
"""
PNG to PDF Label Converter for PrintNode Compatibility

This script converts shipping label images (PNG/JPG) into valid 4x6 inch PDF files
that are fully compatible with PrintNode printing services.

Usage:
    CLI: python convert_label.py input.png output.pdf
    Import: from convert_label import convert_png_to_pdf
"""

import sys
import os
import argparse
from pathlib import Path
from PIL import Image, ImageOps
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# PDF dimensions for 4x6 inch label (in points: 1 inch = 72 points)
LABEL_WIDTH = 4 * 72  # 288 points
LABEL_HEIGHT = 6 * 72  # 432 points
LABEL_SIZE = (LABEL_WIDTH, LABEL_HEIGHT)

# Supported image formats
SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg'}

class LabelConversionError(Exception):
    """Custom exception for label conversion errors"""
    pass

def validate_input_file(input_path):
    """
    Validate the input file exists and is a supported format.
    
    Args:
        input_path (str): Path to input image file
        
    Returns:
        Path: Validated Path object
        
    Raises:
        LabelConversionError: If file doesn't exist or unsupported format
    """
    input_path = Path(input_path)
    
    # Check if file exists
    if not input_path.exists():
        raise LabelConversionError(f"Input file does not exist: {input_path}")
    
    # Check if file is readable
    if not input_path.is_file():
        raise LabelConversionError(f"Input path is not a file: {input_path}")
    
    # Check file extension
    if input_path.suffix.lower() not in SUPPORTED_FORMATS:
        raise LabelConversionError(
            f"Unsupported file format: {input_path.suffix}. "
            f"Supported formats: {', '.join(SUPPORTED_FORMATS)}"
        )
    
    return input_path

def load_and_validate_image(input_path):
    """
    Load and validate the image file.
    
    Args:
        input_path (Path): Path to input image file
        
    Returns:
        PIL.Image: Loaded and validated image
        
    Raises:
        LabelConversionError: If image cannot be loaded or processed
    """
    try:
        image = Image.open(input_path)
        
        # Convert to RGB if needed (removes transparency, handles CMYK, etc.)
        if image.mode not in ('RGB', 'L'):
            logger.info(f"Converting image from {image.mode} to RGB mode")
            image = image.convert('RGB')
        
        # Log image information
        logger.info(f"Loaded image: {image.size[0]}x{image.size[1]} pixels, mode: {image.mode}")
        
        # Check if image is already close to 4:6 ratio
        width, height = image.size
        current_ratio = width / height
        target_ratio = LABEL_WIDTH / LABEL_HEIGHT  # 4/6 = 0.667
        
        if abs(current_ratio - target_ratio) > 0.1:
            logger.warning(
                f"Image ratio ({current_ratio:.3f}) differs significantly from 4:6 ratio ({target_ratio:.3f}). "
                f"Image will be scaled with white padding to maintain aspect ratio."
            )
        
        return image
        
    except Exception as e:
        raise LabelConversionError(f"Failed to load image: {e}")

def scale_image_to_label_size(image):
    """
    Scale image to fit 4x6 label while maintaining aspect ratio.
    Adds white background if needed.
    
    Args:
        image (PIL.Image): Input image
        
    Returns:
        PIL.Image: Scaled image ready for PDF conversion
    """
    # Calculate the scaling factor to fit within label dimensions
    img_width, img_height = image.size
    scale_width = LABEL_WIDTH / img_width
    scale_height = LABEL_HEIGHT / img_height
    
    # Use the smaller scale factor to ensure image fits within bounds
    scale_factor = min(scale_width, scale_height)
    
    # Calculate new dimensions
    new_width = int(img_width * scale_factor)
    new_height = int(img_height * scale_factor)
    
    logger.info(f"Scaling image from {img_width}x{img_height} to {new_width}x{new_height}")
    
    # Resize the image with high-quality resampling
    scaled_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Create a white background of exact label size
    background = Image.new('RGB', (int(LABEL_WIDTH), int(LABEL_HEIGHT)), 'white')
    
    # Calculate position to center the scaled image
    x_offset = (int(LABEL_WIDTH) - new_width) // 2
    y_offset = (int(LABEL_HEIGHT) - new_height) // 2
    
    # Paste the scaled image onto the white background
    background.paste(scaled_image, (x_offset, y_offset))
    
    logger.info(f"Created final image: {background.size[0]}x{background.size[1]} pixels")
    
    return background

def create_pdf_from_image(image, output_path):
    """
    Create a PDF file from the processed image.
    
    Args:
        image (PIL.Image): Processed image ready for PDF
        output_path (Path): Output PDF file path
        
    Raises:
        LabelConversionError: If PDF creation fails
    """
    try:
        # Create the PDF canvas with exact 4x6 inch dimensions
        c = canvas.Canvas(str(output_path), pagesize=LABEL_SIZE)
        
        # Save image to a temporary format that reportlab can use
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_path = temp_file.name
            image.save(temp_path, 'PNG', dpi=(300, 300))
        
        try:
            # Draw the image on the PDF canvas at exact dimensions
            c.drawImage(
                temp_path,
                0, 0,  # Position at bottom-left corner
                width=LABEL_WIDTH,
                height=LABEL_HEIGHT,
                preserveAspectRatio=False  # We already handled aspect ratio
            )
            
            # Save the PDF
            c.save()
            logger.info(f"Successfully created PDF: {output_path}")
            
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
            
    except Exception as e:
        raise LabelConversionError(f"Failed to create PDF: {e}")

def convert_png_to_pdf(input_path, output_path, overwrite=False):
    """
    Convert a PNG/JPG image to a 4x6 inch PDF suitable for PrintNode.
    
    Args:
        input_path (str): Path to input image file
        output_path (str): Path for output PDF file
        overwrite (bool): Whether to overwrite existing output files
        
    Returns:
        bool: True if conversion successful
        
    Raises:
        LabelConversionError: If conversion fails at any step
    """
    # Validate input
    input_path = validate_input_file(input_path)
    output_path = Path(output_path)
    
    # Check if output file already exists
    if output_path.exists() and not overwrite:
        raise LabelConversionError(
            f"Output file already exists: {output_path}. Use --overwrite flag to replace it."
        )
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Converting {input_path} -> {output_path}")
    
    # Load and process the image
    image = load_and_validate_image(input_path)
    
    # Scale image to proper label size
    processed_image = scale_image_to_label_size(image)
    
    # Create the PDF
    create_pdf_from_image(processed_image, output_path)
    
    # Verify the output file was created
    if not output_path.exists():
        raise LabelConversionError("PDF file was not created successfully")
    
    file_size = output_path.stat().st_size
    logger.info(f"Conversion complete! Output file size: {file_size:,} bytes")
    
    return True

def convert_folder(input_folder, output_folder=None, overwrite=False):
    """
    Convert all supported image files in a folder to PDFs.
    
    Args:
        input_folder (str): Path to folder containing images
        output_folder (str): Path to output folder (defaults to input_folder)
        overwrite (bool): Whether to overwrite existing files
        
    Returns:
        list: List of successfully converted files
    """
    input_folder = Path(input_folder)
    if output_folder is None:
        output_folder = input_folder
    else:
        output_folder = Path(output_folder)
    
    if not input_folder.exists():
        raise LabelConversionError(f"Input folder does not exist: {input_folder}")
    
    # Find all supported image files
    image_files = []
    for ext in SUPPORTED_FORMATS:
        image_files.extend(input_folder.glob(f"*{ext}"))
        image_files.extend(input_folder.glob(f"*{ext.upper()}"))
    
    if not image_files:
        logger.warning(f"No supported image files found in {input_folder}")
        return []
    
    logger.info(f"Found {len(image_files)} image files to convert")
    
    converted_files = []
    failed_files = []
    
    for image_file in image_files:
        try:
            # Create output path with .pdf extension
            output_file = output_folder / f"{image_file.stem}.pdf"
            
            convert_png_to_pdf(image_file, output_file, overwrite=overwrite)
            converted_files.append(str(output_file))
            
        except Exception as e:
            logger.error(f"Failed to convert {image_file}: {e}")
            failed_files.append(str(image_file))
    
    logger.info(f"Conversion complete: {len(converted_files)} successful, {len(failed_files)} failed")
    
    if failed_files:
        logger.warning(f"Failed files: {', '.join(failed_files)}")
    
    return converted_files

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Convert shipping label images to 4x6 inch PDFs compatible with PrintNode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python convert_label.py label.png label.pdf
    python convert_label.py /path/to/label.jpg /path/to/output.pdf --overwrite
    python convert_label.py --folder /path/to/labels/
    python convert_label.py --folder /path/to/input/ --output-folder /path/to/output/
        """
    )
    
    # Input/output arguments
    parser.add_argument('input', nargs='?', help='Input image file path')
    parser.add_argument('output', nargs='?', help='Output PDF file path')
    
    # Folder processing
    parser.add_argument('--folder', help='Convert all images in a folder')
    parser.add_argument('--output-folder', help='Output folder for batch conversion')
    
    # Options
    parser.add_argument('--overwrite', action='store_true', 
                       help='Overwrite existing output files')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Suppress all output except errors')
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        if args.folder:
            # Folder mode
            convert_folder(args.folder, args.output_folder, args.overwrite)
        else:
            # Single file mode
            if not args.input or not args.output:
                parser.error("Input and output paths are required for single file conversion")
            
            convert_png_to_pdf(args.input, args.output, args.overwrite)
            
        return 0
        
    except LabelConversionError as e:
        logger.error(f"Conversion failed: {e}")
        return 1
    except KeyboardInterrupt:
        logger.info("Conversion cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 