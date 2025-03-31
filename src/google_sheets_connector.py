import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from src.constants import ROOT_DIR

class GoogleSheetsConnector:
    """
    Class for connecting to Google Sheets and retrieving/updating data.
    Allows for content generation based on spreadsheet data.
    """
    def __init__(self, credentials_path=None):
        """
        Initialize the Google Sheets connector.
        
        Args:
            credentials_path (str): Path to the Google API credentials JSON file
        """
        self.credentials_path = credentials_path
        self.client = None
        self.connected = False
        
        # Try to connect if credentials are provided
        if self.credentials_path and os.path.exists(self.credentials_path):
            self.connect()
    
    def connect(self, credentials_path=None):
        """
        Connect to Google Sheets API.
        
        Args:
            credentials_path (str): Path to the Google API credentials JSON file
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        if credentials_path:
            self.credentials_path = credentials_path
            
        if not self.credentials_path or not os.path.exists(self.credentials_path):
            print("No valid credentials file provided")
            return False
            
        try:
            # Define the scope
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            
            # Authenticate
            credentials = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_path, scope)
            self.client = gspread.authorize(credentials)
            self.connected = True
            return True
            
        except Exception as e:
            print(f"Error connecting to Google Sheets: {e}")
            self.connected = False
            return False
    
    def get_spreadsheet(self, spreadsheet_id=None, spreadsheet_name=None):
        """
        Get a spreadsheet by ID or name.
        
        Args:
            spreadsheet_id (str): The ID of the spreadsheet
            spreadsheet_name (str): The name of the spreadsheet
            
        Returns:
            gspread.Spreadsheet: The spreadsheet object or None if not found
        """
        if not self.connected or not self.client:
            print("Not connected to Google Sheets")
            return None
            
        try:
            if spreadsheet_id:
                return self.client.open_by_key(spreadsheet_id)
            elif spreadsheet_name:
                return self.client.open(spreadsheet_name)
            else:
                print("No spreadsheet ID or name provided")
                return None
                
        except Exception as e:
            print(f"Error getting spreadsheet: {e}")
            return None
    
    def get_worksheet(self, spreadsheet, worksheet_index=0, worksheet_name=None):
        """
        Get a worksheet from a spreadsheet.
        
        Args:
            spreadsheet (gspread.Spreadsheet): The spreadsheet object
            worksheet_index (int): The index of the worksheet (0-based)
            worksheet_name (str): The name of the worksheet
            
        Returns:
            gspread.Worksheet: The worksheet object or None if not found
        """
        if not spreadsheet:
            return None
            
        try:
            if worksheet_name:
                return spreadsheet.worksheet(worksheet_name)
            else:
                return spreadsheet.get_worksheet(worksheet_index)
                
        except Exception as e:
            print(f"Error getting worksheet: {e}")
            return None
    
    def get_content_data(self, spreadsheet_id=None, spreadsheet_name=None, worksheet_name="Content"):
        """
        Get content data from a spreadsheet.
        
        Args:
            spreadsheet_id (str): The ID of the spreadsheet
            spreadsheet_name (str): The name of the spreadsheet
            worksheet_name (str): The name of the worksheet
            
        Returns:
            list: List of dictionaries with content data
        """
        spreadsheet = self.get_spreadsheet(spreadsheet_id, spreadsheet_name)
        if not spreadsheet:
            return []
            
        worksheet = self.get_worksheet(spreadsheet, worksheet_name=worksheet_name)
        if not worksheet:
            return []
            
        try:
            # Get all records (assumes first row is header)
            records = worksheet.get_all_records()
            return records
            
        except Exception as e:
            print(f"Error getting content data: {e}")
            return []
    
    def update_content_status(self, row_index, status, spreadsheet_id=None, spreadsheet_name=None, worksheet_name="Content"):
        """
        Update the status of a content row.
        
        Args:
            row_index (int): The row index to update (1-based)
            status (str): The status to set
            spreadsheet_id (str): The ID of the spreadsheet
            spreadsheet_name (str): The name of the spreadsheet
            worksheet_name (str): The name of the worksheet
            
        Returns:
            bool: True if update successful, False otherwise
        """
        spreadsheet = self.get_spreadsheet(spreadsheet_id, spreadsheet_name)
        if not spreadsheet:
            return False
            
        worksheet = self.get_worksheet(spreadsheet, worksheet_name=worksheet_name)
        if not worksheet:
            return False
            
        try:
            # Find the status column
            headers = worksheet.row_values(1)
            status_col = None
            
            for i, header in enumerate(headers):
                if header.lower() == "status":
                    status_col = i + 1  # Convert to 1-based index
                    break
            
            if not status_col:
                # If no status column exists, add one
                status_col = len(headers) + 1
                worksheet.update_cell(1, status_col, "Status")
            
            # Update the status cell
            worksheet.update_cell(row_index, status_col, status)
            return True
            
        except Exception as e:
            print(f"Error updating content status: {e}")
            return False
    
    def add_content_row(self, content_data, spreadsheet_id=None, spreadsheet_name=None, worksheet_name="Content"):
        """
        Add a new content row to the spreadsheet.
        
        Args:
            content_data (dict): The content data to add
            spreadsheet_id (str): The ID of the spreadsheet
            spreadsheet_name (str): The name of the spreadsheet
            worksheet_name (str): The name of the worksheet
            
        Returns:
            int: The row index of the added row or 0 if failed
        """
        spreadsheet = self.get_spreadsheet(spreadsheet_id, spreadsheet_name)
        if not spreadsheet:
            return 0
            
        worksheet = self.get_worksheet(spreadsheet, worksheet_name=worksheet_name)
        if not worksheet:
            return 0
            
        try:
            # Get headers
            headers = worksheet.row_values(1)
            
            # Prepare row data
            row_data = []
            for header in headers:
                row_data.append(content_data.get(header, ""))
            
            # Append row
            worksheet.append_row(row_data)
            
            # Return the row index
            return worksheet.row_count
            
        except Exception as e:
            print(f"Error adding content row: {e}")
            return 0
    
    def get_content_by_type(self, content_type, status="pending", spreadsheet_id=None, spreadsheet_name=None, worksheet_name="Content"):
        """
        Get content data filtered by type and status.
        
        Args:
            content_type (str): The type of content to filter by (e.g., "shorts", "blog", "ebook")
            status (str): The status to filter by (e.g., "pending", "completed")
            spreadsheet_id (str): The ID of the spreadsheet
            spreadsheet_name (str): The name of the spreadsheet
            worksheet_name (str): The name of the worksheet
            
        Returns:
            list: List of dictionaries with filtered content data
        """
        all_content = self.get_content_data(spreadsheet_id, spreadsheet_name, worksheet_name)
        
        # Filter by type and status
        filtered_content = []
        for content in all_content:
            content_type_match = content.get("Type", "").lower() == content_type.lower()
            status_match = content.get("Status", "").lower() == status.lower()
            
            if content_type_match and status_match:
                filtered_content.append(content)
        
        return filtered_content
    
    def create_template_spreadsheet(self, spreadsheet_name="MoneyPrinter Content"):
        """
        Create a template spreadsheet for content management.
        
        Args:
            spreadsheet_name (str): The name for the new spreadsheet
            
        Returns:
            str: The ID of the created spreadsheet or None if failed
        """
        if not self.connected or not self.client:
            print("Not connected to Google Sheets")
            return None
            
        try:
            # Create new spreadsheet
            spreadsheet = self.client.create(spreadsheet_name)
            
            # Get the first worksheet
            worksheet = spreadsheet.get_worksheet(0)
            
            # Rename the worksheet
            worksheet.update_title("Content")
            
            # Set up headers
            headers = [
                "Topic", "Type", "Script", "Title", "Description", 
                "Keywords", "Status", "URL", "Date Created", "Date Published"
            ]
            
            # Add headers to the first row
            for i, header in enumerate(headers):
                worksheet.update_cell(1, i+1, header)
            
            # Format the header row
            worksheet.format("A1:J1", {
                "backgroundColor": {"red": 0.2, "green": 0.2, "blue": 0.2},
                "textFormat": {"bold": True, "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}}
            })
            
            # Resize columns
            worksheet.resize(rows=100, cols=len(headers))
            
            return spreadsheet.id
            
        except Exception as e:
            print(f"Error creating template spreadsheet: {e}")
            return None
