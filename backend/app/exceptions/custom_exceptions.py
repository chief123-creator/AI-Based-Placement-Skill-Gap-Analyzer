from fastapi import HTTPException

class ResumeParseError(HTTPException):
    def __init__(self):
        super().__init__(status_code=422, detail="Resume parsing failed")

class SkillExtractionError(HTTPException):
    def __init__(self):
        super().__init__(status_code=422, detail="Skill extraction failed")
