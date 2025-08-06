#!/usr/bin/env python3
"""
Test script to demonstrate the final multi-CSV document extraction system
using extracted data from our working system.
"""

import json
import os
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_csv_with_ai(document_text, csv_config, api_key):
    """Generate CSV using AI with specific configuration"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
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
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        print(f"Error generating CSV: {str(e)}")
        return None

def test_multi_csv_generation():
    """Test the multi-CSV generation using extracted data"""
    
    # Load the extracted data
    extraction_file = Path("extraction_results/example-input_20250806_161339.json")
    
    if not extraction_file.exists():
        print(f"❌ Extraction file not found: {extraction_file}")
        return
    
    with open(extraction_file, 'r', encoding='utf-8') as f:
        extraction_data = json.load(f)
    
    document_text = extraction_data.get('markdown', '')
    
    if not document_text:
        print("❌ No document text found in extraction data")
        return
    
    # CSV configurations for all 6 types
    csv_configs = {
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
    
    # Get API key
    api_key = os.getenv('GOOGLE_AI_STUDIO_API_KEY')
    if not api_key:
        print("❌ GOOGLE_AI_STUDIO_API_KEY not found in environment variables")
        return
    
    # Create output directory
    output_dir = Path("output/test-resort-final")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🚀 Testing Multi-CSV Generation System")
    print(f"📄 Using extracted data from: {extraction_file}")
    print(f"📁 Output directory: {output_dir}")
    print("=" * 60)
    
    successful_csvs = 0
    
    # Generate each CSV type
    for csv_name, config in csv_configs.items():
        print(f"📊 Generating {csv_name}.csv...")
        
        csv_content = generate_csv_with_ai(document_text, config, api_key)
        
        if csv_content:
            # Save CSV file
            csv_file = output_dir / f"{csv_name}.csv"
            
            try:
                with open(csv_file, 'w', encoding='utf-8') as f:
                    f.write(csv_content)
                
                # Count lines for verification
                lines = csv_content.split('\n')
                data_rows = len([line for line in lines if line.strip()]) - 1  # Exclude header
                
                print(f"   ✅ Generated successfully: {data_rows} data rows")
                successful_csvs += 1
                
            except Exception as e:
                print(f"   ❌ Failed to save file: {str(e)}")
        else:
            print(f"   ❌ Failed to generate content")
    
    print("=" * 60)
    print(f"📊 Generation Summary:")
    print(f"   📄 Total CSV types: {len(csv_configs)}")
    print(f"   ✅ Successful generations: {successful_csvs}")
    print(f"   ❌ Failed generations: {len(csv_configs) - successful_csvs}")
    print(f"   📁 Output folder: {output_dir}")
    
    if successful_csvs == len(csv_configs):
        print("🎉 All CSV files generated successfully!")
    else:
        print("⚠️  Some CSV files failed to generate.")
    
    # List generated files
    print("\n📁 Generated files:")
    for file in sorted(output_dir.glob("*.csv")):
        file_size = file.stat().st_size
        print(f"   📄 {file.name} ({file_size:,} bytes)")

if __name__ == "__main__":
    test_multi_csv_generation()
