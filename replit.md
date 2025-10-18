# Excel to API Tool

## Overview
This is a Python CLI application that converts Excel files to JSON payloads and sends them to API endpoints. It's designed to parse migration package data from Excel spreadsheets and submit them to BigMachines API endpoints.

## Purpose
The tool automates the process of creating migration packages by:
1. Reading structured data from Excel files
2. Generating properly formatted JSON payloads
3. Sending the data to API endpoints with authentication

## Project Structure
- `main.py` - Main entry point and user interface
- `excel_parser.py` - Handles Excel file parsing using pandas
- `json_generator.py` - Generates JSON payloads for standard items (Commerce, Util Library, etc.)
- `configuration_generator.py` - Generates JSON payloads for Configuration items with nested tree structure
- `api_client.py` - Manages API communication with Basic Auth
- `migrate3.xlsx` - Sample Excel file for testing standard items
- `ConfigTracker2.xlsx` - Sample Excel file for testing Configuration items

## Dependencies
- pandas (2.0.3) - Excel file parsing
- openpyxl (3.1.2) - Excel file support
- xlrd (2.0.1) - Excel file support
- requests (2.31.0) - HTTP API calls
- numpy (1.24.3) - Numerical operations

## How to Use
1. Run the application from the console
2. Enter the path to your Excel file (e.g., `migrate3.xlsx` for the sample file)
3. The tool will generate a JSON payload and display it
4. Confirm if you want to submit to the API
5. Enter API endpoint URL and credentials
6. View the response

## Excel File Format
The Excel file should contain these columns:
- `itemName` - Item type (Commerce, Util Library, Document Designer, etc.)
- `commerceName` - Commerce process name
- `commerceVariableName` - Variable name
- `resourceType` - Resource type
- `granular` - TRUE/FALSE for granular items
- `transactionName` - Transaction name (optional)
- `transactionVariableName` - Transaction variable (optional)
- `transactionResourceType` - Transaction resource type (optional)
- `childVariableName` - Child variable name
- `childResourceType` - Child resource type

## Supported Item Types
- Commerce (COMMERCE)
- Util Library (UTIL_LIBRARY)
- Document Designer (DOCUMENT_DESIGNER)
- Email Designer (EMAIL_DESIGNER)
- Data Table (DATA_TABLE)
- Configuration (CONFIGURATION)

## Recent Changes
- **2025-10-18**: Added Configuration item support
  - Created `configuration_generator.py` for handling Configuration items
  - Implemented nested tree structure generation from delimiter-separated paths
  - Added automatic detection and routing of Configuration vs standard items
  - Configuration items use `commerceVariableName` with dot-delimiter (e.g., "fireDomain.install.expense")
  - Generates hierarchical JSON with "All Product Family" wrapper
  - Supports product_family → product_line → model hierarchy

- **2025-10-07**: Initial Replit setup
  - Installed Python 3.11 and all required dependencies
  - Fixed variable binding issues in json_generator.py
  - Created requirements.txt for dependency management
  - Added .gitignore for Python project
  - Configured CLI workflow for console output
  - Created project documentation

## Architecture
This is a command-line tool that follows a modular architecture:
1. **Parser Layer**: Reads and validates Excel data
2. **Generator Layer**: Transforms data into API-compatible JSON
3. **Client Layer**: Handles HTTP communication with authentication
4. **Main Interface**: Interactive CLI for user input and feedback
