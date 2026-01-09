# backend/app/services/file_handler.py
import os
from pathlib import Path
from fastapi import UploadFile, HTTPException
from typing import Dict
import uuid
from datetime import datetime

from app.utils.validators import validate_resume_file, generate_unique_filename

class FileHandler:
    def __init__(self):
        # Use absolute path for reliability
        current_dir = Path(__file__).parent.parent.parent  # backend directory
        self.base_upload_dir = current_dir / "uploads" / "resumes"
        self.base_upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_uploaded_file(self, file: UploadFile, user_id: int) -> Dict[str, str | int]:
        """
        Save uploaded file to disk and return file info
        """
        file_path = None
        try:
            # Validate file
            file_extension, mime_type = validate_resume_file(file)
            
            # Generate unique filename
            filename = file.filename or "document"
            unique_filename = generate_unique_filename(user_id, filename)
            file_path = self.base_upload_dir / unique_filename
            
            # Save file to disk
            with open(file_path, "wb") as buffer:
                # Read file in chunks to handle large files
                file.file.seek(0)
                chunk_size = 1024 * 1024  # 1MB chunks
                while chunk := file.file.read(chunk_size):
                    buffer.write(chunk)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            return {
                "original_filename": filename,
                "stored_filename": unique_filename,
                "file_path": str(file_path),
                "relative_path": f"uploads/resumes/{unique_filename}",
                "file_size": file_size,
                "file_type": file_extension,
                "mime_type": mime_type
            }
            
        except HTTPException:
            raise  # Re-raise validation errors
        except Exception as e:
            # Clean up if file was partially saved
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=500, 
                detail=f"File upload failed: {str(e)}"
            )
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete file from disk
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception:
            return False
    
    def file_exists(self, file_path: str) -> bool:
        """
        Check if file exists
        """
        path = Path(file_path)
        return path.exists()

# Create singleton instance
file_handler = FileHandler()