import pandas as pd

class ExcelParser:
    def __init__(self, file_path):
        self.file_path = file_path
        
    def parse(self):
        """
        Parse the Excel file and return structured data.
        """
        try:
            # Read Excel file
            df = pd.read_excel(self.file_path)
            
            # Check if core required columns exist
            core_required_columns = [
                'itemName', 'itemCategory', 
                'commerceName', 'commerceVariableName', 'resourceType',
                'childName', 'childVariableName', 'childResourceType'
            ]
            
            for col in core_required_columns:
                if col not in df.columns:
                    raise ValueError(f"Required column '{col}' not found in Excel file.")
            
            # For new columns, add them with empty values if they don't exist
            new_columns = [
                'granular', 'transactionName', 'transactionVariableName', 'transactionResourceType'
            ]
            
            for col in new_columns:
                if col not in df.columns:
                    df[col] = ''
                else:
                    # Fill NA values with empty strings
                    df[col] = df[col].fillna('')
            
            # Return the DataFrame for further processing
            return df
            
        except Exception as e:
            raise Exception(f"Failed to parse Excel file: {str(e)}")