#!/usr/bin/env python3
"""
Test script for PNG to PDF conversion functionality

This script tests the convert_label.py module with a sample image
to ensure it works correctly for PrintNode compatibility.
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent))

from convert_label import convert_png_to_pdf, LabelConversionError

def create_sample_label(output_path="test_label.png"):
    """
    Create a sample shipping label PNG for testing
    
    Args:
        output_path (str): Path where to save the sample label
        
    Returns:
        str: Path to created sample label
    """
    # Create a 4x6 inch image at 300 DPI (1200x1800 pixels)
    width, height = 1200, 1800
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Draw a border
    border_color = 'black'
    border_width = 10
    draw.rectangle([0, 0, width-1, height-1], outline=border_color, width=border_width)
    
    # Try to use a default font, fall back to basic if not available
    try:
        # Try to load a font (size 60 for title, 40 for text)
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    # Add sample shipping label content
    y_pos = 50
    
    # Title
    draw.text((50, y_pos), "SHIPPING LABEL", fill='black', font=title_font)
    y_pos += 100
    
    # From address
    draw.text((50, y_pos), "FROM:", fill='black', font=text_font)
    y_pos += 50
    draw.text((50, y_pos), "Premium AI Solutions", fill='black', font=text_font)
    y_pos += 40
    draw.text((50, y_pos), "123 Tech Street", fill='black', font=text_font)
    y_pos += 40
    draw.text((50, y_pos), "San Francisco, CA 94105", fill='black', font=text_font)
    y_pos += 80
    
    # To address
    draw.text((50, y_pos), "TO:", fill='black', font=text_font)
    y_pos += 50
    draw.text((50, y_pos), "Test Customer", fill='black', font=text_font)
    y_pos += 40
    draw.text((50, y_pos), "456 Customer Ave", fill='black', font=text_font)
    y_pos += 40
    draw.text((50, y_pos), "Los Angeles, CA 90210", fill='black', font=text_font)
    y_pos += 80
    
    # Tracking number
    draw.text((50, y_pos), "TRACKING: EZ1234567890", fill='black', font=title_font)
    y_pos += 100
    
    # Barcode placeholder (simple lines)
    for i in range(0, 500, 10):
        line_width = 2 if i % 20 == 0 else 1
        draw.line([50 + i, y_pos, 50 + i, y_pos + 80], fill='black', width=line_width)
    y_pos += 120
    
    # Service type
    draw.text((50, y_pos), "PRIORITY MAIL", fill='black', font=text_font)
    y_pos += 50
    draw.text((50, y_pos), "1-3 Business Days", fill='black', font=text_font)
    
    # Save the image
    image.save(output_path, 'PNG', dpi=(300, 300))
    print(f"Created sample label: {output_path} ({width}x{height} pixels)")
    return output_path

def test_conversion():
    """Test the PNG to PDF conversion functionality"""
    print("=" * 50)
    print("Testing PNG to PDF Conversion")
    print("=" * 50)
    
    # Create sample label
    sample_png = create_sample_label("test_label.png")
    
    # Test single file conversion
    output_pdf = "test_label.pdf"
    
    try:
        print(f"\nConverting {sample_png} -> {output_pdf}")
        success = convert_png_to_pdf(sample_png, output_pdf, overwrite=True)
        
        if success:
            print("✅ Conversion successful!")
            
            # Check output file
            if os.path.exists(output_pdf):
                file_size = os.path.getsize(output_pdf)
                print(f"✅ Output PDF created: {file_size:,} bytes")
                
                # Try to verify it's a valid PDF by reading first few bytes
                with open(output_pdf, 'rb') as f:
                    header = f.read(4)
                    if header == b'%PDF':
                        print("✅ Output file has valid PDF header")
                    else:
                        print("❌ Output file does not have valid PDF header")
            else:
                print("❌ Output PDF file was not created")
        else:
            print("❌ Conversion failed")
            
    except LabelConversionError as e:
        print(f"❌ Conversion error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    # Test CLI functionality
    print(f"\n" + "="*50)
    print("Testing CLI Functionality")
    print("="*50)
    
    # Create another sample for CLI test
    cli_sample = create_sample_label("cli_test_label.png")
    cli_output = "cli_test_output.pdf"
    
    # Test CLI command
    import subprocess
    try:
        print(f"\nTesting CLI: python convert_label.py {cli_sample} {cli_output}")
        result = subprocess.run([
            sys.executable, "convert_label.py", 
            cli_sample, cli_output, "--verbose"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ CLI conversion successful!")
            print("📄 CLI Output:")
            print(result.stdout)
            if result.stderr:
                print("⚠️ CLI Warnings:")
                print(result.stderr)
        else:
            print(f"❌ CLI conversion failed (exit code: {result.returncode})")
            print("📄 CLI Output:")
            print(result.stdout)
            print("❌ CLI Errors:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("❌ CLI test timed out")
    except Exception as e:
        print(f"❌ CLI test error: {e}")
    
    # Clean up test files
    print(f"\n" + "="*50)
    print("Cleaning Up Test Files")
    print("="*50)
    
    test_files = [sample_png, output_pdf, cli_sample, cli_output]
    for file_path in test_files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🗑️ Removed: {file_path}")
        except Exception as e:
            print(f"⚠️ Failed to remove {file_path}: {e}")
    
    print("\n" + "="*50)
    print("Test Complete!")
    print("="*50)

if __name__ == '__main__':
    test_conversion() 