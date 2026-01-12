from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document
import re
from typing import Optional


class TextExtractor:
    """Extract and clean text from PDF and DOCX files"""
    
    @staticmethod
    def extract(file_path: str) -> str:
        """
        Auto-detect file type and extract text
        
        Args:
            file_path: Path to the resume file
            
        Returns:
            Cleaned extracted text
        """
        if file_path.lower().endswith('.pdf'):
            return TextExtractor._extract_from_pdf(file_path)
        elif file_path.lower().endswith(('.docx', '.doc')):
            return TextExtractor._extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
    
    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            text = extract_pdf_text(file_path)
            return TextExtractor._clean_text(text)
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")
    
    @staticmethod
    def _extract_from_docx(file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            # Extract text from paragraphs
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            text = "\n".join(paragraphs)
            return TextExtractor._clean_text(text)
        except Exception as e:
            raise Exception(f"DOCX extraction failed: {str(e)}")
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Clean extracted text
        - Remove excessive whitespace
        - Remove URLs
        - Keep important punctuation
        """
        if not text:
            return ""
        
        # Remove URLs
        text = re.sub(r'http\S+|www\.\S+', '', text)
        
        # Replace multiple spaces/tabs/newlines with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep: letters, numbers, basic punctuation
        text = re.sub(r'[^\w\s\.\,\-\+\#\(\)\/\:]', '', text)
        
        return text.strip()
