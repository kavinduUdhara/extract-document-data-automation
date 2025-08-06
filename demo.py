#!/usr/bin/env python3
"""
Quick Start Demo for Document Data Extractor using Landing AI
This script demonstrates the basic usage of the DocumentDataExtractor.
"""

import os
import sys
from pathlib import Path

def main():
    """Quick start demonstration."""
    print("🚀 Document Data Extractor - Quick Start Demo (Landing AI)")
    print("=" * 60)
    
    # Check if basic setup is done
    if not Path(".env").exists():
        print("❌ Configuration required!")
        print("\nPlease follow these steps:")
        print("1. Copy .env.example to .env")
        print("2. Get your Landing AI API key from https://landing.ai/")
        print("3. Add VISION_AGENT_API_KEY to your .env file")
        print("4. Run: python validate.py")
        print("5. Add documents to the 'documents' folder")
        print("6. Run this demo again")
        return
    
    # Check for Landing AI API key
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('VISION_AGENT_API_KEY')
    if not api_key or api_key == 'your-landing-ai-api-key':
        print("❌ Landing AI API key not configured!")
        print("\nPlease:")
        print("1. Get your API key from https://landing.ai/")
        print("2. Add it to your .env file as VISION_AGENT_API_KEY")
        return
    
    # Check if documents folder exists and has files
    documents_folder = Path("documents")
    if not documents_folder.exists():
        documents_folder.mkdir()
        print("📁 Created 'documents' folder")
    
    # Check for documents
    supported_extensions = {
        '.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.gif', '.bmp',
        '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt'
    }
    document_files = [f for f in documents_folder.iterdir() 
                     if f.is_file() and f.suffix.lower() in supported_extensions]
    
    if not document_files:
        print("📄 No documents found!")
        print(f"\nPlease add document files to the '{documents_folder}' folder.")
        print("Supported formats:")
        print("  • PDF files (.pdf)")
        print("  • Images (.jpg, .png, .tiff, .gif, .bmp)")
        print("  • Office documents (.doc, .docx, .xls, .xlsx, .ppt, .pptx)")
        print("  • Text files (.txt)")
        return
    
    print(f"📄 Found {len(document_files)} document(s) to process:")
    for doc in document_files[:5]:  # Show first 5
        print(f"   • {doc.name}")
    if len(document_files) > 5:
        print(f"   ... and {len(document_files) - 5} more")
    
    print("\n🤖 Starting extraction with Landing AI...")
    
    try:
        # Import and run the extractor
        from document_extractor import DocumentDataExtractor
        
        # Initialize
        extractor = DocumentDataExtractor()
        print("✅ Landing AI document extractor initialized")
        
        # Run extraction
        csv_path = extractor.run_extraction()
        
        if csv_path:
            print(f"\n🎉 Success! CSV file created: {csv_path}")
            
            # Show some stats
            import pandas as pd
            df = pd.read_csv(csv_path)
            print(f"📊 Generated {len(df)} rows with {len(df.columns)} columns")
            print(f"📋 Columns: {', '.join(df.columns.tolist())}")
            
            # Show preview
            print(f"\n📋 Preview of extracted data:")
            print(df.head().to_string())
            
            print(f"\n🎯 Ready for Google Sheets!")
            print(f"1. Open Google Sheets")
            print(f"2. File > Import > Upload: {csv_path}")
            print(f"3. Or copy-paste the CSV content directly")
            
            # Show additional results
            results_dir = extractor.results_save_dir
            if Path(results_dir).exists():
                result_files = list(Path(results_dir).glob('*.json'))
                if result_files:
                    print(f"\n📁 Detailed extraction results saved to: {results_dir}")
                    print(f"   Found {len(result_files)} result file(s)")
            
        else:
            print("❌ No data was extracted")
            print("💡 Check that your documents are in supported formats")
            
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("💡 Run: pip install -r requirements.txt")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Run validation: python validate.py")
        print("💡 Check your Landing AI API key and internet connection")

def demo_single_document():
    """Demo processing a single document."""
    print("\n" + "="*60)
    print("📄 Single Document Processing Demo")
    print("="*60)
    
    documents_folder = Path("documents")
    if not documents_folder.exists():
        print("❌ Documents folder not found")
        return
    
    # Find first supported document
    supported_extensions = {
        '.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.gif', '.bmp',
        '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt'
    }
    
    document_files = [f for f in documents_folder.iterdir() 
                     if f.is_file() and f.suffix.lower() in supported_extensions]
    
    if not document_files:
        print("❌ No supported documents found")
        return
    
    # Use first document
    test_doc = document_files[0]
    print(f"📄 Processing: {test_doc.name}")
    
    try:
        from document_extractor import DocumentDataExtractor
        extractor = DocumentDataExtractor()
        
        # Process single document
        result = extractor.process_document(str(test_doc))
        
        print(f"\n✅ Processing completed!")
        print(f"Status: {result.get('processing_status', 'Unknown')}")
        
        if 'markdown' in result:
            markdown_content = result['markdown']
            print(f"\n📝 Extracted content preview:")
            print("-" * 40)
            preview = markdown_content[:300] + "..." if len(markdown_content) > 300 else markdown_content
            print(preview)
            print("-" * 40)
            print(f"Total content length: {len(markdown_content)} characters")
        
        if 'entities' in result:
            entities = result['entities']
            print(f"\n🏷️  Extracted entities: {len(entities)}")
            for i, entity in enumerate(entities[:5]):  # Show first 5
                print(f"   {i+1}. {entity.get('type', 'unknown')}: {entity.get('content', '')}")
            if len(entities) > 5:
                print(f"   ... and {len(entities) - 5} more")
        
        if result.get('result_path'):
            print(f"\n💾 Detailed results saved to: {result['result_path']}")
        
    except Exception as e:
        print(f"❌ Error processing document: {e}")

if __name__ == "__main__":
    main()
    
    # Uncomment to run single document demo
    # demo_single_document()
