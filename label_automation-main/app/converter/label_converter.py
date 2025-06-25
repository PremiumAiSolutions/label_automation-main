import logging
import tempfile
import os

logger = logging.getLogger(__name__)

def convert_label_if_needed(label_data, label_content):
    """
    Convert label format if needed (e.g., PDF to ZPL)
    
    Args:
        label_data (dict): Label metadata from EasyPost
        label_content (bytes): Raw label file content
        
    Returns:
        tuple: (converted_label_data, converted_content) ready for PrintNode
    """
    logger.info("Checking if label conversion is needed")
    
    try:
        file_type = label_data.get('label_file_type', '').lower()
        
        # If it's already ZPL or EPL, no conversion needed
        if file_type in ['zpl', 'epl']:
            logger.info(f"Label is already in {file_type.upper()} format, no conversion needed")
            return label_data, label_content
        
        # For PDF files, we may want to convert to ZPL for thermal printers
        # This is a placeholder for actual conversion logic
        if file_type == 'pdf':
            logger.info("PDF label detected - keeping as PDF for now")
            # In a real implementation, you might use a service like:
            # - Labelary API for PDF to ZPL conversion
            # - Local conversion tools
            # - Printer-specific drivers
            
            # For now, return as-is
            return label_data, label_content
        
        # For other formats, log and return as-is
        logger.info(f"Label format {file_type} - no conversion implemented")
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