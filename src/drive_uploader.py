"""
Google Drive uploader for Anki deck files.
"""
import os
import json
from typing import Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


SCOPES = ['https://www.googleapis.com/auth/drive.file']


class DriveUploader:
    """Upload files to Google Drive."""
    
    def __init__(self, credentials_json: str, folder_id: Optional[str] = None):
        """
        Initialize the Drive uploader.
        
        Args:
            credentials_json: JSON string of service account credentials
            folder_id: Optional folder ID to upload to (uses root if not specified)
        """
        creds_dict = json.loads(credentials_json)
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict, scopes=SCOPES
        )
        self.service = build('drive', 'v3', credentials=credentials)
        self.folder_id = folder_id
    
    def upload_file(self, filepath: str, filename: Optional[str] = None) -> str:
        """
        Upload a file to Google Drive.
        
        Args:
            filepath: Local path to the file
            filename: Name to use in Drive (defaults to original filename)
        
        Returns:
            File ID of the uploaded file
        """
        if filename is None:
            filename = os.path.basename(filepath)
        
        file_metadata = {'name': filename}
        
        if self.folder_id:
            file_metadata['parents'] = [self.folder_id]
        
        # Check if file already exists, update if so
        existing_file_id = self._find_file(filename)
        
        media = MediaFileUpload(
            filepath,
            mimetype='application/octet-stream',
            resumable=True
        )
        
        if existing_file_id:
            # Update existing file
            file = self.service.files().update(
                fileId=existing_file_id,
                media_body=media
            ).execute()
        else:
            # Create new file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id',
                                supportsAllDrives=True
            ).execute()
        
        return file.get('id')
    
    def _find_file(self, filename: str) -> Optional[str]:
        """Find a file by name in the target folder."""
        query = f"name = '{filename}' and trashed = false"
        
        if self.folder_id:
            query += f" and '{self.folder_id}' in parents"
        
        results = self.service.files().list(
            q=query,
            fields="files(id, name)",
                        supportsAllDrives=True,
                        includeItemsFromAllDrives=True
        ).execute()
        
        files = results.get('files', [])
        if files:
            return files[0]['id']
        return None
    
    def create_folder(self, folder_name: str) -> str:
        """
        Create a folder in Google Drive.
        
        Returns the folder ID.
        """
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if self.folder_id:
            file_metadata['parents'] = [self.folder_id]
        
        file = self.service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()
        
        return file.get('id')

