import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from src.constants import ROOT_DIR
from src.social_media_manager import SocialMediaManager
from src.enhanced_shorts import EnhancedShorts
from src.blog_generator import BlogGenerator
from src.ebook_generator import EbookGenerator
from src.card_news_generator import CardNewsGenerator
from src.dropbox_uploader import DropboxUploader

class IntegratedContentManager:
    """
    Integrated Content Manager that connects all components with Google Sheets.
    Manages content creation across different platforms and formats.
    """
    def __init__(self, google_credentials_path=None, dropbox_token=None):
        """
        Initialize the Integrated Content Manager.
        
        Args:
            google_credentials_path (str): Path to Google API credentials
            dropbox_token (str): Dropbox access token
        """
        self.google_credentials_path = google_credentials_path
        self.dropbox_token = dropbox_token
        
        # Initialize components
        self.social_media_manager = SocialMediaManager()
        self.enhanced_shorts = EnhancedShorts(dropbox_token)
        self.blog_generator = BlogGenerator()
        self.ebook_generator = EbookGenerator()
        self.card_news_generator = CardNewsGenerator()
        self.dropbox_uploader = DropboxUploader(dropbox_token)
        
        # Google Sheets connection
        self.sheets_client = None
        self.connected = False
        self.spreadsheet_id = None
        self.spreadsheet_name = None
        
        # Try to connect if credentials are provided
        if self.google_credentials_path and os.path.exists(self.google_credentials_path):
            self.connect_to_sheets()
    
    def connect_to_sheets(self, credentials_path=None):
        """
        Connect to Google Sheets API.
        
        Args:
            credentials_path (str): Path to the Google API credentials JSON file
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        if credentials_path:
            self.google_credentials_path = credentials_path
            
        if not self.google_credentials_path or not os.path.exists(self.google_credentials_path):
            print("No valid credentials file provided")
            return False
            
        try:
            # Define the scope
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            
            # Authenticate
            credentials = ServiceAccountCredentials.from_json_keyfile_name(self.google_credentials_path, scope)
            self.sheets_client = gspread.authorize(credentials)
            self.connected = True
            return True
            
        except Exception as e:
            print(f"Error connecting to Google Sheets: {e}")
            self.connected = False
            return False
    
    def connect_to_dropbox(self, access_token=None):
        """
        Connect to Dropbox API.
        
        Args:
            access_token (str): Dropbox API access token
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        if access_token:
            self.dropbox_token = access_token
            
        result = self.dropbox_uploader.connect(self.dropbox_token)
        
        if result:
            # Update the token in the enhanced shorts generator
            self.enhanced_shorts = EnhancedShorts(self.dropbox_token)
            
        return result
    
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
    
    def create_template_spreadsheet(self, name="KyuGle Content Manager"):
        """
        Create a template spreadsheet for content management.
        
        Args:
            name (str): Name for the new spreadsheet
            
        Returns:
            str: ID of the created spreadsheet
        """
        if not self.connected or not self.sheets_client:
            print("Not connected to Google Sheets")
            return None
            
        try:
            # Create new spreadsheet
            spreadsheet = self.sheets_client.create(name)
            
            # Get the first worksheet
            worksheet = spreadsheet.get_worksheet(0)
            
            # Rename the worksheet
            worksheet.update_title("Content")
            
            # Set up headers
            headers = [
                "Topic", "Type", "Method", "Script", "Title", "Description", 
                "Keywords", "Status", "URL", "Dropbox Link", "Date Created", "Date Published"
            ]
            
            # Add headers to the first row
            for i, header in enumerate(headers):
                worksheet.update_cell(1, i+1, header)
            
            # Format the header row
            worksheet.format("A1:L1", {
                "backgroundColor": {"red": 0.2, "green": 0.2, "blue": 0.2},
                "textFormat": {"bold": True, "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}}
            })
            
            # Create Social Media worksheet
            social_worksheet = spreadsheet.add_worksheet(title="Social Media", rows=100, cols=10)
            
            # Set up headers for Social Media worksheet
            social_headers = [
                "Topic", "Platform", "Content Type", "Caption/Text", "Images", 
                "Status", "URL", "Date Created", "Date Published"
            ]
            
            # Add headers to the first row
            for i, header in enumerate(social_headers):
                social_worksheet.update_cell(1, i+1, header)
            
            # Format the header row
            social_worksheet.format("A1:I1", {
                "backgroundColor": {"red": 0.2, "green": 0.2, "blue": 0.2},
                "textFormat": {"bold": True, "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}}
            })
            
            # Set the spreadsheet ID and name
            self.spreadsheet_id = spreadsheet.id
            self.spreadsheet_name = name
            
            return spreadsheet.id
            
        except Exception as e:
            print(f"Error creating template spreadsheet: {e}")
            return None
    
    def get_spreadsheet(self):
        """
        Get the active spreadsheet.
        
        Returns:
            gspread.Spreadsheet: The spreadsheet object or None if not found
        """
        if not self.connected or not self.sheets_client:
            print("Not connected to Google Sheets")
            return None
            
        try:
            if self.spreadsheet_id:
                return self.sheets_client.open_by_key(self.spreadsheet_id)
            elif self.spreadsheet_name:
                return self.sheets_client.open(self.spreadsheet_name)
            else:
                print("No spreadsheet ID or name provided")
                return None
                
        except Exception as e:
            print(f"Error getting spreadsheet: {e}")
            return None
    
    def get_content_data(self, worksheet_name="Content"):
        """
        Get content data from the spreadsheet.
        
        Args:
            worksheet_name (str): The name of the worksheet
            
        Returns:
            list: List of dictionaries with content data
        """
        spreadsheet = self.get_spreadsheet()
        if not spreadsheet:
            return []
            
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
            records = worksheet.get_all_records()
            return records
            
        except Exception as e:
            print(f"Error getting content data: {e}")
            return []
    
    def get_pending_content(self, content_type=None, worksheet_name="Content"):
        """
        Get pending content from the spreadsheet.
        
        Args:
            content_type (str): Type of content to filter by
            worksheet_name (str): The name of the worksheet
            
        Returns:
            list: List of content items
        """
        all_content = self.get_content_data(worksheet_name)
        
        # Filter by status
        pending_content = [c for c in all_content if c.get("Status", "").lower() == "pending"]
        
        # Filter by type if specified
        if content_type:
            pending_content = [c for c in pending_content if c.get("Type", "").lower() == content_type.lower()]
            
        return pending_content
    
    def add_content_item(self, content_data, worksheet_name="Content"):
        """
        Add a new content item to the spreadsheet.
        
        Args:
            content_data (dict): The content data to add
            worksheet_name (str): The name of the worksheet
            
        Returns:
            int: Row index of the added item
        """
        spreadsheet = self.get_spreadsheet()
        if not spreadsheet:
            return 0
            
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
            
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
    
    def update_content_status(self, row_index, status, worksheet_name="Content"):
        """
        Update the status of a content row.
        
        Args:
            row_index (int): The row index to update (1-based)
            status (str): The status to set
            worksheet_name (str): The name of the worksheet
            
        Returns:
            bool: True if update successful, False otherwise
        """
        spreadsheet = self.get_spreadsheet()
        if not spreadsheet:
            return False
            
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
            
            # Find the status column
            headers = worksheet.row_values(1)
            status_col = None
            
            for i, header in enumerate(headers):
                if header.lower() == "status":
                    status_col = i + 1  # Convert to 1-based index
                    break
            
            if not status_col:
                print("Status column not found")
                return False
            
            # Update the status cell
            worksheet.update_cell(row_index, status_col, status)
            return True
            
        except Exception as e:
            print(f"Error updating content status: {e}")
            return False
    
    def update_content_url(self, row_index, url, column_name="URL", worksheet_name="Content"):
        """
        Update a URL or link in a content row.
        
        Args:
            row_index (int): The row index to update (1-based)
            url (str): The URL to set
            column_name (str): The column name to update
            worksheet_name (str): The name of the worksheet
            
        Returns:
            bool: True if update successful, False otherwise
        """
        spreadsheet = self.get_spreadsheet()
        if not spreadsheet:
            return False
            
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
            
            # Find the column
            headers = worksheet.row_values(1)
            col_index = None
            
            for i, header in enumerate(headers):
                if header.lower() == column_name.lower():
                    col_index = i + 1  # Convert to 1-based index
                    break
            
            if not col_index:
                print(f"{column_name} column not found")
                return False
            
            # Update the cell
            worksheet.update_cell(row_index, col_index, url)
            return True
            
        except Exception as e:
            print(f"Error updating content {column_name}: {e}")
            return False
    
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
        method = content_item.get("Method", "")
        
        if not topic:
            return {"success": False, "error": "No topic provided"}
            
        result = {"success": False, "type": content_type}
        
        try:
            # Process based on content type
            if content_type == "shorts" or content_type == "short":
                # Use method if provided, default to "story"
                if not method:
                    method = "story"
                    
                # Process as Enhanced shorts
                result = self._process_shorts(topic, script, method, row_index)
                
            elif content_type == "blog" or content_type == "blogpost":
                # Process as blog post
                length = content_item.get("Length", "medium")
                result = self._process_blog(topic, length, row_index)
                
            elif content_type == "ebook":
                # Process as ebook
                format = content_item.get("Format", "epub")
                length = content_item.get("Length", "medium")
                chapters = int(content_item.get("Chapters", "5"))
                result = self._process_ebook(topic, format, length, chapters, row_index)
                
            elif content_type == "social" or content_type == "socialmedia":
                # Process as social media post
                platform = content_item.get("Platform", "x")
                with_image = content_item.get("WithImage", "").lower() == "true"
                result = self._process_social_media(topic, platform, with_image, row_index)
                
            elif content_type == "instagram" or content_type == "insta":
                # Process as Instagram post
                post_type = content_item.get("PostType", "carousel")
                result = self._process_instagram(topic, post_type, row_index)
                
            elif content_type == "cardnews" or content_type == "cards":
                # Process as card news
                num_cards = int(content_item.get("NumCards", "5"))
                style = content_item.get("Style", "modern")
                result = self._process_card_news(topic, num_cards, style, row_index)
                
            else:
                result = {"success": False, "error": f"Unknown content type: {content_type}"}
                
            # Update spreadsheet status
            if result.get("success"):
                self.update_content_status(row_index, "completed")
                
                # Update URL if available
                if "url" in result:
                    self.update_content_url(row_index, result["url"])
                    
                # Update Dropbox link if available
                if "dropbox_link" in result and result["dropbox_link"]:
                    self.update_content_url(row_index, result["dropbox_link"], "Dropbox Link")
                    
            else:
                self.update_content_status(
                    row_index, 
                    f"failed: {result.get('error', 'unknown error')}"
                )
                
            return result
            
        except Exception as e:
            error_msg = str(e)
            self.update_content_status(
                row_index, 
                f"error: {error_msg}"
            )
            return {"success": False, "error": error_msg}
    
    def _process_shorts(self, topic, script, method, row_index):
        """
        Process a shorts content item.
        
        Args:
            topic (str): Topic for the shorts
            script (str): Optional pre-written script
            method (str): Method to use (story, knowledge, custom)
            row_index (int): Row index in spreadsheet
            
        Returns:
            dict: Result of shorts processing
        """
        # Create short using the specified method
        result = self.enhanced_shorts.create_short_by_method(
            method, 
            topic, 
            script, 
            None,  # custom_images
            True   # upload_to_dropbox
        )
        
        if result and "video_path" in result:
            return {
                "success": True,
                "video_path": result["video_path"],
                "title": result["title"],
                "description": result["description"],
                "type": result["type"],
                "dropbox_link": result.get("dropbox_link")
            }
        else:
            return {"success": False, "error": "Failed to create short"}
    
    def _process_blog(self, topic, length, row_index):
        """
        Process a blog content item.
        
        Args:
            topic (str): Topic for the blog post
            length (str): Length of the blog post
            row_index (int): Row index in spreadsheet
            
        Returns:
            dict: Result of blog processing
        """
        # Generate blog post
        blog_post = self.blog_generator.generate_blog_post(topic, length)
        
        # Save blog post files
        saved_files = self.blog_generator.save_blog_post(blog_post)
        
        # Simulate posting to blog
        post_result = self.blog_generator.post_to_blog(blog_post)
        
        # Upload featured image to Dropbox if available
        dropbox_link = None
        if self.dropbox_uploader.dbx and blog_post.get("image_path"):
            dropbox_path = f"/blog/{os.path.basename(blog_post['image_path'])}"
            upload_result = self.dropbox_uploader.upload_file(blog_post["image_path"], dropbox_path)
            
            if upload_result.get("success"):
                dropbox_link = upload_result.get("shared_link")
        
        if saved_files and "html_path" in saved_files:
            return {
                "success": True,
                "blog_post": blog_post,
                "saved_files": saved_files,
                "url": post_result.get("url") if post_result else None,
                "dropbox_link": dropbox_link
            }
        else:
            return {"success": False, "error": "Failed to create blog post"}
    
    def _process_ebook(self, topic, format, length, chapters, row_index):
        """
        Process an ebook content item.
        
        Args:
            topic (str): Topic for the ebook
            format (str): Output format (pdf, epub, mobi)
            length (str): Length of the ebook
            chapters (int): Number of chapters
            row_index (int): Row index in spreadsheet
            
        Returns:
            dict: Result of ebook processing
        """
        # Generate ebook
        ebook = self.ebook_generator.generate_ebook(topic, format, length, chapters)
        
        # Compile ebook
        compiled_files = self.ebook_generator.compile_ebook(ebook)
        
        # Simulate publishing ebook
        publish_result = self.ebook_generator.publish_ebook(ebook)
        
        # Upload ebook files to Dropbox
        dropbox_link = None
        if self.dropbox_uploader.dbx:
            # Upload the main format file if available
            main_format_file = compiled_files.get(format.lower())
            if main_format_file and os.path.exists(main_format_file):
                dropbox_path = f"/ebooks/{os.path.basename(main_format_file)}"
                upload_result = self.dropbox_uploader.upload_file(main_format_file, dropbox_path)
                
                if upload_result.get("success"):
                    dropbox_link = upload_result.get("shared_link")
            
            # Upload cover image if available
            if ebook.get("cover_path") and os.path.exists(ebook["cover_path"]):
                dropbox_path = f"/ebooks/covers/{os.path.basename(ebook['cover_path'])}"
                self.dropbox_uploader.upload_file(ebook["cover_path"], dropbox_path)
        
        if compiled_files:
            return {
                "success": True,
                "ebook": ebook,
                "compiled_files": compiled_files,
                "url": publish_result.get("url") if publish_result else None,
                "dropbox_link": dropbox_link
            }
        else:
            return {"success": False, "error": "Failed to create ebook"}
    
    def _process_social_media(self, topic, platform, with_image, row_index):
        """
        Process a social media content item.
        
        Args:
            topic (str): Topic for the post
            platform (str): Platform (x, twitter, threads)
            with_image (bool): Whether to include an image
            row_index (int): Row index in spreadsheet
            
        Returns:
            dict: Result of social media processing
        """
        if platform.lower() in ["x", "twitter"]:
            # Generate X post
            post_data = self.social_media_manager.generate_x_post(topic, with_image)
            
            # Upload image to Dropbox if available
            if self.dropbox_uploader.dbx and post_data.get("image_path"):
                dropbox_path = f"/social/x/{os.path.basename(post_data['image_path'])}"
                upload_result = self.dropbox_uploader.upload_file(post_data["image_path"], dropbox_path)
                
                if upload_result.get("success"):
                    post_data["dropbox_link"] = upload_result.get("shared_link")
            
            return {
                "success": True,
                "platform": "x",
                "text": post_data["text"],
                "image_path": post_data.get("image_path"),
                "dropbox_link": post_data.get("dropbox_link")
            }
            
        elif platform.lower() == "threads":
            # Generate Threads post
            post_data = self.social_media_manager.generate_threads_post(topic, 3, with_image)
            
            # Upload images to Dropbox if available
            dropbox_links = []
            for i, post in enumerate(post_data.get("posts", [])):
                if self.dropbox_uploader.dbx and post.get("image_path"):
                    dropbox_path = f"/social/threads/{os.path.basename(post['image_path'])}"
                    upload_result = self.dropbox_uploader.upload_file(post["image_path"], dropbox_path)
                    
                    if upload_result.get("success"):
                        post["dropbox_link"] = upload_result.get("shared_link")
                        dropbox_links.append(upload_result.get("shared_link"))
            
            return {
                "success": True,
                "platform": "threads",
                "posts": post_data.get("posts", []),
                "count": post_data.get("count", 0),
                "dropbox_link": dropbox_links[0] if dropbox_links else None
            }
            
        else:
            return {"success": False, "error": f"Unsupported platform: {platform}"}
    
    def _process_instagram(self, topic, post_type, row_index):
        """
        Process an Instagram content item.
        
        Args:
            topic (str): Topic for the post
            post_type (str): Type of post (single, carousel, story)
            row_index (int): Row index in spreadsheet
            
        Returns:
            dict: Result of Instagram processing
        """
        # Generate Instagram post
        post_data = self.social_media_manager.generate_instagram_post(topic, post_type)
        
        # Upload images to Dropbox
        dropbox_links = []
        for i, image_path in enumerate(post_data.get("images", [])):
            if self.dropbox_uploader.dbx and image_path:
                dropbox_path = f"/social/instagram/{os.path.basename(image_path)}"
                upload_result = self.dropbox_uploader.upload_file(image_path, dropbox_path)
                
                if upload_result.get("success"):
                    dropbox_links.append(upload_result.get("shared_link"))
        
        return {
            "success": True,
            "platform": "instagram",
            "post_type": post_type,
            "caption": post_data["caption"],
            "images": post_data.get("images", []),
            "image_count": len(post_data.get("images", [])),
            "dropbox_link": dropbox_links[0] if dropbox_links else None
        }
    
    def _process_card_news(self, topic, num_cards, style, row_index):
        """
        Process a card news content item.
        
        Args:
            topic (str): Topic for the cards
            num_cards (int): Number of cards to generate
            style (str): Style of the cards
            row_index (int): Row index in spreadsheet
            
        Returns:
            dict: Result of card news processing
        """
        # Generate card news
        card_data = self.card_news_generator.generate_card_news(topic, num_cards, style)
        
        # Upload cards to Dropbox
        dropbox_links = []
        for i, card in enumerate(card_data.get("cards", [])):
            if self.dropbox_uploader.dbx and card.get("path"):
                dropbox_path = f"/card_news/{os.path.basename(card['path'])}"
                upload_result = self.dropbox_uploader.upload_file(card["path"], dropbox_path)
                
                if upload_result.get("success"):
                    card["dropbox_link"] = upload_result.get("shared_link")
                    dropbox_links.append(upload_result.get("shared_link"))
        
        return {
            "success": True,
            "topic": topic,
            "style": style,
            "cards": card_data.get("cards", []),
            "count": card_data.get("count", 0),
            "dropbox_link": dropbox_links[0] if dropbox_links else None
        }
    
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
            all_content = self.get_content_data()
            
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
