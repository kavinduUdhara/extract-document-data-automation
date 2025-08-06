#!/usr/bin/env python3
"""
Windows Permission Fix for Landing AI
This script addresses the temporary file permission issues on Windows
"""

import os
import tempfile
import stat
from pathlib import Path


def fix_windows_temp_permissions():
    """Fix Windows temporary directory permissions"""
    try:
        # Get the temporary directory
        temp_dir = Path(tempfile.gettempdir())
        
        # Create our extraction directory with proper permissions
        extraction_temp = temp_dir / "pdf_extraction_safe"
        extraction_temp.mkdir(exist_ok=True)
        
        # Set permissions to allow full access
        extraction_temp.chmod(stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        
        print(f"✅ Created safe extraction directory: {extraction_temp}")
        return extraction_temp
        
    except Exception as e:
        print(f"❌ Failed to fix permissions: {str(e)}")
        return None


def create_pdf_processing_wrapper():
    """Create a wrapper function for safe PDF processing"""
    script_content = '''
import os
import tempfile
import shutil
from pathlib import Path

def safe_pdf_extract(pdf_path, extraction_function):
    """
    Safely extract PDF content by handling Windows permission issues
    """
    # Create a safe temporary directory
    safe_temp = Path(os.environ.get('TEMP', tempfile.gettempdir())) / "pdf_safe_extraction"
    safe_temp.mkdir(exist_ok=True)
    
    try:
        # Copy PDF to safe location with new name
        safe_pdf = safe_temp / f"processing_{os.getpid()}.pdf"
        shutil.copy2(pdf_path, safe_pdf)
        
        # Ensure file permissions
        safe_pdf.chmod(0o666)
        
        # Run extraction
        result = extraction_function(safe_pdf)
        
        return result
        
    except Exception as e:
        print(f"Extraction error: {e}")
        return None
        
    finally:
        # Clean up
        try:
            if safe_pdf.exists():
                safe_pdf.unlink()
        except:
            pass
    '''
    
    wrapper_file = Path("pdf_processing_wrapper.py")
    with open(wrapper_file, 'w') as f:
        f.write(script_content)
    
    print(f"✅ Created PDF processing wrapper: {wrapper_file}")


def main():
    """Main function to set up Windows fixes"""
    print("🔧 Setting up Windows Permission Fixes...")
    print("=" * 50)
    
    # Fix temp directory permissions
    temp_dir = fix_windows_temp_permissions()
    
    # Create processing wrapper
    create_pdf_processing_wrapper()
    
    print("=" * 50)
    print("✅ Windows fixes applied!")
    print("📝 Recommendation: Use production_extractor.py for best results")
    print("🎯 The production extractor handles permission issues automatically")


if __name__ == "__main__":
    main()
