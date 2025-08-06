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
        Process extracted data and generate structured CSV data.
        
        Args:
            extracted_data (List[Dict[str, Any]]): Extracted document data
            custom_prompt (Optional[str]): Custom prompt for AI processing
            use_google_ai (bool): Whether to use Google AI Studio for additional processing
            
        Returns:
            pd.DataFrame: Structured data ready for CSV export
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
            You are an expert data analyst. Analyze the provided document data extracted by Landing AI and create a structured CSV format.
            
            Your task:
            1. Analyze all the extracted document data
            2. Identify common fields and patterns across documents
            3. Create a consistent CSV structure with appropriate column headers
            4. Extract and organize the most relevant information
            5. Handle missing data appropriately
            6. Return the data in a JSON format that can be easily converted to CSV
            
            Focus on extracting:
            - Document metadata (file name, type, etc.)
            - Key entities (names, dates, amounts, addresses, etc.)
            - Important information from the markdown content
            - Any structured data
            
            Return a JSON array where each object represents a row in the CSV.
            Make sure all objects have the same keys (columns).
            """
            
            # Prepare the prompt
            user_prompt = f"""
            Here is the extracted data from {len(documents_summary)} documents:
            
            {json.dumps(documents_summary, indent=2)}
            
            Please analyze this data and return a structured JSON array suitable for CSV conversion.
            Ensure consistent column names across all rows.
            """
            
            # Combine system and user prompts
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Generate response using Google AI Studio
            response = model.generate_content(full_prompt)
            
            # Parse the AI response
            ai_response = response.text
            
            # Try to extract JSON from the response
            json_start = ai_response.find('[')
            json_end = ai_response.rfind(']') + 1
            
            if json_start != -1 and json_end != -1:
                json_data = ai_response[json_start:json_end]
                structured_data = json.loads(json_data)
                
                # Convert to DataFrame
                df = pd.DataFrame(structured_data)
                self.logger.info(f"Generated CSV data with Google AI: {len(df)} rows and {len(df.columns)} columns")
                return df
            else:
                self.logger.error("Could not extract valid JSON from Google AI response")
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
            documents_folder = os.getenv('DOCUMENTS_FOLDER', 'documents')
        
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
