#!/usr/bin/env python3
"""
Test script to verify the document extraction pipeline is working.
"""

import os
from document_extractor import DocumentDataExtractor
from pathlib import Path

def main():
    """Run a test extraction on the input folder."""
    print("🧪 Starting Document Extraction Test")
    print("=" * 50)
    
    # Initialize the extractor
    try:
        extractor = DocumentDataExtractor()
        print("✅ DocumentDataExtractor initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize extractor: {e}")
        return
    
    # Check input folder
    input_folder = "input"
    if not Path(input_folder).exists():
        print(f"❌ Input folder '{input_folder}' not found")
        return
    
    # List PDF files in input folder
    pdf_files = list(Path(input_folder).glob("*.pdf"))
    print(f"📄 Found {len(pdf_files)} PDF files in input folder:")
    for pdf_file in pdf_files:
        print(f"   - {pdf_file.name}")
    
    if not pdf_files:
        print("❌ No PDF files found in input folder")
        return
    
    # Create output folder if it doesn't exist
    output_folder = Path("output")
    output_folder.mkdir(exist_ok=True)
    print(f"📁 Output folder: {output_folder}")
    
    # Process each PDF individually
    print(f"\n🚀 Starting extraction process for {len(pdf_files)} PDF files...")
    successful_extractions = 0
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n📄 Processing {i}/{len(pdf_files)}: {pdf_file.name}")
        
        try:
            # Create output filename based on PDF name
            pdf_stem = pdf_file.stem  # filename without extension
            output_csv = output_folder / f"{pdf_stem}_extracted.csv"
            
            # Create a temporary folder with just this PDF
            temp_folder = Path("temp_single_pdf")
            temp_folder.mkdir(exist_ok=True)
            
            # Copy the single PDF to temp folder
            import shutil
            temp_pdf = temp_folder / pdf_file.name
            shutil.copy2(pdf_file, temp_pdf)
            
            # Process this single PDF
            csv_path = extractor.run_extraction(
                documents_folder=str(temp_folder),
                output_csv=str(output_csv),
                use_google_ai=True
            )
            
            # Clean up temp folder
            shutil.rmtree(temp_folder)
            
            if csv_path and Path(csv_path).exists():
                file_size = Path(csv_path).stat().st_size
                print(f"   ✅ Success! CSV created: {output_csv.name} ({file_size} bytes)")
                successful_extractions += 1
                
                # Show preview for first file or if only one file
                if i == 1 or len(pdf_files) == 1:
                    print(f"   📖 Preview of {output_csv.name}:")
                    with open(csv_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()[:3]
                        for j, line in enumerate(lines, 1):
                            preview = line.strip()
                            if len(preview) > 100:
                                preview = preview[:97] + "..."
                            print(f"      {j}: {preview}")
            else:
                print(f"   ❌ Failed to create CSV for {pdf_file.name}")
                
        except Exception as e:
            print(f"   ❌ Error processing {pdf_file.name}: {e}")
            # Clean up temp folder if it exists
            temp_folder = Path("temp_single_pdf")
            if temp_folder.exists():
                shutil.rmtree(temp_folder)
    
    # Summary
    print(f"\n📊 Extraction Summary:")
    print(f"   📄 Total PDFs processed: {len(pdf_files)}")
    print(f"   ✅ Successful extractions: {successful_extractions}")
    print(f"   ❌ Failed extractions: {len(pdf_files) - successful_extractions}")
    print(f"   📁 Output folder: {output_folder.absolute()}")
    
    if successful_extractions > 0:
        print(f"\n🎉 All CSV files saved in the output folder!")
        output_files = list(output_folder.glob("*.csv"))
        for csv_file in output_files:
            print(f"   📄 {csv_file.name}")
    else:
        print("❌ No CSV files were generated")

if __name__ == "__main__":
    main()
    main()
