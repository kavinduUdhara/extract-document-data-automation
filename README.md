# Document Data Extractor with Landing AI

A Python module that automatically extracts data from documents using Landing AI's Agentic Document Extraction and generates CSV files ready for Google Sheets.

## Features

- 🔍 **Advanced Document Processing**: Supports PDF, images, and Office documents  
- 🤖 **AI-Powered Extraction**: Uses Landing AI's state-of-the-art document understanding
- 📊 **Smart CSV Generation**: Creates structured, consistent CSV output
- 📋 **Google Sheets Ready**: Generated CSV can be directly imported
- 🔧 **Optional Enhancement**: OpenAI integration for custom data structuring
- 📁 **Batch Processing**: Process entire folders of documents at once
- 💰 **Cost-Effective**: Pay-per-use pricing, no complex cloud setup

## Supported Document Types

- 📄 PDF documents
- 🖼️ Images (JPEG, PNG, TIFF, GIF, BMP)
- 📋 Office documents (Word, Excel, PowerPoint)
- 📝 Text files
- 🧾 Receipts and invoices
- 💼 Business cards
- 📜 Forms and contracts
- 📊 Financial statements

## Why Landing AI?

✅ **No Complex Setup**: Just get an API key and start extracting  
✅ **Superior Accuracy**: State-of-the-art document understanding  
✅ **Wide Format Support**: PDF, images, Office docs, and more  
✅ **Cost-Effective**: Pay only for what you use  
✅ **Fast Processing**: Quick turnaround times  
✅ **Structured Output**: Both markdown and JSON formats  

## Quick Start

### 1. Installation

```bash
# Clone or download this repository
git clone <repository-url>
cd extract-document-data-automation

# Install dependencies
pip install -r requirements.txt
```

### 2. Get Your API Key

1. Go to [Landing AI](https://landing.ai/)
2. Sign up for an account
3. Get your Vision Agent API key from the dashboard

### 3. Configuration

Copy the example environment file and add your API key:
```bash
cp .env.example .env
```

Edit `.env` with your API key:
```env
# Required
VISION_AGENT_API_KEY=your-landing-ai-api-key

# Optional (for enhanced AI processing)
OPENAI_API_KEY=your-openai-api-key

# Configuration
DOCUMENTS_FOLDER=documents
OUTPUT_CSV_FILE=extracted_data.csv
RESULTS_SAVE_DIR=extraction_results
```

### 4. Add Documents

Place your documents in the `documents` folder:
```
documents/
├── invoice1.pdf
├── receipt1.jpg
├── business_card.png
├── contract.docx
└── spreadsheet.xlsx
```

### 5. Run Extraction

```bash
# Basic usage
python document_extractor.py

# Or try the demo
python demo.py

# Or run examples
python examples.py
```

## Usage Examples

### Basic Usage

```python
from document_extractor import DocumentDataExtractor

# Initialize the extractor
extractor = DocumentDataExtractor()

# Run extraction with default settings
csv_path = extractor.run_extraction()
print(f"CSV generated: {csv_path}")
```

### Custom Folder and Output

```python
# Specify custom paths
csv_path = extractor.run_extraction(
    documents_folder="my_documents",
    output_csv="output/my_data.csv"
)
```

### Enhanced Processing with OpenAI

```python
# Use OpenAI for advanced CSV structuring
invoice_prompt = """
Extract invoice information and create a CSV with these columns:
- file_name, invoice_number, date, vendor_name, total_amount, 
  currency, customer_name, description, status

For missing information, use "N/A".
Return a JSON array where each object represents one invoice.
"""

csv_path = extractor.run_extraction(
    custom_prompt=invoice_prompt,
    use_openai=True  # Requires OPENAI_API_KEY
)
```

### Process Single Document

```python
# Process individual document
result = extractor.process_document("path/to/document.pdf")

# Access extracted content
print("Markdown content:", result['markdown'])
print("Structured chunks:", result['chunks'])
print("Entities found:", result['entities'])
```

## Document Type Examples

The `examples.py` file contains specialized examples for:

- **Invoices**: Extract invoice numbers, amounts, vendors, dates
- **Receipts**: Extract merchant info, purchase details, amounts  
- **Business Cards**: Extract contact information
- **Office Documents**: Extract structured data from Word, Excel, PowerPoint
- **General Documents**: Extract any text and structured content

## Verification

Verify your setup is correct:
```bash
python validate.py
```

This will check:
- API key configuration
- Dependencies installation
- Document folder setup
- Landing AI API access

## Project Structure

```
extract-document-data-automation/
├── document_extractor.py     # Main extraction module
├── examples.py              # Usage examples for different document types
├── demo.py                  # Quick start demonstration
├── validate.py              # Setup validation script
├── setup.py                 # Setup guide
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .env                    # Your environment variables (create this)
├── documents/              # Input documents folder
├── extraction_results/     # Detailed extraction results (auto-created)
├── output/                 # Generated CSV files (auto-created)
└── README.md              # This file
```

## Output

The extractor generates two types of output:

### 1. CSV Files
Structured data ready for Google Sheets with columns like:
- **Document metadata**: File names, processing status
- **Extracted entities**: Names, dates, amounts, addresses
- **Content summaries**: Key information from documents
- **Custom fields**: Based on your prompts (with OpenAI)

### 2. Detailed Results (JSON)
Saved in `extraction_results/` folder:
- Full markdown content
- Structured data chunks
- Entity recognition results
- Raw extraction data

## Google Sheets Integration

Import your generated CSV files into Google Sheets:

1. **File Upload Method:**
   - Open Google Sheets
   - Go to File > Import
   - Upload your CSV file
   - Choose import options

2. **Copy-Paste Method:**
   - Open the CSV file in a text editor
   - Copy the content
   - Paste directly into Google Sheets

## Error Handling

The module includes comprehensive error handling:

- **Individual Document Failures**: Continue processing other documents
- **API Errors**: Clear error messages and fallback options
- **Authentication Issues**: Helpful setup guidance
- **File Format Issues**: Skip unsupported files with warnings

## Cost Considerations

### Landing AI
- Pay-per-document pricing
- No monthly minimums
- Free tier often available
- Monitor usage in your dashboard

### OpenAI (Optional)
- Pay-per-API call for enhanced processing
- Only used when `use_openai=True`
- Can be skipped for basic extraction

## Troubleshooting

### Common Issues

1. **API Key Error**
   - Verify your Landing AI API key in `.env`
   - Check your account status and credits

2. **No Documents Processed**
   - Ensure documents are in supported formats
   - Check the documents folder path

3. **Import Errors**
   - Run: `pip install -r requirements.txt`
   - Ensure Python 3.8+ is installed

4. **Empty CSV Results**
   - Check document quality (clear, readable text)
   - Try with different document formats

### Getting Help

1. Run the validation: `python validate.py`
2. Check detailed logs in the console output
3. Review extraction results in `extraction_results/` folder
4. Test with sample documents first

## Comparison: Landing AI vs Google Cloud

| Feature | Landing AI | Google Cloud |
|---------|------------|--------------|
| Setup Complexity | ⭐ Simple API key | ⭐⭐⭐ Complex service accounts |
| Cost Structure | Pay-per-use | Pay-per-page + infrastructure |
| Document Types | PDF, Images, Office docs | Mainly PDF and images |
| Accuracy | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Very good |
| Integration | ⭐⭐⭐⭐⭐ Simple Python API | ⭐⭐⭐ Complex SDK |
| Maintenance | ⭐⭐⭐⭐⭐ Minimal | ⭐⭐ Regular updates needed |

## Advanced Features

### Batch Processing with Custom Prompts

```python
# Process different document types with specialized prompts
business_card_prompt = """
Extract contact information: name, title, company, email, phone, address
"""

receipt_prompt = """
Extract purchase data: merchant, date, total, items, payment_method
"""

# Process different folders with different prompts
contacts_csv = extractor.run_extraction(
    documents_folder="business_cards",
    output_csv="contacts.csv",
    custom_prompt=business_card_prompt,
    use_openai=True
)

expenses_csv = extractor.run_extraction(
    documents_folder="receipts", 
    output_csv="expenses.csv",
    custom_prompt=receipt_prompt,
    use_openai=True
)
```

### Integration with Other Tools

The generated CSV files can be easily integrated with:
- **Google Sheets**: Direct import
- **Excel**: Open CSV files directly
- **Database systems**: Import CSV data
- **Business intelligence tools**: Use as data source
- **Automation tools**: Process with scripts

## Security

- Keep your API keys secure and private
- Don't commit `.env` file to version control
- Monitor API usage in your Landing AI dashboard
- Consider data privacy when processing sensitive documents

## License

This project is provided as-is for educational and commercial use. Please review Landing AI's terms of service for API usage.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this tool.

---

🚀 **Ready to extract data from your documents? Get your Landing AI API key and start processing!**

**Need help?** Run `python validate.py` to check your setup.