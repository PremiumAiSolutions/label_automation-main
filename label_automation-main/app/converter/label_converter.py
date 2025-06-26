import logging
import tempfile
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from convert_label.py
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from convert_label import convert_png_to_pdf, LabelConversionError
    CONVERSION_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("PNG to PDF conversion module loaded successfully")
except ImportError as e:
    CONVERSION_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"PNG to PDF conversion not available: {e}")

def convert_label_if_needed(label_data, label_content):
    """
    Convert label format if needed (e.g., PNG to PDF for PrintNode compatibility)
    
    Args:
        label_data (dict): Label metadata from EasyPost
        label_content (bytes): Raw label file content
        
    Returns:
        tuple: (converted_label_data, converted_content) ready for PrintNode
    """
    logger.info("Checking if label conversion is needed")
    
    try:
        file_type = label_data.get('label_file_type', '').lower()
        logger.info(f"Original label format: {file_type}")
        
        # If it's already ZPL or EPL, no conversion needed
        if file_type in ['zpl', 'epl']:
            logger.info(f"Label is already in {file_type.upper()} format, no conversion needed")
            return label_data, label_content
        
        # For PNG files, convert to PDF for better PrintNode compatibility
        if file_type == 'png' and CONVERSION_AVAILABLE:
            logger.info("PNG label detected - converting to PDF for PrintNode")
            
            # Save PNG to temporary file
            png_temp_path = save_label_to_temp_file(label_content, 'png')
            if not png_temp_path:
                logger.error("Failed to save PNG to temporary file")
                return label_data, label_content
            
            try:
                # Create PDF output path
                pdf_temp_path = png_temp_path.replace('.png', '.pdf')
                
                # Convert PNG to PDF
                convert_png_to_pdf(png_temp_path, pdf_temp_path, overwrite=True)
                
                # Read the converted PDF content
                with open(pdf_temp_path, 'rb') as pdf_file:
                    converted_content = pdf_file.read()
                
                # Update label data to reflect PDF format
                converted_label_data = label_data.copy()
                converted_label_data['label_file_type'] = 'pdf'
                converted_label_data['converted_from'] = 'png'
                
                logger.info(f"Successfully converted PNG to PDF ({len(converted_content)} bytes)")
                
                # Clean up temporary files
                cleanup_temp_file(png_temp_path)
                cleanup_temp_file(pdf_temp_path)
                
                return converted_label_data, converted_content
                
            except LabelConversionError as e:
                logger.error(f"PNG to PDF conversion failed: {e}")
                cleanup_temp_file(png_temp_path)
                # Fall back to original content
                return label_data, label_content
            except Exception as e:
                logger.exception(f"Unexpected error during PNG conversion: {e}")
                cleanup_temp_file(png_temp_path)
                # Fall back to original content
                return label_data, label_content
        
        # For PDF files, check if they need any processing
        elif file_type == 'pdf':
            logger.info("PDF label detected - checking if conversion needed")
            
            # For now, just return as-is, but we could add PDF validation here
            # or ensure proper 4x6 dimensions using our conversion script
            return label_data, label_content
        
        # For JPG/JPEG files, convert to PDF if available
        elif file_type in ['jpg', 'jpeg'] and CONVERSION_AVAILABLE:
            logger.info(f"{file_type.upper()} label detected - converting to PDF for PrintNode")
            
            # Save image to temporary file
            img_temp_path = save_label_to_temp_file(label_content, file_type)
            if not img_temp_path:
                logger.error(f"Failed to save {file_type.upper()} to temporary file")
                return label_data, label_content
            
            try:
                # Create PDF output path
                pdf_temp_path = img_temp_path.replace(f'.{file_type}', '.pdf')
                
                # Convert image to PDF
                convert_png_to_pdf(img_temp_path, pdf_temp_path, overwrite=True)
                
                # Read the converted PDF content
                with open(pdf_temp_path, 'rb') as pdf_file:
                    converted_content = pdf_file.read()
                
                # Update label data to reflect PDF format
                converted_label_data = label_data.copy()
                converted_label_data['label_file_type'] = 'pdf'
                converted_label_data['converted_from'] = file_type
                
                logger.info(f"Successfully converted {file_type.upper()} to PDF ({len(converted_content)} bytes)")
                
                # Clean up temporary files
                cleanup_temp_file(img_temp_path)
                cleanup_temp_file(pdf_temp_path)
                
                return converted_label_data, converted_content
                
            except LabelConversionError as e:
                logger.error(f"{file_type.upper()} to PDF conversion failed: {e}")
                cleanup_temp_file(img_temp_path)
                # Fall back to original content
                return label_data, label_content
            except Exception as e:
                logger.exception(f"Unexpected error during {file_type.upper()} conversion: {e}")
                cleanup_temp_file(img_temp_path)
                # Fall back to original content
                return label_data, label_content
        
        # For other formats, log and return as-is
        else:
            if file_type in ['png', 'jpg', 'jpeg'] and not CONVERSION_AVAILABLE:
                logger.warning(f"Image format {file_type} detected but conversion module not available")
            logger.info(f"Label format {file_type} - no conversion implemented or needed")
            return label_data, label_content
        
    except Exception as e:
        logger.exception(f"Error during label conversion: {str(e)}")
        # Return original data if conversion fails
        return label_data, label_content

def save_label_to_temp_file(label_content, file_extension='pdf'):
    """
    Save label content to a temporary file
    
    Args:
        label_content (bytes): Label file content
        file_extension (str): File extension (without dot)
        
    Returns:
        str: Path to temporary file, or None if failed
    """
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            suffix=f'.{file_extension}', 
            delete=False
        ) as temp_file:
            temp_file.write(label_content)
            temp_path = temp_file.name
        
        logger.info(f"Saved label to temporary file: {temp_path}")
        return temp_path
        
    except Exception as e:
        logger.exception(f"Error saving label to temp file: {str(e)}")
        return None

def cleanup_temp_file(file_path):
    """
    Clean up temporary file
    
    Args:
        file_path (str): Path to file to delete
    """
    try:
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
            logger.info(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup temp file {file_path}: {str(e)}")