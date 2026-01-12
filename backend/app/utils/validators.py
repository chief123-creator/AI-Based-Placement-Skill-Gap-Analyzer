# backend/app/utils/validators.py
import os
import re
from typing import Tuple
from fastapi import UploadFile, HTTPException

# ALLOWED_FILE_TYPES and their extensions
ALLOWED_FILE_TYPES = {
    'application/pdf': 'pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'application/msword': 'doc'
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_resume_file(file: UploadFile) -> Tuple[str, str]:
    """
    Validate uploaded resume file
    
    Returns: (file_extension, mime_type)
    Raises: HTTPException if invalid
    """
    # Check file exists and has name
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file name provided"
        )
    
    # Read file content for validation
    file_content = file.file.read(2048)
    file.file.seek(0)  # Reset pointer
    
    # Simple MIME type detection based on content
    mime_type = None
    
    # Check for PDF (starts with %PDF)
    if file_content.startswith(b'%PDF'):
        mime_type = 'application/pdf'
    
    # Check for DOCX (is a zip file with specific structure)
    elif file_content.startswith(b'PK'):  # ZIP file signature
        # Check if it's a DOCX by looking for word/document.xml in zip
        mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    
    # Check for DOC (old format)
    elif b'Microsoft Word' in file_content[:1000]:
        mime_type = 'application/msword'
    
    # Check file extension as fallback
    if not mime_type:
        filename = file.filename.lower()
        if filename.endswith('.pdf'):
            mime_type = 'application/pdf'
        elif filename.endswith('.docx'):
            mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif filename.endswith('.doc'):
            mime_type = 'application/msword'
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: PDF, DOCX. Got: {filename}"
            )
    
    # Check if MIME type is allowed
    if mime_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: PDF, DOCX. Got: {mime_type}"
        )
    
    # Get file extension
    file_extension = ALLOWED_FILE_TYPES[mime_type]
    
    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset pointer
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    if file_size == 0:
        raise HTTPException(
            status_code=400,
            detail="File is empty"
        )
    
    return file_extension, mime_type

def generate_unique_filename(user_id: int, original_filename: str) -> str:
    """
    Generate unique filename to avoid collisions
    Format: userid_timestamp_random_originalname
    """
    import time
    import uuid
    
    # Get safe filename
    name, ext = os.path.splitext(original_filename)
    # Remove any path components and keep only filename
    name = os.path.basename(name)
    # Clean filename (keep only safe characters)
    safe_name = re.sub(r'[^\w\-\.]', '_', name)
    
    # Generate unique filename
    timestamp = int(time.time())
    unique_id = str(uuid.uuid4())[:8]
    
    return f"{user_id}_{timestamp}_{unique_id}_{safe_name}{ext}"