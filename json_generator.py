class JSONGenerator:
    def __init__(self, excel_data):
        self.excel_data = excel_data
        
    def generate(self):
        """
        Generate the JSON payload from Excel data.
        """
        try:
            df = self.excel_data
            
            # Check if new required columns exist
            required_columns = [
                'granular', 'transactionName', 'transactionVariableName', 'transactionResourceType'
            ]
            
            # Fill NA/NaN values with empty strings for the new columns
            for col in required_columns:
                if col in df.columns:
                    df[col] = df[col].fillna('')
                else:
                    # If column doesn't exist, add it with empty values
                    df[col] = ''
            
            # Get package name (should be the same for all rows)
            package_name = df['PackageName'].iloc[0]
            
            # Initialize the JSON structure
            json_payload = {
                "name": package_name,
                "contents": {
                    "items": []
                }
            }
            
            # Process each unique item
            item_names = df['itemName'].unique()
            
            for item_name in item_names:
                # Filter rows for this item
                item_rows = df[df['itemName'] == item_name]
                
                # Get item category (should be the same for all rows of this item)
                item_category = item_rows['itemCategory'].iloc[0]
                
                # Create item structure
                item = {
                    "name": item_name,
                    "category": item_category,
                    "children": []
                }
                
                # Add commerce level (first level children)
                # These should be the same across all rows for this item
                commerce_name = item_rows['commerceName'].iloc[0]
                commerce_variable_name = item_rows['commerceVariableName'].iloc[0]
                resource_type = item_rows['resourceType'].iloc[0]
                
                commerce = {
                    "name": commerce_name,
                    "variableName": commerce_variable_name,
                    "resourceType": resource_type,
                    "children": []
                }
                
                # Special handling for Commerce items with granular=TRUE
                is_commerce_item = (item_name == "Commerce")
                
                # Check if any rows have granular=TRUE
                has_granular_true = False
                if is_commerce_item:
                    for _, row in item_rows.iterrows():
                        granular_value = str(row['granular']).strip().upper()
                        if granular_value == "TRUE":
                            has_granular_true = True
                            # Add granular field to commerce object
                            commerce["granular"] = row['granular']
                            break
                
                # Process the rows based on special case or normal case
                if is_commerce_item:
                    # Group by transaction details to avoid duplicates
                    transaction_groups = {}
                    regular_children = []
                    
                    for _, row in item_rows.iterrows():
                        granular_value = str(row['granular']).strip().upper()
                        is_granular = granular_value == "TRUE"
                        
                        # Create child object
                        child = {
                            "name": row['childName'],
                            "variableName": row['childVariableName'],
                            "resourceType": row['childResourceType']
                        }
                        
                        if is_granular and row['transactionName'] and row['transactionVariableName'] and row['transactionResourceType']:
                            # Get transaction details
                            transaction_name = row['transactionName']
                            transaction_variable_name = row['transactionVariableName']
                            transaction_resource_type = row['transactionResourceType']
                            
                            # Create a key for grouping
                            transaction_key = f"{transaction_name}_{transaction_variable_name}_{transaction_resource_type}"
                            
                            # Initialize transaction if not exists
                            if transaction_key not in transaction_groups:
                                transaction_groups[transaction_key] = {
                                    "transaction_data": {
                                        "name": transaction_name,
                                        "variableName": transaction_variable_name,
                                        "resourceType": transaction_resource_type,
                                        "children": []
                                    },
                                    "children": []
                                }
                            
                            # Add child to this transaction
                            transaction_groups[transaction_key]["children"].append(child)
                        else:
                            # Regular child processing for non-granular rows or when transaction fields are blank
                            regular_children.append(child)
                    
                    # Add regular children directly to commerce
                    for child in regular_children:
                        commerce["children"].append(child)
                    
                    # Add transactions to commerce children
                    for transaction_key, transaction_data in transaction_groups.items():
                        transaction_obj = transaction_data["transaction_data"]
                        
                        # Add children to transaction
                        for child in transaction_data["children"]:
                            transaction_obj["children"].append(child)
                        
                        # Add transaction to commerce
                        commerce["children"].append(transaction_obj)
                else:
                    # Standard processing for non-Commerce items
                    for _, row in item_rows.iterrows():
                        child = {
                            "name": row['childName'],
                            "variableName": row['childVariableName'],
                            "resourceType": row['childResourceType']
                        }
                        commerce["children"].append(child)
                
                # Add commerce to item
                item["children"].append(commerce)
                
                # Add item to payload
                json_payload["contents"]["items"].append(item)
            
            return json_payload
            
        except Exception as e:
            raise Exception(f"Failed to generate JSON payload: {str(e)}")