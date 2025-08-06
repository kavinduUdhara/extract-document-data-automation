#!/usr/bin/env python3
"""
Multi-CSV Document Extraction System - Production Version
Handles Windows permission issues and provides robust PDF processing
"""

import os
import json
import tempfile
import shutil
from typing import Dict, List, Any, Optional
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# Try to import Landing AI, but provide fallback if it fails
try:
    from agentic_doc.parse import parse
    LANDING_AI_AVAILABLE = True
except ImportError:
    LANDING_AI_AVAILABLE = False
    print("⚠️  Landing AI not available, using fallback mode")


class ProductionMultiCSVExtractor:
    def __init__(self):
        """Initialize the Production Multi-CSV Document Extractor."""
        # Load environment variables
        load_dotenv()
        
        self.vision_agent_api_key = os.getenv('VISION_AGENT_API_KEY')
        self.google_ai_api_key = os.getenv('GOOGLE_AI_STUDIO_API_KEY')
        
        if not self.google_ai_api_key:
            raise ValueError("GOOGLE_AI_STUDIO_API_KEY not found in environment variables")
        
        # Configure Google AI Studio
        genai.configure(api_key=self.google_ai_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # CSV configurations for all 6 types
        self.csv_configs = {
            'Resort_Details': {
                'system_instruction': """You are a resort data extraction specialist. Create a comprehensive resort details CSV from the provided resort document. Focus on extracting resort-specific information, contact details, location data, and general resort policies.""",
                'columns': ['Resort_Name', 'Location', 'Resort_Type', 'Check_In_Time', 'Check_Out_Time', 'Currency', 'Tax_Rate', 'Service_Charge', 'Contact_Phone', 'Contact_Email', 'Website', 'General_Manager', 'Sales_Director']
            },
            
            'Villas_Rooms': {
                'system_instruction': """You are a villa and room type extraction specialist. Create a detailed CSV of all villa and room types available at the resort. Extract information about each room category, occupancy limits, and basic features.""",
                'columns': ['Villa_Type', 'Max_Occupancy', 'Standard_Occupancy', 'Villa_Features', 'Pool_Available', 'Villa_Category', 'Villa_Size_SQM', 'Bedrooms', 'Bathrooms', 'Balcony_Terrace']
            },
            
            'Meal_Plans': {
                'system_instruction': """You are a meal plan extraction specialist. Create a comprehensive CSV of all meal plan options, dining venues, and food-related policies from the resort document.""",
                'columns': ['Meal_Plan_Type', 'Included_Meals', 'Restaurants_Available', 'Meal_Credits_USD', 'Special_Dining_Options', 'Beverage_Inclusions', 'Dietary_Restrictions', 'Operating_Hours', 'Dress_Code']
            },
            
            'Transfers': {
                'system_instruction': """You are a transfer and transportation extraction specialist. Create a detailed CSV of all transfer options, costs, and transportation policies from the resort document.""",
                'columns': ['Transfer_Type', 'Adult_Price_USD', 'Child_Price_USD', 'Infant_Price_USD', 'Transfer_Duration', 'Baggage_Allowance', 'Excess_Baggage_Fee', 'Operating_Hours', 'Advance_Notice_Required', 'Weather_Dependent']
            },
            
            'Packages': {
                'system_instruction': """You are a resort package extraction specialist. Create a comprehensive CSV of all package deals, seasonal pricing, and package inclusions from the resort document. Extract ALL package combinations and pricing tiers.""",
                'columns': ['Package_Name', 'Villa_Type', 'Season', 'Package_Duration', 'Package_Price_USD', 'Additional_Night_USD', 'Transfer_Type', 'Valid_From', 'Valid_To', 'Minimum_Stay', 'Inclusions', 'Restrictions']
            },
            
            'Room_Rates': {
                'system_instruction': """You are a room rate extraction specialist. Create a detailed CSV of daily room rates, seasonal variations, and occupancy-based pricing from the resort document.""",
                'columns': ['Villa_Type', 'Season', 'Rate_Date_From', 'Rate_Date_To', 'Base_Rate_USD', 'Additional_Person_USD', 'Child_Rate_USD', 'Infant_Rate_USD', 'Min_Stay_Nights', 'Rate_Type', 'Cancellation_Policy']
            }
        }
        
        print("✅ Production Multi-CSV Document Extractor initialized successfully")
    
    def _extract_document_text_with_landing_ai(self, pdf_path: Path) -> Optional[str]:
        """Extract text using Landing AI (if available and working)"""
        if not LANDING_AI_AVAILABLE:
            return None
            
        try:
            # Create a proper temporary directory with better permissions
            temp_dir = Path(tempfile.gettempdir()) / "pdf_extraction"
            temp_dir.mkdir(exist_ok=True)
            
            # Copy file to temp directory with proper permissions
            temp_file = temp_dir / pdf_path.name
            shutil.copy2(pdf_path, temp_file)
            
            # Try to extract with Landing AI
            result = parse(temp_file)
            
            if result and hasattr(result, 'markdown'):
                return result.markdown
            elif result and isinstance(result, list) and len(result) > 0:
                first_result = result[0]
                if hasattr(first_result, 'markdown'):
                    return first_result.markdown
            
            return None
            
        except Exception as e:
            print(f"   ⚠️  Landing AI extraction failed: {str(e)}")
            return None
        finally:
            # Clean up temporary file
            try:
                if 'temp_file' in locals() and temp_file.exists():
                    temp_file.unlink()
            except:
                pass
    
    def _use_existing_extraction(self, pdf_name: str) -> Optional[str]:
        """Use existing extraction results if available"""
        extraction_dir = Path("extraction_results")
        if not extraction_dir.exists():
            return None
        
        # Look for extraction files that match the PDF name
        base_name = pdf_name.replace('.pdf', '').replace('.zdoc.pdf', '')
        
        for extraction_file in extraction_dir.glob("*.json"):
            try:
                with open(extraction_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'markdown' in data:
                        print(f"   ✅ Using existing extraction: {extraction_file.name}")
                        return data['markdown']
            except:
                continue
        
        return None
    
    def _generate_csv_with_ai(self, document_text: str, csv_config: Dict, csv_name: str) -> Optional[str]:
        """Generate CSV using AI with specific configuration"""
        try:
            prompt = f"""
            {csv_config['system_instruction']}
            
            Document text to analyze:
            {document_text}
            
            Generate a CSV with exactly these columns: {', '.join(csv_config['columns'])}
            
            Requirements:
            - First row must be the headers
            - Extract ALL relevant information from the document
            - Use DD/MM/YYYY date format
            - For pricing, include currency (e.g., "USD 1,200")
            - Return ONLY the CSV content, no explanations
            - If information is not available, use "Not specified"
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"   ❌ Failed to generate {csv_name}: {str(e)}")
            return None
    
    def process_document(self, pdf_path: Path, output_folder: Path) -> bool:
        """Process a single PDF document and generate CSV files"""
        
        # Create output folder for this document
        doc_name = pdf_path.stem.replace('.zdoc', '')
        doc_output_dir = output_folder / doc_name
        doc_output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📄 Processing: {pdf_path.name}")
        
        # Try to extract document text
        document_text = None
        
        # First, try existing extraction results
        document_text = self._use_existing_extraction(pdf_path.name)
        
        # If no existing extraction, try Landing AI
        if not document_text and LANDING_AI_AVAILABLE:
            print("   🔄 Extracting with Landing AI...")
            document_text = self._extract_document_text_with_landing_ai(pdf_path)
        
        if not document_text:
            print(f"   ❌ Failed to extract text from {pdf_path.name}")
            return False
        
        print(f"   ✅ Document text extracted ({len(document_text):,} characters)")
        
        # Generate all CSV files
        successful_csvs = 0
        
        for csv_name, config in self.csv_configs.items():
            print(f"   📊 Generating {csv_name}.csv...")
            
            csv_content = self._generate_csv_with_ai(document_text, config, csv_name)
            
            if csv_content:
                # Save CSV file
                csv_file = doc_output_dir / f"{csv_name}.csv"
                
                try:
                    with open(csv_file, 'w', encoding='utf-8') as f:
                        f.write(csv_content)
                    
                    # Count lines for verification
                    lines = csv_content.split('\n')
                    data_rows = len([line for line in lines if line.strip()]) - 1
                    
                    print(f"      ✅ Generated: {data_rows} data rows")
                    successful_csvs += 1
                    
                except Exception as e:
                    print(f"      ❌ Failed to save: {str(e)}")
            else:
                print(f"      ❌ Failed to generate content")
        
        if successful_csvs == len(self.csv_configs):
            print(f"   🎉 All {len(self.csv_configs)} CSV files generated successfully!")
            return True
        else:
            print(f"   ⚠️  Generated {successful_csvs}/{len(self.csv_configs)} CSV files")
            return successful_csvs > 0
    
    def extract_all_documents(self, input_folder: str = "input", output_folder: str = "output"):
        """
        Extract data from all PDF files and generate structured CSV files.
        """
        input_path = Path(input_folder)
        output_path = Path(output_folder)
        
        # Find all PDF files
        pdf_files = list(input_path.glob("*.pdf"))
        
        if not pdf_files:
            print(f"❌ No PDF files found in {input_folder}")
            return
        
        print(f"🚀 Starting Production Multi-CSV Document Extraction...")
        print("=" * 60)
        print(f"📄 Found {len(pdf_files)} PDF files to process")
        
        successful_extractions = 0
        failed_extractions = 0
        
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n📄 Processing {i}/{len(pdf_files)}: {pdf_file.name}")
            
            success = self.process_document(pdf_file, output_path)
            
            if success:
                successful_extractions += 1
            else:
                failed_extractions += 1
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📊 Extraction Summary:")
        print(f"   📄 Total PDFs processed: {len(pdf_files)}")
        print(f"   ✅ Successful extractions: {successful_extractions}")
        print(f"   ❌ Failed extractions: {failed_extractions}")
        print(f"   📁 Output folder: {output_path.absolute()}")
        
        if successful_extractions > 0:
            print("🎉 Production Multi-CSV Document Extraction Complete!")
            
            # List generated folders
            print("\n📁 Generated document folders:")
            for item in sorted(output_path.iterdir()):
                if item.is_dir():
                    csv_files = list(item.glob("*.csv"))
                    print(f"   📂 {item.name}/ ({len(csv_files)} CSV files)")
        else:
            print("❌ No documents were successfully processed.")


def main():
    """Main function to run the production extractor"""
    try:
        extractor = ProductionMultiCSVExtractor()
        extractor.extract_all_documents()
    except Exception as e:
        print(f"❌ Error initializing extractor: {str(e)}")


if __name__ == "__main__":
    main()
