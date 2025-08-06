import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
import json
import logging
from dotenv import load_dotenv
from agentic_doc.parse import parse

# Load environment variables
load_dotenv()

class DocumentDataExtractor:
    """
    A class to extract data from documents using Landing AI Agentic Document Extraction
    and process it to generate CSV output ready for Google Sheets.
    """
    
    def __init__(self):
        """Initialize the DocumentDataExtractor with Landing AI configurations."""
        self.api_key = os.getenv('VISION_AGENT_API_KEY')
        self.results_save_dir = os.getenv('RESULTS_SAVE_DIR', 'extraction_results')
        
        # Validate required environment variables
        if not self.api_key:
            raise ValueError("Missing VISION_AGENT_API_KEY. Please check your .env file.")
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Create results directory
        Path(self.results_save_dir).mkdir(parents=True, exist_ok=True)
        
        self.logger.info("Landing AI Document Extractor initialized successfully")
    
    def process_document(self, file_path: str, save_results: bool = True) -> Dict[str, Any]:
        """
        Process a single document using Landing AI Agentic Document Extraction.
        
        Args:
            file_path (str): Path to the document file
            save_results (bool): Whether to save extraction results to directory
            
        Returns:
            Dict[str, Any]: Extracted document data
        """
        try:
            self.logger.info(f"Processing document: {Path(file_path).name}")
            
            # Parse the document using Landing AI
            if save_results:
                # Save results to directory
                result = parse(file_path, result_save_dir=self.results_save_dir)
            else:
                # Get results as objects only
                result = parse(file_path)
            
            if not result or len(result) == 0:
                raise ValueError("No results returned from document parsing")
            
            # Extract the first result (documents typically return one result)
            doc_result = result[0]
            
            # Extract structured data
            extracted_data = {
                'file_name': Path(file_path).name,
                'file_path': file_path,
                'markdown': doc_result.markdown if hasattr(doc_result, 'markdown') else '',
                'chunks': doc_result.chunks if hasattr(doc_result, 'chunks') else [],
                'result_path': doc_result.result_path if hasattr(doc_result, 'result_path') else None,
                'processing_status': 'success'
            }
            
            # Extract additional structured information from chunks
            entities = []
            tables = []
            text_content = []
            
            for chunk in extracted_data.get('chunks', []):
                if isinstance(chunk, dict):
                    chunk_type = chunk.get('type', 'unknown')
                    content = chunk.get('content', '')
                    
                    if chunk_type in ['entity', 'name', 'date', 'amount', 'address']:
                        entities.append({
                            'type': chunk_type,
                            'content': content,
                            'confidence': chunk.get('confidence', 1.0)
                        })
                    elif chunk_type == 'table':
                        tables.append(content)
                    else:
                        text_content.append(content)
            
            extracted_data.update({
                'entities': entities,
                'tables': tables,
                'text_content': text_content,
                'full_text': extracted_data['markdown']
            })
            
            self.logger.info(f"Successfully processed document: {file_path}")
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"Error processing document {file_path}: {e}")
            return {
                'file_name': Path(file_path).name,
                'file_path': file_path,
                'error': str(e),
                'processing_status': 'failed'
            }
    
    def process_folder(self, folder_path: str) -> List[Dict[str, Any]]:
        """
        Process all documents in a folder.
        
        Args:
            folder_path (str): Path to the folder containing documents
            
        Returns:
            List[Dict[str, Any]]: List of extracted data from all documents
        """
        folder = Path(folder_path)
        if not folder.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        
        # Landing AI supports various formats including PDF, images, and office documents
        supported_extensions = {
            '.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.gif', '.bmp',
            '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'
        }
        document_files = [
            file for file in folder.iterdir()
            if file.is_file() and file.suffix.lower() in supported_extensions
        ]
        
        if not document_files:
            self.logger.warning(f"No supported document files found in {folder_path}")
            return []
        
        self.logger.info(f"Found {len(document_files)} documents to process")
        
        all_extracted_data = []
        for file_path in document_files:
            self.logger.info(f"Processing: {file_path.name}")
            extracted_data = self.process_document(str(file_path))
            all_extracted_data.append(extracted_data)
        
        return all_extracted_data
    
    def generate_csv_with_ai(self, extracted_data: List[Dict[str, Any]], 
                           custom_prompt: Optional[str] = None,
                           use_google_ai: bool = False) -> pd.DataFrame:
        """
        You will be given official resort documents one by one. There are usually 3–6 documents per resort.

There are two types of documents:

Main Contract – Contains the core resort information, room details, meal plans, transfers, and general policies.

Package Document(s) – Contain special promotional packages and exclusive offers. These are only available to us and will be highlighted on our platform. This is the primary source for package details and rates.

🟡 Document Handling Rules
Wait until I say: “Let’s structure this resort” — only then should you extract and structure the data.

Do not summarize, reword, or paraphrase — extract all content exactly as written.

Maintain correct casing and punctuation from the documents.

If information is missing, mark it as: Not specified.

All data must be presented section by section, exactly in the format and field naming below.

Do not generate the CSV until I say: “Provide CSV”.
Once I say that, then:

Then break the message clearly with something like:
➡️ Now Generating CSV...

Then generate the CSV based on the structured data.

Each CSV section should be separate, as follows:

1. Resort_Details.csv – one row per resort.
2. Villas_Rooms.csv – one row per villa/room per resort.
3. Meal_Plans.csv – one row per meal plan per resort.
4. Transfers.csv – one row per transfer per resort.
5. Packages.csv – one row per package per resort.
6. Room_Rates.csv – one row per rate entry per room per resort.

🧾 Resort Data Format to Follow
1. 🏝 RESORT DETAILS
Resort Name: (ALL CAPS. If it’s a package, append ‘- PACKAGE’. Shorten only if it exceeds 40 characters.)

Resort Legal Name: (CamelCase)

Atoll:

Star Category:

Offer Type: (Keep this field for all resorts)

Resort Category: (Island Resort / City Hotel / Guest House)

Board Type: (Select the lowest meal board type provided by the resort, in this order. If not found, write 'Not specified')

markdown
Copy
Edit
1. Bed and breakfast (B/B)  
2. Half board (H/B)  
3. HB plus  
4. Full board (F/B)  
5. Fb plus  
6. Soft All Inclusive  
7. Basic All Inclusive  
8. Classic All Inclusive  
9. Al Gold  
10. Al plus  
11. Premium All Inclusive  
12. Platinum All Inclusive  
13. Deluxe all inclusive  
14. Extreme all inclusive  
15. Serenity plan  
16. Reserve plan  
17. Lobi plan  
18. Velassaru Indulgence  
19. The Milaidhoo Gourmet Plan  
20. Pure indulgence  
21. Indulgence plan  
22. Varu plan  
23. Kanifushi plan  
24. Fushi Plan  
25. RAAYA Plan  
26. Experience  
27. Anything Anytime Anywhere  
Marketplace: (Select from: Australia, Eastern Europe / CIS, Europe, Russia, Middle East, Africa, Asia, South America. If only a region is mentioned, assign ‘All’ countries under that region. If specific countries are listed, mention them.)

Booking Period - From: (Format: DD/MM/YYYY)

Booking Period - To: (Format: DD/MM/YYYY)

Age Definition:

Teenage From Age:

Child From Age: (If Infants are 0–1.99, Child From Age should be 2)

Early Check-In Cost: 0

Late Check-Out Cost: 0

Resort Details (Intro): (Limit to 3000 characters. Remove unnecessary repetition or generic text if longer.)

Resort Terms and Conditions: (Limit to 3000 characters)

Resort Cancellation Policy: (Limit to 3000 characters)

Other Additional Information:

2. 🛏 ROOM / VILLA DETAILS
(Repeat for each room/villa)

Resort Name:

Room Type:

No of Rooms / Villas:

Room / Villa Category:

Basic Occupancy Count:

Adult:

Teenage:

Child:

Maximum Occupancy (Including Basic):

Room Size (sqm):

Minimum Stay (Nights):

Bed Type:

Bed Count:

Room / Villa Description:

Facilities Provided:

Room Terms and Conditions:

3. 🍽 MEAL PLAN
(Repeat for each meal plan)

Resort Name:

Meal Plan:

Cost for Adult:

Cost for Child:

Meal Plan Inclusion Details:

If Included in a Package: (Mention package names or 'Not included')

4. 🚤 TRANSFER DETAILS
(Repeat for each transfer type)

Resort Name:

Transfer Name:

Transfer Type: (Select from options like Shared Seaplane, Private Luxury Yacht, etc.)

Valid Travel - From:

Valid Travel - To:

Transfer Cost:

Adult:

Child:

Included in Package(s):

Transfer Terms and Conditions:

5. 🎁 PACKAGE DETAILS
(Repeat for each package)

Resort Name:

Package Name:

Package Inclusion:

Apply Countries:

Package Period - From:

Package Period - To:

Booking Period - From:

Booking Period - To:

Blackout Periods:

Villa / Room Type:

Stay Duration (Nights):

Basic Occupancy Count:

Adult:

Teenage:

Child:

Maximum Occupancy (Including Basic):

Meal Plan:

Transfer:

Package Cost: (State per room or per person)

Package Value: (E.g., $2000)

Extra Person Rate per Night:

Adult:

Teenage:

Child:

6. 💰 ROOM / VILLA RATE
(Repeat for each rate)

Resort Name:

Ban Countries: (If any)

Room Type:

Rate Period - From:

Rate Period - To:

Rate Based On: (Per Room Per Night / Per Person Per Day)

Room Rate:

Extra Person Rate:

Adult:

Teenage:

Child:

⚠️ Special Notes
Honeymoon, Anniversary & Birthday Benefits must only be listed as part of a package if they are found within the package document. If they are only found in the main contract, do not list them as part of the package.

Repeatable fields (villas, transfers, packages) must be listed individually, not combined.

Do not generate any CSV or structured data until you receive the command: “Let’s structure this resort”, and then wait again until you are told: “Provide CSV”.

        """
        if not extracted_data:
            return pd.DataFrame()
        
        # Filter out failed documents
        successful_data = [doc for doc in extracted_data if doc.get('processing_status') == 'success']
        
        if not successful_data:
            self.logger.warning("No successfully processed documents found")
            return self._create_basic_dataframe(extracted_data)
        
        # Try to use Google AI Studio for additional AI processing if requested and API key is available
        if use_google_ai and os.getenv('GOOGLE_AI_STUDIO_API_KEY'):
            return self._generate_csv_with_google_ai(successful_data, custom_prompt)
        
        # Otherwise, create structured CSV from Landing AI extraction results
        return self._create_structured_dataframe(successful_data, custom_prompt)
    
    def _generate_csv_with_google_ai(self, extracted_data: List[Dict[str, Any]], 
                                   custom_prompt: Optional[str] = None) -> pd.DataFrame:
        """Generate CSV using Google AI Studio for additional processing."""
        try:
            import google.generativeai as genai
            
            # Configure Google AI Studio
            api_key = os.getenv('GOOGLE_AI_STUDIO_API_KEY')
            genai.configure(api_key=api_key)
            
            # Initialize the model
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Prepare data summary for Google AI
            documents_summary = []
            for doc_data in extracted_data:
                summary = {
                    'file_name': doc_data['file_name'],
                    'markdown': doc_data.get('markdown', '')[:2000] + '...' if len(doc_data.get('markdown', '')) > 2000 else doc_data.get('markdown', ''),
                    'entities': doc_data.get('entities', []),
                    'chunks_count': len(doc_data.get('chunks', []))
                }
                documents_summary.append(summary)
            
            # Default system prompt
            system_prompt = custom_prompt or """
You will be given official resort documents one by one. There are usually 3–6 documents per resort.

There are two types of documents:

Main Contract – Contains the core resort information, room details, meal plans, transfers, and general policies.

Package Document(s) – Contain special promotional packages and exclusive offers. These are only available to us and will be highlighted on our platform. This is the primary source for package details and rates.

🟡 Document Handling Rules
Wait until I say: “Let’s structure this resort” — only then should you extract and structure the data.

Do not summarize, reword, or paraphrase — extract all content exactly as written.

Maintain correct casing and punctuation from the documents.

If information is missing, mark it as: Not specified.

All data must be presented section by section, exactly in the format and field naming below.

Do not generate the CSV until I say: “Provide CSV”.
Once I say that, then:

Then break the message clearly with something like:
➡️ Now Generating CSV...

Then generate the CSV based on the structured data.

Each CSV section should be separate, as follows:

1. Resort_Details.csv – one row per resort.
2. Villas_Rooms.csv – one row per villa/room per resort.
3. Meal_Plans.csv – one row per meal plan per resort.
4. Transfers.csv – one row per transfer per resort.
5. Packages.csv – one row per package per resort.
6. Room_Rates.csv – one row per rate entry per room per resort.

🧾 Resort Data Format to Follow
1. 🏝 RESORT DETAILS
Resort Name: (ALL CAPS. If it’s a package, append ‘- PACKAGE’. Shorten only if it exceeds 40 characters.)

Resort Legal Name: (CamelCase)

Atoll:

Star Category:

Offer Type: (Keep this field for all resorts)

Resort Category: (Island Resort / City Hotel / Guest House)

Board Type: (Select the lowest meal board type provided by the resort, in this order. If not found, write 'Not specified')

markdown
Copy
Edit
1. Bed and breakfast (B/B)  
2. Half board (H/B)  
3. HB plus  
4. Full board (F/B)  
5. Fb plus  
6. Soft All Inclusive  
7. Basic All Inclusive  
8. Classic All Inclusive  
9. Al Gold  
10. Al plus  
11. Premium All Inclusive  
12. Platinum All Inclusive  
13. Deluxe all inclusive  
14. Extreme all inclusive  
15. Serenity plan  
16. Reserve plan  
17. Lobi plan  
18. Velassaru Indulgence  
19. The Milaidhoo Gourmet Plan  
20. Pure indulgence  
21. Indulgence plan  
22. Varu plan  
23. Kanifushi plan  
24. Fushi Plan  
25. RAAYA Plan  
26. Experience  
27. Anything Anytime Anywhere  
Marketplace: (Select from: Australia, Eastern Europe / CIS, Europe, Russia, Middle East, Africa, Asia, South America. If only a region is mentioned, assign ‘All’ countries under that region. If specific countries are listed, mention them.)

Booking Period - From: (Format: DD/MM/YYYY)

Booking Period - To: (Format: DD/MM/YYYY)

Age Definition:

Teenage From Age:

Child From Age: (If Infants are 0–1.99, Child From Age should be 2)

Early Check-In Cost: 0

Late Check-Out Cost: 0

Resort Details (Intro): (Limit to 3000 characters. Remove unnecessary repetition or generic text if longer.)

Resort Terms and Conditions: (Limit to 3000 characters)

Resort Cancellation Policy: (Limit to 3000 characters)

Other Additional Information:

2. 🛏 ROOM / VILLA DETAILS
(Repeat for each room/villa)

Resort Name:

Room Type:

No of Rooms / Villas:

Room / Villa Category:

Basic Occupancy Count:

Adult:

Teenage:

Child:

Maximum Occupancy (Including Basic):

Room Size (sqm):

Minimum Stay (Nights):

Bed Type:

Bed Count:

Room / Villa Description:

Facilities Provided:

Room Terms and Conditions:

3. 🍽 MEAL PLAN
(Repeat for each meal plan)

Resort Name:

Meal Plan:

Cost for Adult:

Cost for Child:

Meal Plan Inclusion Details:

If Included in a Package: (Mention package names or 'Not included')

4. 🚤 TRANSFER DETAILS
(Repeat for each transfer type)

Resort Name:

Transfer Name:

Transfer Type: (Select from options like Shared Seaplane, Private Luxury Yacht, etc.)

Valid Travel - From:

Valid Travel - To:

Transfer Cost:

Adult:

Child:

Included in Package(s):

Transfer Terms and Conditions:

5. 🎁 PACKAGE DETAILS
(Repeat for each package)

Resort Name:

Package Name:

Package Inclusion:

Apply Countries:

Package Period - From:

Package Period - To:

Booking Period - From:

Booking Period - To:

Blackout Periods:

Villa / Room Type:

Stay Duration (Nights):

Basic Occupancy Count:

Adult:

Teenage:

Child:

Maximum Occupancy (Including Basic):

Meal Plan:

Transfer:

Package Cost: (State per room or per person)

Package Value: (E.g., $2000)

Extra Person Rate per Night:

Adult:

Teenage:

Child:

6. 💰 ROOM / VILLA RATE
(Repeat for each rate)

Resort Name:

Ban Countries: (If any)

Room Type:

Rate Period - From:

Rate Period - To:

Rate Based On: (Per Room Per Night / Per Person Per Day)

Room Rate:

Extra Person Rate:

Adult:

Teenage:

Child:

⚠️ Special Notes
Honeymoon, Anniversary & Birthday Benefits must only be listed as part of a package if they are found within the package document. If they are only found in the main contract, do not list them as part of the package.

Repeatable fields (villas, transfers, packages) must be listed individually, not combined.

Do not generate any CSV or structured data until you receive the command: “Let’s structure this resort”, and then wait again until you are told: “Provide CSV”.

            """
            
            # Prepare the prompt
            user_prompt = f"""
Let's structure this resort data. Here is the extracted data from {len(documents_summary)} documents:

{json.dumps(documents_summary, indent=2)}

Provide CSV data now. Extract package information and return ONLY the CSV content with the exact headers specified in the system prompt.
            """
            
            # Combine system and user prompts
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Generate response using Google AI Studio
            response = model.generate_content(full_prompt)
            
            # Parse the AI response
            ai_response = response.text
            
            # Try to extract CSV from the response
            # Look for CSV content (should start with headers)
            lines = ai_response.strip().split('\n')
            csv_lines = []
            
            # Find the start of CSV data (look for line with commas that could be headers)
            csv_started = False
            for line in lines:
                if not csv_started:
                    # Check if this looks like a CSV header line
                    if ',' in line and ('Resort Name' in line or 'Package Name' in line):
                        csv_started = True
                        csv_lines.append(line)
                else:
                    # Continue collecting CSV lines
                    if ',' in line and line.strip():
                        csv_lines.append(line)
                    elif not line.strip():
                        continue  # Skip empty lines
                    else:
                        break  # Stop at non-CSV content
            
            if csv_lines:
                # Create DataFrame from CSV lines
                from io import StringIO
                csv_content = '\n'.join(csv_lines)
                df = pd.read_csv(StringIO(csv_content))
                self.logger.info(f"Generated CSV data with Google AI: {len(df)} rows and {len(df.columns)} columns")
                return df
            else:
                self.logger.error("Could not extract valid CSV from Google AI response")
                return self._create_structured_dataframe(extracted_data)
                
        except Exception as e:
            self.logger.error(f"Error generating CSV with Google AI: {e}")
            return self._create_structured_dataframe(extracted_data)
    
    def _create_structured_dataframe(self, extracted_data: List[Dict[str, Any]], 
                                   custom_prompt: Optional[str] = None) -> pd.DataFrame:
        """Create structured DataFrame from Landing AI extraction results."""
        structured_data = []
        
        for doc_data in extracted_data:
            # Base row data
            row = {
                'file_name': doc_data['file_name'],
                'processing_status': doc_data.get('processing_status', 'success'),
                'content_length': len(doc_data.get('markdown', '')),
                'chunks_count': len(doc_data.get('chunks', [])),
                'entities_count': len(doc_data.get('entities', [])),
                'tables_count': len(doc_data.get('tables', []))
            }
            
            # Extract common entities
            entities = doc_data.get('entities', [])
            
            # Look for common entity types
            names = [e['content'] for e in entities if e['type'] in ['name', 'person']]
            dates = [e['content'] for e in entities if e['type'] in ['date', 'time']]
            amounts = [e['content'] for e in entities if e['type'] in ['amount', 'money', 'price']]
            addresses = [e['content'] for e in entities if e['type'] in ['address', 'location']]
            
            row.update({
                'names': '; '.join(names) if names else '',
                'dates': '; '.join(dates) if dates else '',
                'amounts': '; '.join(amounts) if amounts else '',
                'addresses': '; '.join(addresses) if addresses else '',
            })
            
            # Extract key information from markdown content
            markdown = doc_data.get('markdown', '')
            if markdown:
                # Look for patterns in markdown
                lines = markdown.split('\n')
                key_lines = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
                
                row['first_line'] = key_lines[0] if key_lines else ''
                row['content_preview'] = ' '.join(key_lines[:3])[:200] + '...' if len(' '.join(key_lines[:3])) > 200 else ' '.join(key_lines[:3])
            
            # Add result path if available
            if doc_data.get('result_path'):
                row['result_file'] = doc_data['result_path']
            
            structured_data.append(row)
        
        df = pd.DataFrame(structured_data)
        self.logger.info(f"Generated structured CSV data: {len(df)} rows and {len(df.columns)} columns")
        return df
    
    def _create_basic_dataframe(self, extracted_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Create a basic DataFrame as fallback when processing fails."""
        basic_data = []
        
        for doc_data in extracted_data:
            if 'error' in doc_data:
                row = {
                    'file_name': doc_data['file_name'],
                    'status': 'Error',
                    'error_message': doc_data['error']
                }
            else:
                row = {
                    'file_name': doc_data['file_name'],
                    'status': doc_data.get('processing_status', 'Unknown'),
                    'content_available': 'Yes' if doc_data.get('markdown') else 'No'
                }
            
            basic_data.append(row)
        
        return pd.DataFrame(basic_data)
    
    def save_to_csv(self, df: pd.DataFrame, output_path: str = None) -> str:
        """
        Save DataFrame to CSV file.
        
        Args:
            df (pd.DataFrame): DataFrame to save
            output_path (str, optional): Output file path
            
        Returns:
            str: Path to the saved CSV file
        """
        if output_path is None:
            output_path = os.getenv('OUTPUT_CSV_FILE', 'extracted_data.csv')
        
        # Ensure the output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save to CSV
        df.to_csv(output_path, index=False, encoding='utf-8')
        self.logger.info(f"CSV file saved to: {output_path}")
        
        return output_path
    
    def run_extraction(self, documents_folder: str = None, 
                      output_csv: str = None, 
                      custom_prompt: str = None,
                      use_google_ai: bool = False) -> str:
        """
        Run the complete extraction pipeline.
        
        Args:
            documents_folder (str, optional): Path to documents folder
            output_csv (str, optional): Output CSV file path
            custom_prompt (str, optional): Custom prompt for AI processing
            use_google_ai (bool): Whether to use Google AI Studio for additional processing
            
        Returns:
            str: Path to the generated CSV file
        """
        if documents_folder is None:
            documents_folder = os.getenv('DOCUMENTS_FOLDER', 'input')
        
        self.logger.info(f"Starting document extraction from: {documents_folder}")
        
        # Process all documents
        extracted_data = self.process_folder(documents_folder)
        
        if not extracted_data:
            self.logger.warning("No documents were processed successfully")
            return None
        
        # Generate CSV
        df = self.generate_csv_with_ai(extracted_data, custom_prompt, use_google_ai)
        
        # Save to CSV
        csv_path = self.save_to_csv(df, output_csv)
        
        self.logger.info("Document extraction pipeline completed successfully")
        return csv_path


def main():
    """Main function to run the document extraction."""
    try:
        # Initialize the extractor
        extractor = DocumentDataExtractor()
        
        # Run the extraction
        csv_path = extractor.run_extraction()
        
        if csv_path:
            print(f"✅ Extraction completed successfully!")
            print(f"📁 CSV file saved to: {csv_path}")
            print(f"📋 You can now copy-paste this data into Google Sheets")
        else:
            print("❌ No documents were processed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        logging.error(f"Main execution error: {e}")


if __name__ == "__main__":
    main()
