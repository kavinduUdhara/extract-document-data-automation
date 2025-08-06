"""
Test Enhanced Multi-CSV Generation using existing extraction results
"""

import os
import json
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv


def generate_multiple_csv_from_existing_data():
    """Generate multiple CSV files from existing extraction results."""
    
    # Load environment variables
    load_dotenv()
    google_ai_api_key = os.getenv('GOOGLE_AI_STUDIO_API_KEY')
    
    if not google_ai_api_key:
        print("❌ GOOGLE_AI_STUDIO_API_KEY not found")
        return
    
    # Configure Google AI
    genai.configure(api_key=google_ai_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Read existing extraction result
    extraction_files = list(Path("extraction_results").glob("*.json"))
    if not extraction_files:
        print("❌ No extraction results found")
        return
    
    # Use the most recent extraction file
    latest_file = max(extraction_files, key=lambda x: x.stat().st_mtime)
    print(f"📄 Using extraction file: {latest_file.name}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        extraction_data = json.load(f)
    
    # Get the markdown text
    markdown_text = extraction_data.get('markdown', '')
    
    # Create output folder for example-input
    output_folder = Path("output/example-input")
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Define CSV types and their prompts
    csv_configs = {
        "Resort_Details": {
            "headers": "Resort Name,Resort Legal Name,Atoll,Star Category,Offer Type,Resort Category,Board Type,Marketplace,Booking Period - From,Booking Period - To,Age Definition,Teenage From Age,Child From Age,Early Check-In Cost,Late Check-Out Cost,Resort Details (Intro),Resort Terms and Conditions,Resort Cancellation Policy,Other Additional Information",
            "instructions": "Extract resort information. Resort Name: ALL CAPS, append '- PACKAGE'. Board Type: lowest meal type. Marketplace: target countries/regions."
        },
        
        "Villas_Rooms": {
            "headers": "Resort Name,Room Type,No of Rooms / Villas,Room / Villa Category,Basic Occupancy Count: Adult,Basic Occupancy Count: Teenage,Basic Occupancy Count: Child,Maximum Occupancy (Including Basic),Room Size (sqm),Minimum Stay (Nights),Bed Type,Bed Count,Room / Villa Description,Facilities Provided,Room Terms and Conditions",
            "instructions": "Extract room/villa details. One row per room type. Include occupancy details and room descriptions."
        },
        
        "Meal_Plans": {
            "headers": "Resort Name,Meal Plan,Cost for Adult,Cost for Child,Meal Plan Inclusion Details,If Included in a Package",
            "instructions": "Extract meal plan information. Include costs and detailed descriptions of what's included."
        },
        
        "Transfers": {
            "headers": "Resort Name,Transfer Name,Transfer Type,Valid Travel - From,Valid Travel - To,Transfer Cost: Adult,Transfer Cost: Child,Included in Package(s),Transfer Terms and Conditions",
            "instructions": "Extract transfer details. Include seaplane, domestic flights, speedboat transfers with costs."
        },
        
        "Packages": {
            "headers": "Resort Name,Package Name,Package Inclusion,Apply Countries,Package Period - From,Package Period - To,Booking Period - From,Booking Period - To,Blackout Periods,Villa / Room Type,Stay Duration (Nights),Basic Occupancy Count: Adult,Basic Occupancy Count: Teenage,Basic Occupancy Count: Child,Maximum Occupancy (Including Basic),Meal Plan,Transfer,Package Cost,Package Value,Extra Person Rate per Night: Adult,Extra Person Rate per Night: Teenage,Extra Person Rate per Night: Child",
            "instructions": "CRITICAL: Create separate rows for EACH combination of room type × season × transfer type. Extract ALL package combinations from rate tables."
        },
        
        "Room_Rates": {
            "headers": "Resort Name,Ban Countries,Room Type,Rate Period - From,Rate Period - To,Rate Based On,Room Rate,Extra Person Rate: Adult,Extra Person Rate: Teenage,Extra Person Rate: Child",
            "instructions": "Extract room rates by season and room type. Include any country restrictions."
        }
    }
    
    print(f"📝 Generating {len(csv_configs)} CSV files...")
    
    # Generate each CSV file
    for csv_name, config in csv_configs.items():
        try:
            prompt = f"""
You are processing resort documents. Extract {csv_name.replace('_', ' ').lower()} data and create a CSV with these exact headers:
{config['headers']}

Instructions: {config['instructions']}

IMPORTANT: 
- Return ONLY the CSV data with headers, no other text or explanations
- If information is missing, use 'Not specified'
- Extract exactly as written from documents
- For dates, use DD/MM/YYYY format
- Don't summarize or paraphrase

Document text to extract from:
{markdown_text[:20000]}
            """
            
            response = model.generate_content(prompt)
            csv_content = response.text.strip()
            
            # Clean up response
            if csv_content.startswith("```"):
                lines = csv_content.split("\n")
                csv_content = "\n".join(lines[1:-1])
            
            # Save CSV file
            if csv_content and csv_content.strip():
                csv_path = output_folder / f"{csv_name}.csv"
                with open(csv_path, 'w', encoding='utf-8') as f:
                    f.write(csv_content)
                print(f"  ✅ Generated: {csv_name}.csv")
            else:
                print(f"  ⚠️ No data generated for: {csv_name}")
                
        except Exception as e:
            print(f"  ❌ Error generating {csv_name}: {str(e)}")
    
    print(f"\n🎉 All CSV files saved in: {output_folder}")


if __name__ == "__main__":
    generate_multiple_csv_from_existing_data()
