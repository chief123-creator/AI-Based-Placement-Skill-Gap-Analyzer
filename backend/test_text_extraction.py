from app.services.resume_parser import ResumeParser
from app.database import SessionLocal

# Test file
file_path = "D:\\AI-Based-Placement-Skill-Gap-Analyzer-main\\backend\\test_sample.pdf"

# Parse resume
db = SessionLocal()
parser = ResumeParser(db)

result = parser.parse(file_path)

print("=" * 50)
print("RESUME PARSING RESULT")
print("=" * 50)
print(f"Text length: {len(result['extracted_text'])} characters")
print(f"Total skills found: {result['parsed_sections']['skill_count']}")
print(f"\nSkills: {result['parsed_sections']['skills']}")
print(f"\nSkills by category:")
for category, skills in result['parsed_sections']['skills_by_category'].items():
    print(f"  {category}: {skills}")

db.close()
