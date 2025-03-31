import os
import json
import requests
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError
from src.constants import ROOT_DIR

class DropboxUploader:
    """
    Class for uploading files to Dropbox.
    """
    def __init__(self, access_token=None):
        """
        Initialize the Dropbox uploader.
        
        Args:
            access_token (str): Dropbox API access token
        """
        self.access_token = access_token
        self.dbx = None
        
        if self.access_token:
            self.connect()
    
    def connect(self, access_token=None):
        """
        Connect to Dropbox API.
        
        Args:
            access_token (str): Dropbox API access token
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        if access_token:
            self.access_token = access_token
            
        if not self.access_token:
            print("No access token provided")
            return False
            
        try:
            self.dbx = dropbox.Dropbox(self.access_token)
            # Check that the access token is valid
            self.dbx.users_get_current_account()
            return True
        except AuthError:
            print("Invalid access token")
            return False
        except Exception as e:
            print(f"Error connecting to Dropbox: {e}")
            return False
    
    def upload_file(self, file_path, dropbox_path=None):
        """
        Upload a file to Dropbox.
        
        Args:
            file_path (str): Path to the local file
            dropbox_path (str): Path in Dropbox where the file should be uploaded
            
        Returns:
            dict: Upload result with shared link if successful
        """
        if not self.dbx:
            print("Not connected to Dropbox")
            return {"success": False, "error": "Not connected to Dropbox"}
            
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return {"success": False, "error": f"File not found: {file_path}"}
            
        # If no Dropbox path is provided, use the filename
        if not dropbox_path:
            dropbox_path = f"/{os.path.basename(file_path)}"
            
        # Make sure the Dropbox path starts with a slash
        if not dropbox_path.startswith('/'):
            dropbox_path = f"/{dropbox_path}"
            
        try:
            # Upload the file
            with open(file_path, 'rb') as f:
                print(f"Uploading {file_path} to Dropbox as {dropbox_path}")
                self.dbx.files_upload(f.read(), dropbox_path, mode=WriteMode('overwrite'))
                
            # Create a shared link
            shared_link = self.dbx.sharing_create_shared_link_with_settings(dropbox_path)
            
            return {
                "success": True,
                "path": dropbox_path,
                "shared_link": shared_link.url,
                "name": os.path.basename(file_path)
            }
            
        except ApiError as e:
            print(f"API error: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            print(f"Error uploading file: {e}")
            return {"success": False, "error": str(e)}
    
    def create_folder(self, folder_path):
        """
        Create a folder in Dropbox.
        
        Args:
            folder_path (str): Path of the folder to create
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.dbx:
            print("Not connected to Dropbox")
            return False
            
        # Make sure the path starts with a slash
        if not folder_path.startswith('/'):
            folder_path = f"/{folder_path}"
            
        try:
            self.dbx.files_create_folder_v2(folder_path)
            return True
        except Exception as e:
            print(f"Error creating folder: {e}")
            return False
    
    def list_folder(self, folder_path=""):
        """
        List contents of a folder in Dropbox.
        
        Args:
            folder_path (str): Path of the folder to list
            
        Returns:
            list: List of files and folders
        """
        if not self.dbx:
            print("Not connected to Dropbox")
            return []
            
        # Make sure the path starts with a slash
        if folder_path and not folder_path.startswith('/'):
            folder_path = f"/{folder_path}"
            
        try:
            result = self.dbx.files_list_folder(folder_path)
            files = []
            
            for entry in result.entries:
                entry_type = "folder" if isinstance(entry, dropbox.files.FolderMetadata) else "file"
                files.append({
                    "name": entry.name,
                    "path": entry.path_display,
                    "type": entry_type
                })
                
            return files
        except Exception as e:
            print(f"Error listing folder: {e}")
            return []
