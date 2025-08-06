"""
Landing AI Agentic Document Extraction Setup and Configuration Guide
"""

import os
import json
from pathlib import Path

def create_landing_ai_account_info():
    """Display information about setting up Landing AI account."""
    print("=== Landing AI Account Setup ===\n")
    
    print("1. Go to Landing AI (https://landing.ai/)")
    print("2. Sign up for an account or log in")
    print("3. Navigate to your dashboard")
    print("4. Go to API section or account settings")
    print("5. Generate an API key for Vision Agent")
    print("6. Copy the API key and save it securely")
    print("7. Add the key to your .env file as VISION_AGENT_API_KEY\n")

def create_google_ai_setup_info():
    """Display information about optional Google AI Studio setup."""
    print("=== Google AI Studio Setup (Optional) ===\n")
    
    print("For enhanced AI processing, you can optionally add Google AI Studio:")
    print("1. Go to Google AI Studio (https://aistudio.google.com/)")
    print("2. Sign up or log in to your account")
    print("3. Navigate to API keys section")
    print("4. Create a new API key")
    print("5. Add the key to your .env file as GOOGLE_AI_STUDIO_API_KEY")
    print("6. This enables advanced CSV structuring with custom prompts\n")

def setup_environment():
    """Guide user through environment setup."""
    print("=== Environment Setup ===\n")
    
    # Check if .env file exists
    env_file = Path(".env")
    
    if not env_file.exists():
        print("Creating .env file from template...")
        
        # Copy from .env.example
        example_file = Path(".env.example")
        if example_file.exists():
            with open(example_file, 'r') as f:
                content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(content)
            
            print("✅ .env file created!")
            print("📝 Please edit the .env file with your actual API keys")
        else:
            print("❌ .env.example file not found")
    else:
        print("✅ .env file already exists")
    
    print("\nRequired environment variables:")
    print("- VISION_AGENT_API_KEY: Your Landing AI Vision Agent API key (REQUIRED)")
    print("- GOOGLE_AI_STUDIO_API_KEY: Your Google AI Studio API key (OPTIONAL - for enhanced processing)")
    print("- DOCUMENTS_FOLDER: Folder containing documents to process")
    print("- OUTPUT_CSV_FILE: Output CSV file name")
    print("- RESULTS_SAVE_DIR: Directory to save detailed extraction results")

def verify_setup():
    """Verify the setup is correct."""
    print("=== Setup Verification ===\n")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['VISION_AGENT_API_KEY']
    optional_vars = ['GOOGLE_AI_STUDIO_API_KEY']
    
    all_good = True
    
    # Check required variables
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: Not set (REQUIRED)")
            all_good = False
    
    # Check optional variables
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set (enables enhanced processing)")
        else:
            print(f"⚠️  {var}: Not set (optional)")
    
    # Test Landing AI access
    try:
        print("\n=== Testing Landing AI Access ===")
        from agentic_doc.parse import parse
        
        print("✅ Landing AI library imported successfully")
        
        # Create a test file to verify API access
        test_content = "This is a test document for API verification."
        test_file = Path("test_document.txt")
        
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        try:
            # Test with a simple text file
            result = parse(str(test_file))
            if result:
                print("✅ Landing AI API access successful")
            else:
                print("❌ Landing AI API test failed - no results returned")
                all_good = False
        except Exception as e:
            print(f"❌ Landing AI API test failed: {e}")
            all_good = False
        finally:
            # Clean up test file
            if test_file.exists():
                test_file.unlink()
        
    except ImportError as e:
        print(f"❌ Landing AI library import failed: {e}")
        print("💡 Run: pip install agentic-doc")
        all_good = False
    except Exception as e:
        print(f"❌ Landing AI access test failed: {e}")
        all_good = False
    
    # Test Google AI Studio if available
    google_ai_key = os.getenv('GOOGLE_AI_STUDIO_API_KEY')
    if google_ai_key:
        try:
            print("\n=== Testing Google AI Studio Access ===")
            import google.generativeai as genai
            
            genai.configure(api_key=google_ai_key)
            print("✅ Google AI Studio library available and configured")
            
        except ImportError:
            print("⚠️  Google AI Studio library not installed (pip install google-generativeai)")
        except Exception as e:
            print(f"⚠️  Google AI Studio setup issue: {e}")
    
    if all_good:
        print("\n🎉 Setup verification completed successfully!")
        print("You're ready to use the Document Data Extractor!")
    else:
        print("\n⚠️  Some issues found. Please fix them before proceeding.")

def create_sample_documents_folder():
    """Create a sample documents folder."""
    print("=== Creating Sample Documents Folder ===\n")
    
    documents_folder = Path("documents")
    documents_folder.mkdir(exist_ok=True)
    
    # Create a README in the documents folder
    readme_content = """# Documents Folder

Place your documents here for processing with Landing AI Agentic Document Extraction.

Supported file formats:
- PDF (.pdf)
- Images: JPEG (.jpg, .jpeg), PNG (.png), TIFF (.tiff, .tif), GIF (.gif), BMP (.bmp)
- Office documents: Word (.doc, .docx), Excel (.xls, .xlsx), PowerPoint (.ppt, .pptx)
- Text files (.txt)

Example documents you can test with:
- Invoices
- Receipts
- Business cards
- Forms
- Contracts
- Financial statements
- Any document with text or structured data

The extractor will process all supported files in this folder using Landing AI's
advanced document understanding capabilities.

Landing AI provides:
- Accurate text extraction
- Intelligent document understanding
- Structured data extraction
- Table and form recognition
- Entity extraction
"""
    
    with open(documents_folder / "README.md", 'w') as f:
        f.write(readme_content)
    
    print(f"✅ Created documents folder: {documents_folder}")
    print("📝 Add your document files to this folder for processing")

def display_features():
    """Display Landing AI features and benefits."""
    print("=== Landing AI Agentic Document Extraction Features ===\n")
    
    print("🤖 **AI-Powered Document Understanding**")
    print("   - Advanced document parsing and understanding")
    print("   - Intelligent text extraction from any document type")
    print("   - Automatic entity recognition and extraction")
    print("")
    
    print("📊 **Structured Data Extraction**")
    print("   - Tables, forms, and structured content extraction")
    print("   - JSON and Markdown output formats")
    print("   - Consistent data structuring across document types")
    print("")
    
    print("🔧 **Easy Integration**")
    print("   - Simple Python API")
    print("   - No complex cloud setup required")
    print("   - Pay-per-use pricing model")
    print("")
    
    print("📁 **Wide Format Support**")
    print("   - PDF, images, Office documents")
    print("   - Scanned documents and photos")
    print("   - Multi-page document processing")
    print("")

def main():
    """Main setup function."""
    print("Landing AI Document Data Extractor - Setup Guide")
    print("=" * 60)
    
    print("\nThis guide will help you set up the Document Data Extractor using Landing AI.\n")
    
    # Display features
    display_features()
    
    # Display setup information
    create_landing_ai_account_info()
    create_google_ai_setup_info()
    
    # Setup environment
    setup_environment()
    
    # Create documents folder
    create_sample_documents_folder()
    
    print("\n" + "=" * 60)
    print("Setup guide completed!")
    print("\nNext steps:")
    print("1. Get your Landing AI API key and add it to .env")
    print("2. (Optional) Get OpenAI API key for enhanced processing")
    print("3. Install dependencies: pip install -r requirements.txt")
    print("4. Add documents to the 'documents' folder")
    print("5. Run the verification: python setup.py --verify")
    print("6. Start extracting: python document_extractor.py")
    print("\nLanding AI Benefits:")
    print("✅ No complex cloud setup")
    print("✅ Superior document understanding")
    print("✅ Pay-per-use pricing")
    print("✅ Wide format support")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        verify_setup()
    else:
        main()
