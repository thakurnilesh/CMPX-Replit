import argparse
import json
import sys
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
from excel_parser import ExcelParser
from json_generator import JSONGenerator
from api_client import APIClient

def main():
    print("Excel to API Tool")
    print("=================\n")
    
    # Get the Excel file path
    excel_file = input("Enter the path to the Excel file: ")
    
    try:
        # Parse Excel file
        print(f"Reading Excel file: {excel_file}")
        parser = ExcelParser(excel_file)
        excel_data = parser.parse()
        
        # Generate JSON payload
        print("Generating JSON payload...")
        generator = JSONGenerator(excel_data)
        payload = generator.generate()
        
        # Display the generated JSON for verification
        print("\nGenerated JSON Payload:")
        print(json.dumps(payload, indent=4))
        
        # Confirm with user
        confirm = input("\nDo you want to submit this payload to the API? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Operation cancelled by user.")
            return
        
        # Get API details
        api_endpoint = input("\nEnter the API endpoint URL: ")
        username = input("Enter username for Basic Auth: ")
        password = input("Enter password for Basic Auth: ")
        
        # Make API call
        print("\nSending API request...")
        api_client = APIClient(api_endpoint, username, password)
        response = api_client.post_data(payload)
        
        # Display response
        print("\nAPI Response:")
        print(f"Status Code: {response.status_code}")
        print("Response Body:")
        try:
            print(json.dumps(response.json(), indent=4))
        except:
            print(response.text)
            
         # Show success message if API call was successful
        if response.status_code in [200, 201]:
            print("\nMigration Package Created")
        else:
            print("\nMigration Package creation failed.")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    
    input("\nPress Enter to exit...") #Prevents the console from closing immediately

if __name__ == "__main__":
    main()