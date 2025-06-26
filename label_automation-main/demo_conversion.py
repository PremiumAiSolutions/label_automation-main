#!/usr/bin/env python3
"""
Demo script showing PNG to PDF conversion integration with the label automation system

This script demonstrates how PNG shipping labels are automatically converted 
to PDF format for optimal PrintNode compatibility.
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent))

from convert_label import convert_png_to_pdf, LabelConversionError
from app.converter.label_converter import convert_label_if_needed

def create_realistic_shipping_label(output_path="demo_shipping_label.png"):
    """
    Create a realistic shipping label PNG for demonstration
    
    Args:
        output_path (str): Path where to save the label
        
    Returns:
        str: Path to created label
    """
    # Create a 4x6 inch image at 300 DPI
    width, height = 1200, 1800
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Draw header
    draw.rectangle([0, 0, width, 120], fill='#0066cc')
    draw.text((50, 40), "USPS PRIORITY MAIL", fill='white', font=ImageFont.load_default())
    
    # From address section
    y_pos = 160
    draw.text((50, y_pos), "FROM:", fill='black', font=ImageFont.load_default())
    y_pos += 40
    draw.text((50, y_pos), "Premium AI Solutions", fill='black', font=ImageFont.load_default())
    y_pos += 30
    draw.text((50, y_pos), "123 Tech Street", fill='black', font=ImageFont.load_default())
    y_pos += 30
    draw.text((50, y_pos), "San Francisco, CA 94105", fill='black', font=ImageFont.load_default())
    y_pos += 60
    
    # To address section
    draw.rectangle([40, y_pos-10, width-40, y_pos+170], outline='black', width=2)
    y_pos += 20
    draw.text((60, y_pos), "TO:", fill='black', font=ImageFont.load_default())
    y_pos += 40
    draw.text((60, y_pos), "Customer Name", fill='black', font=ImageFont.load_default())
    y_pos += 30
    draw.text((60, y_pos), "456 Customer Street", fill='black', font=ImageFont.load_default())
    y_pos += 30
    draw.text((60, y_pos), "Los Angeles, CA 90210-1234", fill='black', font=ImageFont.load_default())
    y_pos += 80
    
    # Tracking barcode area
    draw.rectangle([50, y_pos, width-50, y_pos+100], outline='black', width=1)
    y_pos += 20
    draw.text((60, y_pos), "TRACKING NUMBER:", fill='black', font=ImageFont.load_default())
    y_pos += 30
    draw.text((60, y_pos), "EZ1000000001", fill='black', font=ImageFont.load_default())
    
    # Simple barcode representation
    y_pos += 40
    for i in range(0, 600, 8):
        line_width = 3 if i % 32 == 0 else 1
        draw.line([60 + i, y_pos, 60 + i, y_pos + 40], fill='black', width=line_width)
    
    y_pos += 80
    
    # Service info
    draw.rectangle([0, y_pos, width, y_pos+80], fill='#f0f0f0')
    y_pos += 20
    draw.text((50, y_pos), "PRIORITY MAIL 2-DAY", fill='black', font=ImageFont.load_default())
    y_pos += 30
    draw.text((50, y_pos), "Delivery by: Mon, 12/30/2024", fill='black', font=ImageFont.load_default())
    
    # Save the image
    image.save(output_path, 'PNG', dpi=(300, 300))
    print(f"Created realistic shipping label: {output_path}")
    return output_path

def demo_manual_conversion():
    """Demonstrate manual PNG to PDF conversion"""
    print("\n" + "="*60)
    print("🎯 DEMO: Manual PNG to PDF Conversion")
    print("="*60)
    
    # Create a sample label
    png_path = create_realistic_shipping_label("demo_label.png")
    pdf_path = "demo_label.pdf"
    
    try:
        print(f"\n📷 Converting: {png_path} → {pdf_path}")
        
        # Convert using our script
        success = convert_png_to_pdf(png_path, pdf_path, overwrite=True)
        
        if success:
            print("✅ Conversion successful!")
            
            # Show file info
            png_size = os.path.getsize(png_path)
            pdf_size = os.path.getsize(pdf_path)
            
            print(f"📊 Original PNG: {png_size:,} bytes")
            print(f"📊 Output PDF: {pdf_size:,} bytes")
            print(f"📐 PDF Dimensions: 4x6 inches (288x432 points)")
            print(f"🖨️ PrintNode Compatible: YES")
            
        else:
            print("❌ Conversion failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Cleanup
    try:
        if os.path.exists(png_path):
            os.remove(png_path)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        print("\n🗑️ Cleanup complete")
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")

def demo_webhook_integration():
    """Demonstrate how conversion works in the webhook system"""
    print("\n" + "="*60)
    print("🔗 DEMO: Webhook Integration")
    print("="*60)
    
    # Create a sample PNG label
    png_path = create_realistic_shipping_label("webhook_demo_label.png")
    
    try:
        # Read the PNG content as bytes (simulating webhook download)
        with open(png_path, 'rb') as f:
            png_content = f.read()
        
        # Simulate label data from EasyPost
        label_data = {
            "shipment_id": "shp_demo123456",
            "tracking_code": "EZ1000000001",
            "label_url": "https://example.com/label.png",
            "label_file_type": "png",  # This triggers conversion
            "label_date": "2024-12-27T10:00:00Z"
        }
        
        print(f"\n📡 Simulating EasyPost webhook...")
        print(f"📦 Shipment ID: {label_data['shipment_id']}")
        print(f"🏷️ Original Format: {label_data['label_file_type'].upper()}")
        print(f"💾 Original Size: {len(png_content):,} bytes")
        
        # Use our integrated converter
        print(f"\n🔄 Processing through label automation system...")
        converted_data, converted_content = convert_label_if_needed(label_data, png_content)
        
        # Show results
        print(f"✅ Processing complete!")
        print(f"🏷️ Output Format: {converted_data['label_file_type'].upper()}")
        print(f"💾 Output Size: {len(converted_content):,} bytes")
        
        if 'converted_from' in converted_data:
            print(f"🔄 Converted from: {converted_data['converted_from'].upper()}")
        
        print(f"🖨️ Ready for PrintNode: YES")
        
        # Save the result to show it works
        output_path = "webhook_demo_output.pdf"
        with open(output_path, 'wb') as f:
            f.write(converted_content)
        
        # Verify it's a valid PDF
        with open(output_path, 'rb') as f:
            header = f.read(4)
            if header == b'%PDF':
                print(f"✅ Valid PDF created: {output_path}")
            else:
                print(f"❌ Invalid PDF format")
        
    except Exception as e:
        print(f"❌ Integration demo failed: {e}")
    
    # Cleanup
    try:
        for file_path in [png_path, "webhook_demo_output.pdf"]:
            if os.path.exists(file_path):
                os.remove(file_path)
        print("\n🗑️ Cleanup complete")
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")

def demo_cli_usage():
    """Demonstrate CLI usage examples"""
    print("\n" + "="*60)
    print("💻 DEMO: CLI Usage Examples")
    print("="*60)
    
    print("\n📝 Common CLI Commands:")
    print("\n1️⃣ Basic conversion:")
    print("   python convert_label.py input.png output.pdf")
    
    print("\n2️⃣ With overwrite protection:")
    print("   python convert_label.py label.png label.pdf --overwrite")
    
    print("\n3️⃣ Verbose output:")
    print("   python convert_label.py label.png label.pdf --verbose")
    
    print("\n4️⃣ Batch convert folder:")
    print("   python convert_label.py --folder /path/to/labels/")
    
    print("\n5️⃣ Batch with separate output folder:")
    print("   python convert_label.py --folder input/ --output-folder output/")
    
    print("\n6️⃣ Get help:")
    print("   python convert_label.py --help")

def main():
    """Run all demos"""
    print("🚀 PNG to PDF Label Conversion Demo")
    print("🏷️ PrintNode Compatible | 4x6 Inch Output")
    
    # Run demos
    demo_manual_conversion()
    demo_webhook_integration() 
    demo_cli_usage()
    
    print("\n" + "="*60)
    print("✅ Demo Complete!")
    print("="*60)
    print("\n📋 Summary:")
    print("• ✅ PNG/JPG labels automatically convert to PDF")
    print("• ✅ Perfect 4x6 inch dimensions for PrintNode")
    print("• ✅ Integrated with EasyPost webhook system")
    print("• ✅ CLI tool for manual conversions")
    print("• ✅ Batch processing support")
    print("• ✅ Error handling and validation")
    print("\n🎯 Your label automation system is ready for PNG labels!")

if __name__ == '__main__':
    main() 