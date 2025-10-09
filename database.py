from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///resumes.db')
Session = sessionmaker(bind=engine)

class Resume(Base):
    __tablename__ = 'resumes'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    skills = Column(Text)      # Matches existing DB
    experience = Column(Text)  # Matches existing DB  
    education = Column(Text)   # Matches existing DB

Base.metadata.create_all(engine)

def store_resume(data):
    """Store or update resume in database"""
    session = Session()
    try:
        # Check if resume already exists
        existing = session.query(Resume).filter_by(name=data.get('name', 'Unknown')).first()
        
        if existing:
            # Update existing resume
            existing.skills = str(data.get('skills', []))
            existing.experience = str(data.get('experience', []))
            existing.education = str(data.get('education', []))
            print(f"Updated existing resume for {existing.name}")
        else:
            # Create new resume
            resume = Resume(
                name=data.get('name', 'Unknown'),
                skills=str(data.get('skills', [])),
                experience=str(data.get('experience', [])),
                education=str(data.get('education', []))
            )
            session.add(resume)
            print(f"Added new resume for {resume.name}")
        
        session.commit()
    finally:
        session.close()