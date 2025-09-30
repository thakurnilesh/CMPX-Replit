import pandas as pd
import numpy as np

class JSONGenerator:
    """
    A class to generate a nested JSON payload from a pandas DataFrame.
    """
    def __init__(self, excel_data):
        """
        Initializes the JSONGenerator with a DataFrame.
        
        Args:
            excel_data (pd.DataFrame): The input data from an Excel file.
        """
        if not isinstance(excel_data, pd.DataFrame):
            raise TypeError("excel_data must be a pandas DataFrame.")
        self.excel_data = excel_data.copy()  # Work on copy to avoid modifying the original DataFrame

    def generate(self):
        """
        Generates the JSON payload from the DataFrame.
        """
        try:
            print("Getting Started")
            df = self.excel_data

            # Define required columns and fill missing ones with empty strings
            required_columns = [
                'itemName', 'commerceName', 'commerceVariableName', 
                'resourceType', 'granular', 'transactionName', 'transactionVariableName', 
                'transactionResourceType', 'childVariableName', 'childResourceType'
            ]
            
                         
            # Fill NA/NaN values with empty strings for the new columns
            for col in required_columns:
                if col in df.columns:
                    df[col] = df[col].fillna('')
                else:
                    # If column doesn't exist, add it with empty values
                    df[col] = ''
            
            package_name = input("Enter the Package Name: ")
            # Get package name (should be the same for all rows)
            #if df['PackageName'].empty:
            #    raise ValueError("PackageName column is empty.")
            #package_name = df['PackageName'].iloc[0]

            # Initialize the JSON structure
            json_payload = {
                "name": package_name,
                "contents": {
                    "items": []
                }
            }

            # Process each unique item using groupby for efficiency
            item_groups = df.groupby('itemName')

            for item_name, item_rows in item_groups:
                #item_category = item_rows['itemCategory'].iloc[0]
                if item_name == 'Commerce':
                    item_category = 'COMMERCE'
                elif item_name == 'Util Library':
                    item_category = 'UTIL_LIBRARY'
                elif item_name == 'Document Designer':
                    item_category = 'DOCUMENT_DESIGNER'
                elif item_name == 'Email Designer':
                    item_category = 'EMAIL_DESIGNER'
                elif item_name == 'Data Table':
                    item_category = 'DATA_TABLE'
                else:   
                    raise ValueError(f"Incorrect Item Name '{item_name}'.Use: Commerce, Util Library, Document Designer, Email Designer, Data Table")
                
                item = {
                    "name": item_name,
                    "category": item_category,
                    "children": []
                }

                # Assuming commerce details are consistent for each item group
                commerce_name = item_rows['commerceName'].iloc[0]
                commerce_variable_name = item_rows['commerceVariableName'].iloc[0]
                resource_type = item_rows['resourceType'].iloc[0]
                if item_name != "Util Library" :
                    commerce = {
                        "name": commerce_name,
                        "variableName": commerce_variable_name,
                        "resourceType": resource_type,
                        "children": []
                    }
                elif item_name == "Util Library" : 
                      for _, row in item_rows.iterrows():
                        commerce = {
                            "name": row['childVariableName'],
                            "variableName": row['childVariableName'],
                            "resourceType": row['childResourceType']
                        }
                
                is_commerce_item = (item_name.lower() == "commerce")
                is_granular = (item_rows['granular'].astype(str).str.strip().str.upper() == "TRUE").any()

                if is_commerce_item and is_granular:
                # commerce or granular items
                    print("Commerce and Granular Item Found")
                    commerce['granular'] = True
                    
                    # Group children by transaction details
                    transaction_groups = item_rows.groupby(['transactionName', 'transactionVariableName', 'transactionResourceType'])
                    
                    for transaction_details, transaction_rows in transaction_groups:
                        transaction_name, transaction_variable_name, transaction_resource_type = transaction_details
                        
                        if transaction_name and transaction_variable_name and transaction_resource_type:
                            transaction_obj = {
                                "name": transaction_name,
                                "variableName": transaction_variable_name,
                                "resourceType": transaction_resource_type,
                                "children": []
                            }
                            
                            for _, row in transaction_rows.iterrows():
                                child = {
                                    "name": row['childVariableName'],
                                    "variableName": row['childVariableName'],
                                    "resourceType": row['childResourceType']
                                }
                                transaction_obj['children'].append(child)
                                
                            commerce['children'].append(transaction_obj)
                        else:
                            # Handle rows that are not part of a transaction (e.g., granular is false or transaction fields are empty)
                            for _, row in transaction_rows.iterrows():
                                child = {
                                    "name": row['childVariableName'],
                                    "variableName": row['childVariableName'],
                                    "resourceType": row['childResourceType']
                                }
                                commerce['children'].append(child)
                elif item_name != "Util Library" :
                    # Non-commerce or non-granular items
                   #print("Non-Commerce or Non-Granular Item Found")
                    for _, row in item_rows.iterrows():
                        child = {
                            "name": row['childVariableName'],
                            "variableName": row['childVariableName'],
                            "resourceType": row['childResourceType']
                        }
                        commerce['children'].append(child)

                item["children"].append(commerce)
                json_payload["contents"]["items"].append(item)
            
            return json_payload

        except Exception as e:
            # Raise a more informative exception
            raise RuntimeError(f"Failed to generate JSON payload: {e}")

# Example Usage:
if __name__ == "__main__":
    # Create a sample DataFrame to test the class
    data = {
        #'PackageName': ['Auto28AugTest','Auto28AugTest'],
        'itemName': ['Document Designer','Commerce'],
        #'itemCategory': ['DOCUMENT_DESIGNER','COMMERCE'],
        'commerceName': ['Paramount Quote to Order','Paramount Quote to Order'],
        'commerceVariableName': ['oraclecpqo_bmClone_2','oraclecpqo_bmClone_2'],
        'resourceType': ['_set','process'],
        'granular': ['','TRUE'],
        'transactionName': ['','Transaction'],
        'transactionVariableName': ['','transaction'],
        'transactionResourceType': ['','document'],
        #'childName': ['Field Profile Sheet - English','API_Save'],
        'childVariableName': ['Field Profile Sheet - English','aPI_Save_t'],
        'childResourceType': ['doc_designer','action']
    }
    df = pd.DataFrame(data)
    
    generator = JSONGenerator(df)
    result = generator.generate()
    
    import json
    print(json.dumps(result, indent=4))