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
            # Mixed items - handle with two-step API call
            print("Detected both Configuration and standard items...")
            print("Will create package with standard items first, then update with Configuration items.")
            
            # This will be handled after API confirmation
            payload = None
        
        # Handle mixed items scenario
        if has_configuration and has_other_items:
            # Get package name first for mixed items
            package_name = input("\nEnter the Package Name: ")
            
            # Step 1: Generate payload for non-Configuration items
            print("\n[Step 1/2] Generating payload for standard items...")
            non_config_data = excel_data[excel_data['itemName'] != 'Configuration']
            standard_generator = JSONGenerator(non_config_data)
            standard_payload = standard_generator.generate()
            
            print("\nStandard Items Payload:")
            print(json.dumps(standard_payload, indent=4))
            
            # Confirm with user
            confirm = input("\nDo you want to submit to the API? (yes/no): ")
            if confirm.lower() != 'yes':
                print("Operation cancelled by user.")
                return
            
            # Get API details
            cpq_instance = input("\nEnter the CPQ instance name: ")
            api_endpoint = f"{cpq_instance}/rest/v14/migrationPackages"
            username = input("Enter username for Basic Auth: ")
            password = input("Enter password for Basic Auth: ")
            
            # Make first API call (POST)
            print("\n[Step 1/2] Creating migration package with standard items...")
            api_client = APIClient(api_endpoint, username, password)
            response = api_client.post_data(standard_payload)
            
            # Display response
            print("\nAPI Response (CREATE):")
            print(f"Status Code: {response.status_code}")
            print("Response Body:")
            try:
                print(json.dumps(response.json(), indent=4))
            except:
                print(response.text)
            
            if response.status_code not in [200, 201]:
                print("\nMigration Package creation failed. Cannot proceed with Configuration items.")
                return
            
            print("\nMigration Package Created Successfully!")
            
            # Step 2: Generate payload for Configuration items
            print("\n[Step 2/2] Generating payload for Configuration items...")
            config_data = excel_data[excel_data['itemName'] == 'Configuration']
            config_generator = ConfigurationGenerator(config_data)
            config_payload = config_generator.generate(package_name)
            
            print("\nConfiguration Items Payload:")
            print(json.dumps(config_payload, indent=4))
            
            # Generate identifier for PATCH
            identifier = package_name.lower() + "_v1"
            
            # Make second API call (PATCH)
            print(f"\n[Step 2/2] Updating migration package with Configuration items (identifier: {identifier})...")
            patch_response = api_client.patch_data(identifier, config_payload)
            
            # Display response
            print("\nAPI Response (UPDATE):")
            print(f"Status Code: {patch_response.status_code}")
            print("Response Body:")
            try:
                print(json.dumps(patch_response.json(), indent=4))
            except:
                print(patch_response.text)
            
            # Show final success message
            if patch_response.status_code in [200, 201]:
                print("\nMigration Package Updated with Configuration Items Successfully!")
            else:
                print("\nConfiguration items update failed.")
        
        else:
            # Single item type - existing flow
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
                print("\nMigration Package Created Successfully!")
            else:
                print("\nMigration Package creation failed.")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    
    input("\nPress Enter to exit...") #Prevents the console from closing immediately

if __name__ == "__main__":
    main()