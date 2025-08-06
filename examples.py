#!/usr/bin/env python3
"""
Example usage script for the Document Data Extractor using Landing AI.
This script demonstrates different ways to use the DocumentDataExtractor cla    csv_path = extractor.run_extraction(
        documents_folder="receipts",
        output_csv="purchases.csv",
        custom_prompt=receipt_prompt,
        use_google_ai=True
    )""

import os
from document_extractor import DocumentDataExtractor

def example_basic_usage():
    """Basic usage example."""
    print("=== Basic Usage Example ===")
    
    # Initialize the extractor
    extractor = DocumentDataExtractor()
    
    # Run extraction with default settings
    csv_path = extractor.run_extraction()
    
    if csv_path:
        print(f"✅ CSV generated: {csv_path}")
    else:
        print("❌ No documents processed")

def example_custom_folder_and_output():
    """Example with custom folder and output paths."""
    print("\n=== Custom Paths Example ===")
    
    extractor = DocumentDataExtractor()
    
    # Specify custom paths
    documents_folder = "my_documents"
    output_csv = "output/my_extracted_data.csv"
    
    csv_path = extractor.run_extraction(
        documents_folder=documents_folder,
        output_csv=output_csv
    )
    
    if csv_path:
        print(f"✅ CSV generated: {csv_path}")

def example_with_google_ai_processing():
    """Example using Google AI Studio for additional AI processing."""
    print("\n=== Google AI Studio Enhanced Processing Example ===")
    
    extractor = DocumentDataExtractor()
    
    # Custom prompt for invoice processing with Google AI enhancement
    invoice_prompt = """
    You are analyzing invoice documents extracted by Landing AI. Create a CSV with these columns:
    
    Required columns:
    - file_name: Name of the document file
    - invoice_number: Invoice or document number
    - date: Invoice date (format: YYYY-MM-DD)
    - vendor_name: Name of the vendor/supplier
    - total_amount: Total amount (extract numbers only)
    - currency: Currency symbol or code
    - customer_name: Customer or bill-to name
    - description: Brief description of goods/services
    - status: Processing status
    
    Extract information from the markdown content and entities.
    For missing information, use "N/A" as the value.
    Return a JSON array where each object represents one invoice row.
    """
    
    csv_path = extractor.run_extraction(
        custom_prompt=invoice_prompt,
        use_google_ai=True  # Enable Google AI Studio processing
    )
    
    if csv_path:
        print(f"✅ Enhanced invoice CSV generated: {csv_path}")

def example_step_by_step():
    """Example showing step-by-step processing."""
    print("\n=== Step-by-Step Processing Example ===")
    
    extractor = DocumentDataExtractor()
    
    # Step 1: Process documents
    documents_folder = "documents"
    print(f"Processing documents from: {documents_folder}")
    extracted_data = extractor.process_folder(documents_folder)
    print(f"Processed {len(extracted_data)} documents")
    
    # Show some details about extracted data
    for i, doc_data in enumerate(extracted_data[:3]):  # Show first 3
        print(f"  Document {i+1}: {doc_data['file_name']}")
        print(f"    Status: {doc_data.get('processing_status', 'Unknown')}")
        if 'markdown' in doc_data:
            print(f"    Content length: {len(doc_data['markdown'])} characters")
        if 'entities' in doc_data:
            print(f"    Entities found: {len(doc_data['entities'])}")
    
    # Step 2: Generate CSV
    print("\nGenerating structured data...")
    df = extractor.generate_csv_with_ai(extracted_data)
    print(f"Generated DataFrame with {len(df)} rows and {len(df.columns)} columns")
    print("Columns:", list(df.columns))
    
    # Step 3: Save to CSV
    csv_path = extractor.save_to_csv(df, "step_by_step_output.csv")
    print(f"✅ Saved to: {csv_path}")
    
    # Optional: Display preview
    print("\nPreview of generated data:")
    print(df.head())

def example_business_cards():
    """Example for processing business cards."""
    print("\n=== Business Cards Processing Example ===")
    
    extractor = DocumentDataExtractor()
    
    business_card_prompt = """
    You are analyzing business card documents extracted by Landing AI. Extract contact information and create a CSV with these columns:
    
    Required columns:
    - file_name: Name of the document file
    - full_name: Person's full name
    - job_title: Job title or position
    - company_name: Company name
    - email: Email address
    - phone: Phone number
    - mobile: Mobile phone number
    - address: Business address
    - website: Website URL
    - linkedin: LinkedIn profile (if mentioned)
    - notes: Any additional information
    
    Extract information from the markdown content and entities provided by Landing AI.
    For missing information, use "N/A" as the value.
    Clean and format phone numbers consistently.
    Return a JSON array where each object represents one business card.
    """
    
    csv_path = extractor.run_extraction(
        documents_folder="business_cards",
        output_csv="contacts.csv",
        custom_prompt=business_card_prompt,
        use_google_ai=True
    )
    
    if csv_path:
        print(f"✅ Business cards CSV generated: {csv_path}")

def example_receipts():
    """Example for processing receipts."""
    print("\n=== Receipts Processing Example ===")
    
    extractor = DocumentDataExtractor()
    
    receipt_prompt = """
    You are analyzing receipt documents extracted by Landing AI. Extract purchase information and create a CSV with these columns:
    
    Required columns:
    - file_name: Name of the document file
    - merchant_name: Store/merchant name
    - date: Purchase date (format: YYYY-MM-DD)
    - time: Purchase time
    - total_amount: Total amount paid
    - tax_amount: Tax amount (if separate)
    - payment_method: Payment method (cash, card, etc.)
    - receipt_number: Receipt or transaction number
    - items_count: Number of items purchased
    - category: Type of purchase (grocery, restaurant, retail, etc.)
    - location: Store location or address
    
    Extract information from the markdown content and entities provided by Landing AI.
    For missing information, use "N/A" as the value.
    Standardize date format to YYYY-MM-DD.
    Return a JSON array where each object represents one receipt.
    """
    
    csv_path = extractor.run_extraction(
        documents_folder="receipts",
        output_csv="expenses.csv",
        custom_prompt=receipt_prompt,
        use_openai=True
    )
    
    if csv_path:
        print(f"✅ Receipts CSV generated: {csv_path}")

def example_without_openai():
    """Example showing extraction without OpenAI (Landing AI only)."""
    print("\n=== Landing AI Only (No OpenAI) Example ===")
    
    extractor = DocumentDataExtractor()
    
    # Process with just Landing AI extraction
    csv_path = extractor.run_extraction(use_openai=False)
    
    if csv_path:
        print(f"✅ CSV generated using Landing AI only: {csv_path}")
        print("This approach uses the structured data directly from Landing AI")

def example_single_document():
    """Example for processing a single document."""
    print("\n=== Single Document Processing Example ===")
    
    extractor = DocumentDataExtractor()
    
    # Process a single document (replace with your document path)
    document_path = "documents/sample.pdf"  # Update this path
    
    if os.path.exists(document_path):
        print(f"Processing single document: {document_path}")
        
        # Process the document
        result = extractor.process_document(document_path)
        
        print(f"Processing status: {result.get('processing_status', 'Unknown')}")
        if 'markdown' in result:
            print(f"Extracted content preview:")
            print(result['markdown'][:300] + "..." if len(result['markdown']) > 300 else result['markdown'])
        
        if result.get('result_path'):
            print(f"Detailed results saved to: {result['result_path']}")
    else:
        print(f"Document not found: {document_path}")
        print("Please add a document to the documents folder first")

if __name__ == "__main__":
    print("Document Data Extractor - Usage Examples (Landing AI)")
    print("=" * 60)
    
    # Run different examples
    try:
        # Uncomment the examples you want to run:
        
        example_basic_usage()
        # example_custom_folder_and_output()
        # example_with_openai_processing()
        # example_step_by_step()
        # example_business_cards()
        # example_receipts()
        # example_without_openai()
        # example_single_document()
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        print("Make sure you have:")
        print("1. Set up your .env file with VISION_AGENT_API_KEY")
        print("2. Created a 'documents' folder with sample documents")
        print("3. Installed all required dependencies: pip install -r requirements.txt")
