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
    skills = Column(Text)
    experience = Column(Text)
    education = Column(Text)

Base.metadata.create_all(engine)

def store_resume(data):
    session = Session()
    name = data.get('name', 'Unknown')
    
    # Check if resume with same name already exists
    existing_resume = session.query(Resume).filter_by(name=name).first()
    
    if existing_resume:
        # Update existing resume
        existing_resume.skills = str(data['skills'])
        existing_resume.experience = str(data['experience'])
        existing_resume.education = str(data['education'])
        print(f"Updated existing resume for {name}")
    else:
        # Create new resume
        resume = Resume(
            name=name,
            skills=str(data['skills']),
            experience=str(data['experience']),
            education=str(data['education'])
        )
        session.add(resume)
        print(f"Created new resume for {name}")
    
    session.commit()
    session.close()