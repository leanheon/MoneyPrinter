import os
import json
from datetime import datetime
from src.classes.ShortsGenerator import ShortsGenerator
from src.blog_generator import BlogGenerator
from src.google_sheets_connector import GoogleSheetsConnector
from src.constants import ROOT_DIR

class ContentManager:
    """
    Class for managing content generation across different platforms using Google Sheets data.
    Integrates shorts generator, blog posting, and other content types.
    """
    def __init__(self, credentials_path=None):
        """
        Initialize the Content Manager.
        
        Args:
            credentials_path (str): Path to Google API credentials
        """
        self.sheets_connector = GoogleSheetsConnector(credentials_path)
        self.blog_generator = BlogGenerator()
        self.spreadsheet_id = None
        self.spreadsheet_name = None
        
    def set_spreadsheet(self, spreadsheet_id=None, spreadsheet_name=None):
        """
        Set the active spreadsheet.
        
        Args:
            spreadsheet_id (str): The ID of the spreadsheet
            spreadsheet_name (str): The name of the spreadsheet
            
        Returns:
            bool: True if spreadsheet was set successfully
        """
        self.spreadsheet_id = spreadsheet_id
        self.spreadsheet_name = spreadsheet_name
        return True
        
    def create_template_spreadsheet(self, name="MoneyPrinter Content"):
        """
        Create a template spreadsheet for content management.
        
        Args:
            name (str): Name for the new spreadsheet
            
        Returns:
            str: ID of the created spreadsheet
        """
        spreadsheet_id = self.sheets_connector.create_template_spreadsheet(name)
        if spreadsheet_id:
            self.spreadsheet_id = spreadsheet_id
            self.spreadsheet_name = name
        return spreadsheet_id
        
    def get_pending_content(self, content_type=None):
        """
        Get pending content from the spreadsheet.
        
        Args:
            content_type (str): Type of content to filter by
            
        Returns:
            list: List of content items
        """
        if content_type:
            return self.sheets_connector.get_content_by_type(
                content_type, 
                "pending", 
                self.spreadsheet_id, 
                self.spreadsheet_name
            )
        else:
            all_content = self.sheets_connector.get_content_data(
                self.spreadsheet_id, 
                self.spreadsheet_name
            )
            return [c for c in all_content if c.get("Status", "").lower() == "pending"]
            
    def process_content_item(self, content_item, row_index):
        """
        Process a single content item based on its type.
        
        Args:
            content_item (dict): Content item data
            row_index (int): Row index in spreadsheet
            
        Returns:
            dict: Result of content processing
        """
        content_type = content_item.get("Type", "").lower()
        topic = content_item.get("Topic", "")
        script = content_item.get("Script", "")
        
        if not topic:
            return {"success": False, "error": "No topic provided"}
            
        result = {"success": False, "type": content_type}
        
        try:
            if content_type == "shorts" or content_type == "short":
                # Process as shorts
                is_knowledge = content_item.get("Knowledge", "").lower() == "true"
                result = self._process_shorts(topic, script, is_knowledge)
                
            elif content_type == "blog" or content_type == "blogpost":
                # Process as blog post
                length = content_item.get("Length", "medium")
                result = self._process_blog(topic, length)
                
            else:
                result = {"success": False, "error": f"Unknown content type: {content_type}"}
                
            # Update spreadsheet status
            if result.get("success"):
                self.sheets_connector.update_content_status(
                    row_index, 
                    "completed", 
                    self.spreadsheet_id, 
                    self.spreadsheet_name
                )
                
                # Update URL if available
                if "url" in result:
                    self._update_content_url(row_index, result["url"])
                    
            else:
                self.sheets_connector.update_content_status(
                    row_index, 
                    f"failed: {result.get('error', 'unknown error')}", 
                    self.spreadsheet_id, 
                    self.spreadsheet_name
                )
                
            return result
            
        except Exception as e:
            error_msg = str(e)
            self.sheets_connector.update_content_status(
                row_index, 
                f"error: {error_msg}", 
                self.spreadsheet_id, 
                self.spreadsheet_name
            )
            return {"success": False, "error": error_msg}
            
    def _process_shorts(self, topic, script=None, is_knowledge=False):
        """
        Process a shorts content item.
        
        Args:
            topic (str): Topic for the shorts
            script (str): Optional pre-written script
            is_knowledge (bool): Whether this is a knowledge short
            
        Returns:
            dict: Result of shorts processing
        """
        # Create ShortsGenerator instance
        shorts_generator = ShortsGenerator(topic, is_knowledge)
        
        # Use provided script or generate new one
        if script and script.strip():
            shorts_generator.script = script.strip()
        else:
            shorts_generator.generate_script()
            
        # Generate metadata
        shorts_generator.generate_metadata()
        
        # Create the short
        video_path = shorts_generator.create_short()
        
        if video_path:
            return {
                "success": True,
                "video_path": video_path,
                "title": shorts_generator.title,
                "description": shorts_generator.description,
                "type": "knowledge_short" if is_knowledge else "story_short"
            }
        else:
            return {"success": False, "error": "Failed to create short"}
            
    def _process_blog(self, topic, length="medium"):
        """
        Process a blog content item.
        
        Args:
            topic (str): Topic for the blog post
            length (str): Length of the blog post
            
        Returns:
            dict: Result of blog processing
        """
        # Generate blog post
        blog_post = self.blog_generator.generate_blog_post(topic, length)
        
        # Save blog post files
        saved_files = self.blog_generator.save_blog_post(blog_post)
        
        # Simulate posting to blog
        post_result = self.blog_generator.post_to_blog(blog_post)
        
        if saved_files and "html_path" in saved_files:
            return {
                "success": True,
                "blog_post": blog_post,
                "saved_files": saved_files,
                "url": post_result.get("url") if post_result else None
            }
        else:
            return {"success": False, "error": "Failed to create blog post"}
            
    def _update_content_url(self, row_index, url):
        """
        Update the URL of a content item in the spreadsheet.
        
        Args:
            row_index (int): Row index in spreadsheet
            url (str): URL to set
            
        Returns:
            bool: True if update was successful
        """
        spreadsheet = self.sheets_connector.get_spreadsheet(
            self.spreadsheet_id, 
            self.spreadsheet_name
        )
        if not spreadsheet:
            return False
            
        worksheet = self.sheets_connector.get_worksheet(spreadsheet)
        if not worksheet:
            return False
            
        try:
            # Find the URL column
            headers = worksheet.row_values(1)
            url_col = None
            
            for i, header in enumerate(headers):
                if header.lower() == "url":
                    url_col = i + 1  # Convert to 1-based index
                    break
            
            if not url_col:
                return False
            
            # Update the URL cell
            worksheet.update_cell(row_index, url_col, url)
            return True
            
        except Exception as e:
            print(f"Error updating content URL: {e}")
            return False
            
    def process_all_pending(self, content_type=None):
        """
        Process all pending content items.
        
        Args:
            content_type (str): Type of content to filter by
            
        Returns:
            list: Results of all processed items
        """
        pending_items = self.get_pending_content(content_type)
        results = []
        
        for item in pending_items:
            # Find the row index
            all_content = self.sheets_connector.get_content_data(
                self.spreadsheet_id, 
                self.spreadsheet_name
            )
            
            row_index = None
            for i, content in enumerate(all_content):
                if (content.get("Topic") == item.get("Topic") and 
                    content.get("Type") == item.get("Type") and
                    content.get("Status", "").lower() == "pending"):
                    # Row index is 1-based and includes header row
                    row_index = i + 2
                    break
                    
            if row_index:
                result = self.process_content_item(item, row_index)
                results.append(result)
                
        return results
        
    def add_content_item(self, topic, content_type, script=None, additional_data=None):
        """
        Add a new content item to the spreadsheet.
        
        Args:
            topic (str): Topic for the content
            content_type (str): Type of content
            script (str): Optional pre-written script
            additional_data (dict): Additional data for the content item
            
        Returns:
            int: Row index of the added item
        """
        content_data = {
            "Topic": topic,
            "Type": content_type,
            "Script": script or "",
            "Status": "pending",
            "Date Created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Add any additional data
        if additional_data and isinstance(additional_data, dict):
            content_data.update(additional_data)
            
        row_index = self.sheets_connector.add_content_row(
            content_data,
            self.spreadsheet_id,
            self.spreadsheet_name
        )
        
        return row_index
