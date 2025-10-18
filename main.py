import argparse
import json
import sys
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
from excel_parser import ExcelParser
from json_generator import JSONGenerator
from configuration_generator import ConfigurationGenerator
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
        
        # Check if we have Configuration items
        has_configuration = (excel_data['itemName'] == 'Configuration').any()
        has_other_items = (excel_data['itemName'] != 'Configuration').any()
        
        # Generate JSON payload
        print("Generating JSON payload...")
        
        if has_configuration and not has_other_items:
            # Only Configuration items - use ConfigurationGenerator
            print("Detected Configuration items only...")
            package_name = input("Enter the Package Name: ")
            generator = ConfigurationGenerator(excel_data)
            payload = generator.generate(package_name)
        elif not has_configuration and has_other_items:
            # Only non-Configuration items - use existing JSONGenerator
            print("Detected standard items...")
            generator = JSONGenerator(excel_data)
            payload = generator.generate()
        else:
            # Mixed items - for now, handle them separately (future enhancement)
            print("Error: Mixed Configuration and non-Configuration items not yet supported.")
            print("Please use separate Excel files for Configuration and other items.")
            return
        
        # Display the generated JSON for verification
        print("\nGenerated JSON Payload:")
        print(json.dumps(payload, indent=4))
        
        # Confirm with user
        confirm = input("\nDo you want to submit this payload to the API? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Operation cancelled by user.")
            return
        
        # Get API details
        cpq_instance = input("\nEnter the CPQ instance name: ")
        api_endpoint = f"{cpq_instance}/rest/v14/migrationPackages"
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