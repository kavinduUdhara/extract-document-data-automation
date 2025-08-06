"""
Enhanced Document Data Extractor with Multiple CSV Generation
"""

import os
import json
import pandas as pd
import tempfile
import shutil
from typing import Dict, List, Any, Optional
from pathlib import Path
import google.generativeai as genai
from agentic_doc.parse import parse


class EnhancedDocumentExtractor:
    def __init__(self, vision_agent_api_key: str, google_ai_api_key: str):
        """
        Initialize the Enhanced Document Extractor.
        
        Args:
            vision_agent_api_key: API key for Landing AI Vision Agent
            google_ai_api_key: API key for Google AI Studio
        """
        self.vision_agent_api_key = vision_agent_api_key
        self.google_ai_api_key = google_ai_api_key
        
        # Configure Google AI Studio
        genai.configure(api_key=google_ai_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("Enhanced Document Extractor initialized successfully")
    
    def extract_documents(self, input_folder: str, output_folder: str):
        """
        Extract data from all PDF files in input folder and generate structured CSV files.
        
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
        
        print(f"📄 Found {len(pdf_files)} PDF files to process")
        
        # Process each PDF file
        for pdf_file in pdf_files:
            print(f"\n🔄 Processing: {pdf_file.name}")
            try:
                # Extract base filename without extension
                base_name = pdf_file.stem
                
                # Create output subfolder for this PDF
                pdf_output_folder = output_path / base_name
                pdf_output_folder.mkdir(parents=True, exist_ok=True)
                
                # Extract document data using Landing AI (reuse working approach)
                document_data = self._extract_with_working_method(str(pdf_file))
                
                if document_data:
                    # Generate all CSV files for this document
                    self._generate_all_csv_files(document_data, pdf_output_folder, base_name)
                    print(f"✅ Successfully processed {pdf_file.name}")
                else:
                    print(f"❌ Failed to extract data from {pdf_file.name}")
                    
            except Exception as e:
                print(f"❌ Error processing {pdf_file.name}: {str(e)}")
    
    def _extract_with_working_method(self, pdf_path: str) -> Optional[str]:
        """
        Extract document data using the working Landing AI approach.
        
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
                
                print(f"📄 Processing document: {os.path.basename(pdf_path)}")
                
                # Extract data using Landing AI parse function (same as working code)
                extraction_result = parse(temp_dir)
                
                if extraction_result and len(extraction_result) > 0:
                    # Get the markdown content from the first document
                    first_doc = extraction_result[0]
                    if hasattr(first_doc, 'markdown'):
                        return first_doc.markdown
                    else:
                        print(f"⚠️ No markdown content found in extraction result")
                        return str(first_doc)
                else:
                    print(f"❌ No extraction results returned")
                    return None
                    
        except Exception as e:
            print(f"Landing AI extraction error: {str(e)}")
            return None
    
    def _generate_all_csv_files(self, document_text: str, output_folder: Path, base_name: str):
        """
        Generate all CSV files for a document using separate AI prompts.
        
        Args:
            document_text: Extracted document text from Landing AI
            output_folder: Output folder for CSV files
            base_name: Base filename
        """
        # List of CSV types to generate
        csv_types = [
            "resort_details",
            "villas_rooms", 
            "meal_plans",
            "transfers",
            "packages",
            "room_rates"
        ]
        
        print(f"📝 Generating {len(csv_types)} CSV files...")
        
        # Generate each CSV file separately
        for csv_type in csv_types:
            try:
                csv_content = self._generate_csv_with_ai(document_text, csv_type)
                
                if csv_content and csv_content.strip():
                    # Save CSV file
                    csv_filename = f"{csv_type.title().replace('_', '_')}.csv"
                    csv_path = output_folder / csv_filename
                    
                    with open(csv_path, 'w', encoding='utf-8') as f:
                        f.write(csv_content)
                    
                    print(f"  ✅ Generated: {csv_filename}")
                else:
                    print(f"  ⚠️ No data generated for: {csv_type}")
                    
            except Exception as e:
                print(f"  ❌ Error generating {csv_type}: {str(e)}")
    
    def _generate_csv_with_ai(self, document_text: str, csv_type: str) -> str:
        """
        Generate CSV content using Google AI for specific CSV type.
        
        Args:
            document_data: Document data from Landing AI
            csv_type: Type of CSV to generate
            
        Returns:
            CSV content as string
        """
        # Define prompts for each CSV type
        prompts = {
            "resort_details": {
                "headers": "Resort Name,Resort Legal Name,Atoll,Star Category,Offer Type,Resort Category,Board Type,Marketplace,Booking Period - From,Booking Period - To,Age Definition,Teenage From Age,Child From Age,Early Check-In Cost,Late Check-Out Cost,Resort Details (Intro),Resort Terms and Conditions,Resort Cancellation Policy,Other Additional Information",
                "rules": """
Rules for Resort Details:
- Resort Name: ALL CAPS. If package, append '- PACKAGE'. Max 40 chars.
- Resort Legal Name: CamelCase format
- Board Type: Select lowest meal board type (B/B, H/B, F/B, etc.) or 'Not specified'
- Resort Category: Island Resort / City Hotel / Guest House
- Marketplace: Australia, Eastern Europe/CIS, Europe, Russia, Middle East, Africa, Asia, South America
- Dates: DD/MM/YYYY format
- Early/Late costs: 0 if not specified
- Descriptions: Max 3000 characters
- Extract exactly as written, don't paraphrase
                """
            },
            
            "villas_rooms": {
                "headers": "Resort Name,Room Type,No of Rooms / Villas,Room / Villa Category,Basic Occupancy Count: Adult,Basic Occupancy Count: Teenage,Basic Occupancy Count: Child,Maximum Occupancy (Including Basic),Room Size (sqm),Minimum Stay (Nights),Bed Type,Bed Count,Room / Villa Description,Facilities Provided,Room Terms and Conditions",
                "rules": """
Rules for Villas/Rooms:
- Create one row per room/villa type
- Extract exactly as written from documents
- Basic Occupancy: Standard occupancy numbers
- Maximum Occupancy: Including extra persons
- If information missing, use 'Not specified'
                """
            },
            
            "meal_plans": {
                "headers": "Resort Name,Meal Plan,Cost for Adult,Cost for Child,Meal Plan Inclusion Details,If Included in a Package",
                "rules": """
Rules for Meal Plans:
- Create one row per meal plan
- Extract costs exactly as stated
- Include detailed descriptions of what's included
- Mention package names if applicable or 'Not included'
                """
            },
            
            "transfers": {
                "headers": "Resort Name,Transfer Name,Transfer Type,Valid Travel - From,Valid Travel - To,Transfer Cost: Adult,Transfer Cost: Child,Included in Package(s),Transfer Terms and Conditions",
                "rules": """
Rules for Transfers:
- Create one row per transfer type
- Transfer Type: Shared Seaplane, Private Luxury Yacht, Domestic Flight + Speedboat, etc.
- Extract costs exactly as stated
- List package names or 'Not included'
                """
            },
            
            "packages": {
                "headers": "Resort Name,Package Name,Package Inclusion,Apply Countries,Package Period - From,Package Period - To,Booking Period - From,Booking Period - To,Blackout Periods,Villa / Room Type,Stay Duration (Nights),Basic Occupancy Count: Adult,Basic Occupancy Count: Teenage,Basic Occupancy Count: Child,Maximum Occupancy (Including Basic),Meal Plan,Transfer,Package Cost,Package Value,Extra Person Rate per Night: Adult,Extra Person Rate per Night: Teenage,Extra Person Rate per Night: Child",
                "rules": """
Rules for Packages:
CRITICAL: Create separate rows for each combination of:
- Room/Villa type (Beach Villa, Deluxe Beach Villa, etc.)
- Season (Low Season, Shoulder Season, etc.)
- Transfer type (Seaplane, Domestic Flight + Speedboat)

- Extract ALL package combinations from rate tables
- Package Cost: State exact price from tables
- Dates: DD/MM/YYYY format
- Include ALL benefits and inclusions
- Honeymoon/Anniversary/Birthday benefits only if in package documents
                """
            },
            
            "room_rates": {
                "headers": "Resort Name,Ban Countries,Room Type,Rate Period - From,Rate Period - To,Rate Based On,Room Rate,Extra Person Rate: Adult,Extra Person Rate: Teenage,Extra Person Rate: Child",
                "rules": """
Rules for Room Rates:
- Create one row per rate entry per room
- Rate Based On: Per Room Per Night / Per Person Per Day
- Extract all seasonal rates
- Include any country restrictions
- Dates: DD/MM/YYYY format
                """
            }
        }
        
        prompt_config = prompts.get(csv_type, {})
        headers = prompt_config.get("headers", "")
        rules = prompt_config.get("rules", "")
        
    def _generate_csv_with_ai(self, document_text: str, csv_type: str) -> str:
        """
        Generate CSV content using Google AI for specific CSV type.
        
        Args:
            document_text: Document text from Landing AI
            csv_type: Type of CSV to generate
            
        Returns:
            CSV content as string
        """
        # Define prompts for each CSV type
        prompts = {
            "resort_details": {
                "headers": "Resort Name,Resort Legal Name,Atoll,Star Category,Offer Type,Resort Category,Board Type,Marketplace,Booking Period - From,Booking Period - To,Age Definition,Teenage From Age,Child From Age,Early Check-In Cost,Late Check-Out Cost,Resort Details (Intro),Resort Terms and Conditions,Resort Cancellation Policy,Other Additional Information",
                "rules": """
Rules for Resort Details:
- Resort Name: ALL CAPS. If package, append '- PACKAGE'. Max 40 chars.
- Resort Legal Name: CamelCase format
- Board Type: Select lowest meal board type (B/B, H/B, F/B, etc.) or 'Not specified'
- Resort Category: Island Resort / City Hotel / Guest House
- Marketplace: Australia, Eastern Europe/CIS, Europe, Russia, Middle East, Africa, Asia, South America
- Dates: DD/MM/YYYY format
- Early/Late costs: 0 if not specified
- Descriptions: Max 3000 characters
- Extract exactly as written, don't paraphrase
                """
            },
            
            "villas_rooms": {
                "headers": "Resort Name,Room Type,No of Rooms / Villas,Room / Villa Category,Basic Occupancy Count: Adult,Basic Occupancy Count: Teenage,Basic Occupancy Count: Child,Maximum Occupancy (Including Basic),Room Size (sqm),Minimum Stay (Nights),Bed Type,Bed Count,Room / Villa Description,Facilities Provided,Room Terms and Conditions",
                "rules": """
Rules for Villas/Rooms:
- Create one row per room/villa type
- Extract exactly as written from documents
- Basic Occupancy: Standard occupancy numbers
- Maximum Occupancy: Including extra persons
- If information missing, use 'Not specified'
                """
            },
            
            "meal_plans": {
                "headers": "Resort Name,Meal Plan,Cost for Adult,Cost for Child,Meal Plan Inclusion Details,If Included in a Package",
                "rules": """
Rules for Meal Plans:
- Create one row per meal plan
- Extract costs exactly as stated
- Include detailed descriptions of what's included
- Mention package names if applicable or 'Not included'
                """
            },
            
            "transfers": {
                "headers": "Resort Name,Transfer Name,Transfer Type,Valid Travel - From,Valid Travel - To,Transfer Cost: Adult,Transfer Cost: Child,Included in Package(s),Transfer Terms and Conditions",
                "rules": """
Rules for Transfers:
- Create one row per transfer type
- Transfer Type: Shared Seaplane, Private Luxury Yacht, Domestic Flight + Speedboat, etc.
- Extract costs exactly as stated
- List package names or 'Not included'
                """
            },
            
            "packages": {
                "headers": "Resort Name,Package Name,Package Inclusion,Apply Countries,Package Period - From,Package Period - To,Booking Period - From,Booking Period - To,Blackout Periods,Villa / Room Type,Stay Duration (Nights),Basic Occupancy Count: Adult,Basic Occupancy Count: Teenage,Basic Occupancy Count: Child,Maximum Occupancy (Including Basic),Meal Plan,Transfer,Package Cost,Package Value,Extra Person Rate per Night: Adult,Extra Person Rate per Night: Teenage,Extra Person Rate per Night: Child",
                "rules": """
Rules for Packages:
CRITICAL: Create separate rows for each combination of:
- Room/Villa type (Beach Villa, Deluxe Beach Villa, etc.)
- Season (Low Season, Shoulder Season, etc.)
- Transfer type (Seaplane, Domestic Flight + Speedboat)

- Extract ALL package combinations from rate tables
- Package Cost: State exact price from tables
- Dates: DD/MM/YYYY format
- Include ALL benefits and inclusions
- Honeymoon/Anniversary/Birthday benefits only if in package documents
                """
            },
            
            "room_rates": {
                "headers": "Resort Name,Ban Countries,Room Type,Rate Period - From,Rate Period - To,Rate Based On,Room Rate,Extra Person Rate: Adult,Extra Person Rate: Teenage,Extra Person Rate: Child",
                "rules": """
Rules for Room Rates:
- Create one row per rate entry per room
- Rate Based On: Per Room Per Night / Per Person Per Day
- Extract all seasonal rates
- Include any country restrictions
- Dates: DD/MM/YYYY format
                """
            }
        }
        
        prompt_config = prompts.get(csv_type, {})
        headers = prompt_config.get("headers", "")
        rules = prompt_config.get("rules", "")
        
        user_prompt = f"""
You are processing resort documents. Extract {csv_type.replace('_', ' ')} data and create a CSV with these exact headers:
{headers}

{rules}

IMPORTANT: 
- Return ONLY the CSV data with headers, no other text
- If information is missing, use 'Not specified'
- Extract exactly as written from documents
- Don't summarize or paraphrase

Document text to extract from:
{document_text[:15000]}...
        """
        
        try:
            response = self.model.generate_content(user_prompt)
            csv_content = response.text.strip()
            
            # Clean up the response (remove markdown code blocks if present)
            if csv_content.startswith("```"):
                lines = csv_content.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                csv_content = "\n".join(lines)
            
            return csv_content
            
        except Exception as e:
            print(f"Error generating {csv_type} with Google AI: {str(e)}")
            return ""


def main():
    """Main function to run enhanced extraction."""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    vision_agent_api_key = os.getenv('VISION_AGENT_API_KEY')
    google_ai_api_key = os.getenv('GOOGLE_AI_STUDIO_API_KEY')
    
    if not vision_agent_api_key:
        print("❌ VISION_AGENT_API_KEY not found in environment variables")
        return
    
    if not google_ai_api_key:
        print("❌ GOOGLE_AI_STUDIO_API_KEY not found in environment variables")
        return
    
    # Initialize extractor
    extractor = EnhancedDocumentExtractor(vision_agent_api_key, google_ai_api_key)
    
    # Set input and output folders
    input_folder = "input"
    output_folder = "output"
    
    # Run extraction
    print("🚀 Starting Enhanced Document Extraction...")
    print("="*50)
    extractor.extract_documents(input_folder, output_folder)
    print("="*50)
    print("🎉 Enhanced Document Extraction Complete!")


if __name__ == "__main__":
    main()
