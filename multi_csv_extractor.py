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
        # Define CSV configurations
        csv_configs = {
            "Resort_Details": {
                "headers": "Resort Name,Resort Legal Name,Atoll,Star Category,Offer Type,Resort Category,Board Type,Marketplace,Booking Period - From,Booking Period - To,Age Definition,Teenage From Age,Child From Age,Early Check-In Cost,Late Check-Out Cost,Resort Details (Intro),Resort Terms and Conditions,Resort Cancellation Policy,Other Additional Information",
                "instructions": """Extract resort information. Rules:
- Resort Name: ALL CAPS, append '- PACKAGE' if it's a package document
- Resort Legal Name: CamelCase format
- Board Type: Select lowest meal board type (B/B, H/B, F/B, etc.) or 'Not specified'
- Resort Category: Island Resort / City Hotel / Guest House
- Marketplace: Target countries/regions (Middle East, Europe, Asia, etc.)
- Dates: DD/MM/YYYY format
- Early/Late costs: 0 if not specified
- Descriptions: Max 3000 characters, extract exactly as written"""
            },
            
            "Villas_Rooms": {
                "headers": "Resort Name,Room Type,No of Rooms / Villas,Room / Villa Category,Basic Occupancy Count: Adult,Basic Occupancy Count: Teenage,Basic Occupancy Count: Child,Maximum Occupancy (Including Basic),Room Size (sqm),Minimum Stay (Nights),Bed Type,Bed Count,Room / Villa Description,Facilities Provided,Room Terms and Conditions",
                "instructions": """Extract room/villa details. Rules:
- Create one row per room/villa type mentioned
- Extract exactly as written from documents
- Basic Occupancy: Standard occupancy numbers
- Maximum Occupancy: Including extra persons
- If information missing, use 'Not specified'"""
            },
            
            "Meal_Plans": {
                "headers": "Resort Name,Meal Plan,Cost for Adult,Cost for Child,Meal Plan Inclusion Details,If Included in a Package",
                "instructions": """Extract meal plan information. Rules:
- Create one row per meal plan (Half Board, Full Board, etc.)
- Extract costs exactly as stated
- Include detailed descriptions of what's included in meals
- Mention package names if applicable or 'Not included'"""
            },
            
            "Transfers": {
                "headers": "Resort Name,Transfer Name,Transfer Type,Valid Travel - From,Valid Travel - To,Transfer Cost: Adult,Transfer Cost: Child,Included in Package(s),Transfer Terms and Conditions",
                "instructions": """Extract transfer details. Rules:
- Create one row per transfer type
- Transfer Type: Shared Seaplane, Private Luxury Yacht, Domestic Flight + Speedboat, etc.
- Extract costs exactly as stated
- List package names where transfers are included or 'Not included'
- Include terms and conditions for transfers"""
            },
            
            "Packages": {
                "headers": "Resort Name,Package Name,Package Inclusion,Apply Countries,Package Period - From,Package Period - To,Booking Period - From,Booking Period - To,Blackout Periods,Villa / Room Type,Stay Duration (Nights),Basic Occupancy Count: Adult,Basic Occupancy Count: Teenage,Basic Occupancy Count: Child,Maximum Occupancy (Including Basic),Meal Plan,Transfer,Package Cost,Package Value,Extra Person Rate per Night: Adult,Extra Person Rate per Night: Teenage,Extra Person Rate per Night: Child",
                "instructions": """Extract package details. CRITICAL: 
- Create separate rows for EACH combination of room type × season × transfer type
- Extract ALL package combinations from rate tables
- Package Cost: State exact price from tables
- Package Inclusion: Include ALL benefits (floating breakfast, shisha, activities, etc.)
- Dates: DD/MM/YYYY format
- Include ALL benefits and inclusions mentioned
- Honeymoon/Anniversary/Birthday benefits only if in package documents"""
            },
            
            "Room_Rates": {
                "headers": "Resort Name,Ban Countries,Room Type,Rate Period - From,Rate Period - To,Rate Based On,Room Rate,Extra Person Rate: Adult,Extra Person Rate: Teenage,Extra Person Rate: Child",
                "instructions": """Extract room rates. Rules:
- Create one row per rate entry per room type
- Rate Based On: Per Room Per Night / Per Person Per Day
- Extract all seasonal rates (Low Season, Shoulder Season, Peak Season)
- Include any country restrictions or bans
- Dates: DD/MM/YYYY format"""
            }
        }\n        \n        print(f\"   📝 Generating {len(csv_configs)} CSV files...\")\n        \n        successful_files = 0\n        \n        # Generate each CSV file separately\n        for csv_name, config in csv_configs.items():\n            try:\n                csv_content = self._generate_csv_with_ai(markdown_text, csv_name, config)\n                \n                if csv_content and csv_content.strip():\n                    # Save CSV file\n                    csv_path = output_folder / f\"{csv_name}.csv\"\n                    \n                    with open(csv_path, 'w', encoding='utf-8') as f:\n                        f.write(csv_content)\n                    \n                    successful_files += 1\n                    print(f\"      ✅ {csv_name}.csv\")\n                else:\n                    print(f\"      ⚠️ No data for {csv_name}.csv\")\n                    \n            except Exception as e:\n                print(f\"      ❌ Error generating {csv_name}: {str(e)}\")\n        \n        return successful_files\n    \n    def _generate_csv_with_ai(self, markdown_text: str, csv_name: str, config: Dict) -> str:\n        \"\"\"Generate CSV content using Google AI for specific CSV type.\"\"\"\n        \n        prompt = f\"\"\"\nYou are processing resort documents to extract {csv_name.replace('_', ' ').lower()} data.\n\nCreate a CSV with these exact headers:\n{config['headers']}\n\n{config['instructions']}\n\nIMPORTANT RULES:\n- Return ONLY the CSV data with headers, no other text or explanations\n- If information is missing, use 'Not specified'\n- Extract exactly as written from documents\n- For dates, use DD/MM/YYYY format\n- Don't summarize or paraphrase\n- Don't add extra rows with 'Note:' or explanations\n\nDocument text to extract from:\n{markdown_text[:20000]}...\n        \"\"\"\n        \n        try:\n            response = self.model.generate_content(prompt)\n            csv_content = response.text.strip()\n            \n            # Clean up response (remove markdown code blocks if present)\n            if csv_content.startswith(\"```\"):\n                lines = csv_content.split(\"\\n\")\n                if lines[0].startswith(\"```\"):\n                    lines = lines[1:]\n                if lines and lines[-1].startswith(\"```\"):\n                    lines = lines[:-1]\n                csv_content = \"\\n\".join(lines)\n            \n            return csv_content\n            \n        except Exception as e:\n            print(f\"      ❌ Google AI error for {csv_name}: {str(e)}\")\n            return \"\"\n\n\ndef main():\n    \"\"\"Main function to run the multi-CSV extraction.\"\"\"\n    try:\n        extractor = MultiCSVDocumentExtractor()\n        extractor.extract_all_documents(\"input\", \"output\")\n    except Exception as e:\n        print(f\"❌ Fatal error: {str(e)}\")\n\n\nif __name__ == \"__main__\":\n    main()
