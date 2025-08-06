#!/usr/bin/env python3
"""
Configuration validator for Document Data Extractor using Landing AI.
This script helps validate your Landing AI setup.
"""

import os
import sys
import json
from pathlib import Path

def check_python_version():
    """Check Python version compatibility."""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (Compatible)")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (Requires Python 3.8+)")
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        ('agentic_doc', 'agentic-doc'),
        ('pandas', 'pandas'),
        ('dotenv', 'python-dotenv')
    ]
    
    optional_packages = [
        ('google.generativeai', 'google-generativeai')
    ]
    
    all_required_installed = True
    
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            print(f"   ✅ {package_name}")
        except ImportError:
            print(f"   ❌ {package_name} (Required - Not installed)")
            all_required_installed = False
    
    for import_name, package_name in optional_packages:
        try:
            __import__(import_name)
            print(f"   ✅ {package_name} (Optional)")
        except ImportError:
            print(f"   ⚠️  {package_name} (Optional - Not installed)")
    
    if not all_required_installed:
        print(f"\n   💡 Install missing packages with: pip install -r requirements.txt")
    
    return all_required_installed

def check_env_file():
    """Check environment file configuration."""
    print("\n⚙️  Checking environment configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("   ❌ .env file not found")
        print("   💡 Copy .env.example to .env and fill in your values")
        return False
    
    print("   ✅ .env file exists")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("   ⚠️  Cannot load .env file (python-dotenv not installed)")
        return False
    
    # Check required variables
    required_vars = {
        'VISION_AGENT_API_KEY': 'Your Landing AI Vision Agent API key'
    }
    
    optional_vars = {
        'GOOGLE_AI_STUDIO_API_KEY': 'Your Google AI Studio API key (for enhanced processing)',
        'DOCUMENTS_FOLDER': 'Documents folder path',
        'OUTPUT_CSV_FILE': 'Output CSV file name',
        'RESULTS_SAVE_DIR': 'Results save directory'
    }
    
    missing_required = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and value != f'your-{var.lower().replace("_", "-")}':
            print(f"   ✅ {var}")
        else:
            print(f"   ❌ {var} (Required - {description})")
            missing_required.append(var)
    
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value and value != f'your-{var.lower().replace("_", "-")}':
            print(f"   ✅ {var}")
        else:
            print(f"   ⚠️  {var} (Optional - {description})")
    
    return len(missing_required) == 0

def check_landing_ai_access():
    """Test Landing AI API access."""
    print("\n🤖 Testing Landing AI API access...")
    
    api_key = os.getenv('VISION_AGENT_API_KEY')
    if not api_key:
        print("   ❌ VISION_AGENT_API_KEY not set")
        return False
    
    try:
        # Import Landing AI library
        from agentic_doc.parse import parse
        print("   ✅ Landing AI library imported successfully")
        
        # Create a simple test file
        test_content = "This is a test document for Landing AI API verification."
        test_file = Path("test_api_verification.txt")
        
        try:
            with open(test_file, 'w') as f:
                f.write(test_content)
            
            # Test API call with simple text file
            result = parse(str(test_file))
            
            if result and len(result) > 0:
                print("   ✅ Landing AI API call successful")
                
                # Check result structure
                first_result = result[0]
                if hasattr(first_result, 'markdown'):
                    print("   ✅ Markdown extraction available")
                if hasattr(first_result, 'chunks'):
                    print("   ✅ Structured chunks available")
                
                return True
            else:
                print("   ❌ Landing AI API call failed - no results returned")
                return False
                
        except Exception as api_error:
            print(f"   ❌ Landing AI API call failed: {api_error}")
            return False
        finally:
            # Clean up test file
            if test_file.exists():
                test_file.unlink()
        
    except ImportError as e:
        print(f"   ❌ Landing AI library not available: {e}")
        print("   💡 Install with: pip install agentic-doc")
        return False

def check_google_ai_access():
    """Test Google AI Studio API access (optional)."""
    print("\n🧠 Testing Google AI Studio API access (optional)...")
    
    api_key = os.getenv('GOOGLE_AI_STUDIO_API_KEY')
    if not api_key:
        print("   ⚠️  GOOGLE_AI_STUDIO_API_KEY not set (optional)")
        return True  # Not required, so return True
    
    try:
        import google.generativeai as genai
        print("   ✅ Google AI Studio library available")
        
        # Configure API key
        genai.configure(api_key=api_key)
        print("   ✅ Google AI Studio API key configured")
        
        # Note: We don't test the actual API call to avoid charges
        # The user can test this when they run the actual extraction
        
        return True
        
    except ImportError:
        print("   ⚠️  OpenAI library not installed")
        print("   💡 Install with: pip install openai")
        return True  # Optional, so still return True
    except Exception as e:
        print(f"   ⚠️  OpenAI setup issue: {e}")
        return True  # Optional, so still return True

def check_folders():
    """Check input/output folder structure."""
    print("\n📁 Checking folder structure...")
    
    documents_folder = os.getenv('DOCUMENTS_FOLDER', 'documents')
    documents_path = Path(documents_folder)
    
    if documents_path.exists():
        files = list(documents_path.glob('*'))
        supported_extensions = {
            '.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.gif', '.bmp',
            '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt'
        }
        supported_files = [f for f in files if f.suffix.lower() in supported_extensions]
        
        print(f"   ✅ Documents folder exists: {documents_folder}")
        print(f"      Total files: {len(files)}")
        print(f"      Supported files: {len(supported_files)}")
        
        if len(supported_files) == 0:
            print("   ⚠️  No supported document files found")
            print("      Add PDF, images, or Office documents to process")
        else:
            print(f"      File types found: {set(f.suffix.lower() for f in supported_files)}")
    else:
        print(f"   ❌ Documents folder not found: {documents_folder}")
        print("   💡 Create the folder and add documents to process")
        return False
    
    # Check results directory
    results_dir = os.getenv('RESULTS_SAVE_DIR', 'extraction_results')
    results_path = Path(results_dir)
    
    if not results_path.exists():
        try:
            results_path.mkdir(parents=True)
            print(f"   ✅ Created results directory: {results_dir}")
        except Exception as e:
            print(f"   ⚠️  Could not create results directory: {e}")
    else:
        print(f"   ✅ Results directory exists: {results_dir}")
    
    return True

def generate_test_report():
    """Generate a comprehensive test report."""
    print("\n" + "="*60)
    print("📋 CONFIGURATION TEST REPORT")
    print("="*60)
    
    tests = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment File", check_env_file),
        ("Landing AI Access", check_landing_ai_access),
        ("Google AI Studio Access", check_google_ai_access),
        ("Folders", check_folders)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} test failed with error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
    
    print(f"\nTests passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! You're ready to use the Document Data Extractor!")
        print("\nNext steps:")
        print("1. Add documents to the 'documents' folder")
        print("2. Run: python document_extractor.py")
        print("3. Or try examples: python examples.py")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Get your Landing AI API key from https://landing.ai/")
        print("- Copy .env.example to .env and fill in your API key")
        print("- Add documents to the 'documents' folder")
    
    return passed == total

def main():
    """Main validation function."""
    print("Landing AI Document Data Extractor - Configuration Validator")
    print("=" * 60)
    
    try:
        success = generate_test_report()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Validation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error during validation: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
