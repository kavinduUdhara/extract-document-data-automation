"""
Complete Multi-CSV Document Extraction System
Processes PDFs individually and generates structured CSV files for each document
"""

import os
import json
import tempfile
import shutil
from typing import Dict, List, Any, Optional
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
from agentic_doc.parse import parse


class MultiCSVDocumentExtractor:
    def __init__(self):
        """Initialize the Multi-CSV Document Extractor."""
        # Load environment variables
        load_dotenv()
        
        self.vision_agent_api_key = os.getenv('VISION_AGENT_API_KEY')
        self.google_ai_api_key = os.getenv('GOOGLE_AI_STUDIO_API_KEY')
        
        if not self.vision_agent_api_key:
            raise ValueError("VISION_AGENT_API_KEY not found in environment variables")
        
        if not self.google_ai_api_key:
            raise ValueError("GOOGLE_AI_STUDIO_API_KEY not found in environment variables")
        
        # Configure Google AI Studio
        genai.configure(api_key=self.google_ai_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("✅ Multi-CSV Document Extractor initialized successfully")
    
    def extract_all_documents(self, input_folder: str = "input", output_folder: str = "output"):
        """
        Extract data from all PDF files and generate structured CSV files.
        
        Args:
            input_folder: Path to folder containing PDF files
            output_folder: Path to output folder for CSV files
        """
        input_path = Path(input_folder)
        output_path = Path(output_folder)
        
        # Find all PDF files
        pdf_files = list(input_path.glob("*.pdf"))
        
        if not pdf_files:
            print("❌ No PDF files found in input folder")
            return
        
        print(f"🚀 Starting Multi-CSV Document Extraction...")
        print("="*60)
        print(f"📄 Found {len(pdf_files)} PDF files to process")
        
        successful_extractions = 0
        failed_extractions = 0
        
        # Process each PDF file
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n📄 Processing {i}/{len(pdf_files)}: {pdf_file.name}")
            try:
                # Extract base filename without extension
                base_name = pdf_file.stem
                
                # Create output subfolder for this PDF
                pdf_output_folder = output_path / base_name
                pdf_output_folder.mkdir(parents=True, exist_ok=True)
                
                # Extract document data using Landing AI
                markdown_text = self._extract_document_text(str(pdf_file))
                
                if markdown_text:
                    # Generate all CSV files for this document
                    csv_count = self._generate_all_csv_files(markdown_text, pdf_output_folder, base_name)
                    print(f"   ✅ Successfully generated {csv_count} CSV files for {pdf_file.name}")
                    successful_extractions += 1
                else:
                    print(f"   ❌ Failed to extract data from {pdf_file.name}")
                    failed_extractions += 1
                    
            except Exception as e:
                print(f"   ❌ Error processing {pdf_file.name}: {str(e)}")
                failed_extractions += 1
        
        # Print summary
        print("="*60)
        print(f"📊 Extraction Summary:")
        print(f"   📄 Total PDFs processed: {len(pdf_files)}")
        print(f"   ✅ Successful extractions: {successful_extractions}")
        print(f"   ❌ Failed extractions: {failed_extractions}")
        print(f"   📁 Output folder: {output_path.absolute()}")
        print("🎉 Multi-CSV Document Extraction Complete!")
    
    def _extract_document_text(self, pdf_path: str) -> Optional[str]:
        """
        Extract document text using Landing AI.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted markdown text or None if failed
        """
        try:
            # Create temporary folder for single PDF 
            with tempfile.TemporaryDirectory() as temp_dir:
                # Copy PDF to temp directory
                temp_pdf = os.path.join(temp_dir, os.path.basename(pdf_path))
                shutil.copy2(pdf_path, temp_pdf)
                
                print(f"   🔄 Extracting with Landing AI...")
                
                # Extract data using Landing AI parse function
                extraction_result = parse(temp_dir)
                
                if extraction_result and len(extraction_result) > 0:
                    # Get the markdown content from the first document
                    first_doc = extraction_result[0]
                    if hasattr(first_doc, 'markdown'):
                        return first_doc.markdown
                    else:
                        print(f"   ⚠️ No markdown content found in extraction result")
                        return None
                else:
                    print(f"   ❌ No extraction results returned")
                    return None
                    
        except Exception as e:
            print(f"   ❌ Landing AI extraction error: {str(e)}")
            return None
    
    def _generate_all_csv_files(self, markdown_text: str, output_folder: Path, base_name: str) -> int:
        """
        Generate all CSV files for a document using separate AI prompts.
        
        Args:
            markdown_text: Extracted document text from Landing AI
            output_folder: Output folder for CSV files
            base_name: Base filename
            
        Returns:
            Number of CSV files successfully generated
        """
        print(f"   📝 Generating CSV files...")
        
        successful_files = 0
        
        # Generate each CSV file separately
        csv_types = [
            ("Resort_Details", "Resort Name,Resort Legal Name,Atoll,Star Category,Offer Type,Resort Category,Board Type,Marketplace,Booking Period - From,Booking Period - To,Age Definition,Teenage From Age,Child From Age,Early Check-In Cost,Late Check-Out Cost,Resort Details (Intro),Resort Terms and Conditions,Resort Cancellation Policy,Other Additional Information"),
            ("Villas_Rooms", "Resort Name,Room Type,No of Rooms / Villas,Room / Villa Category,Basic Occupancy Count: Adult,Basic Occupancy Count: Teenage,Basic Occupancy Count: Child,Maximum Occupancy (Including Basic),Room Size (sqm),Minimum Stay (Nights),Bed Type,Bed Count,Room / Villa Description,Facilities Provided,Room Terms and Conditions"),
            ("Meal_Plans", "Resort Name,Meal Plan,Cost for Adult,Cost for Child,Meal Plan Inclusion Details,If Included in a Package"),
            ("Transfers", "Resort Name,Transfer Name,Transfer Type,Valid Travel - From,Valid Travel - To,Transfer Cost: Adult,Transfer Cost: Child,Included in Package(s),Transfer Terms and Conditions"),
            ("Packages", "Resort Name,Package Name,Package Inclusion,Apply Countries,Package Period - From,Package Period - To,Booking Period - From,Booking Period - To,Blackout Periods,Villa / Room Type,Stay Duration (Nights),Basic Occupancy Count: Adult,Basic Occupancy Count: Teenage,Basic Occupancy Count: Child,Maximum Occupancy (Including Basic),Meal Plan,Transfer,Package Cost,Package Value,Extra Person Rate per Night: Adult,Extra Person Rate per Night: Teenage,Extra Person Rate per Night: Child"),
            ("Room_Rates", "Resort Name,Ban Countries,Room Type,Rate Period - From,Rate Period - To,Rate Based On,Room Rate,Extra Person Rate: Adult,Extra Person Rate: Teenage,Extra Person Rate: Child")
        ]
        
        for csv_name, headers in csv_types:
            try:
                csv_content = self._generate_csv_with_ai(markdown_text, csv_name, headers)
                
                if csv_content and csv_content.strip():
                    # Save CSV file
                    csv_path = output_folder / f"{csv_name}.csv"
                    
                    with open(csv_path, 'w', encoding='utf-8') as f:
                        f.write(csv_content)
                    
                    successful_files += 1
                    print(f"      ✅ {csv_name}.csv")
                else:
                    print(f"      ⚠️ No data for {csv_name}.csv")
                    
            except Exception as e:
                print(f"      ❌ Error generating {csv_name}: {str(e)}")
        
        return successful_files
    
    def _generate_csv_with_ai(self, markdown_text: str, csv_name: str, headers: str) -> str:
        """Generate CSV content using Google AI for specific CSV type."""
        
        # Define specific instructions for each CSV type
        instructions = {
            "Resort_Details": "Extract resort information. Resort Name: ALL CAPS, append '- PACKAGE' if package document. Marketplace: target countries.",
            "Villas_Rooms": "Extract room/villa details. One row per room type. Include occupancy and room descriptions.",
            "Meal_Plans": "Extract meal plan information. Include costs and detailed descriptions.",
            "Transfers": "Extract transfer details. Include seaplane, domestic flights, speedboat transfers with costs.",
            "Packages": "CRITICAL: Create separate rows for EACH combination of room type × season × transfer type. Extract ALL package combinations.",
            "Room_Rates": "Extract room rates by season and room type. Include any country restrictions."
        }
        
        instruction = instructions.get(csv_name, "Extract relevant data")
        
        prompt = f"""
You are processing resort documents to extract {csv_name.replace('_', ' ').lower()} data.

Create a CSV with these exact headers:
{headers}

Instructions: {instruction}

IMPORTANT RULES:
- Return ONLY the CSV data with headers, no other text or explanations
- If information is missing, use 'Not specified'
- Extract exactly as written from documents
- For dates, use DD/MM/YYYY format
- Don't summarize or paraphrase

Document text to extract from:
{markdown_text[:20000]}...
        """
        
        try:
            response = self.model.generate_content(prompt)
            csv_content = response.text.strip()
            
            # Clean up response (remove markdown code blocks if present)
            if csv_content.startswith("```"):
                lines = csv_content.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                csv_content = "\n".join(lines)
            
            return csv_content
            
        except Exception as e:
            print(f"      ❌ Google AI error for {csv_name}: {str(e)}")
            return ""


def main():
    """Main function to run the multi-CSV extraction."""
    try:
        extractor = MultiCSVDocumentExtractor()
        extractor.extract_all_documents("input", "output")
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")


if __name__ == "__main__":
    main()
