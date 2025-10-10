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
    raw_text = Column(Text)
    hard_skills = Column(Text)
    education = Column(Text)
    projects = Column(Text)
    soft_skills = Column(Text)
    growth_verbs = Column(Text)
    certifications = Column(Text)  # New field

Base.metadata.create_all(engine)

def store_resume(data):
    session = Session()
    resume = Resume(
        name=data.get('name', 'Unknown'),
        raw_text=data['raw_text'],
        hard_skills=str(data['hard_skills']),
        education=str(data['education']),
        projects=str(data['projects']),
        soft_skills=str(data['soft_skills']),
        growth_verbs=str(data['growth_verbs']),
        certifications=str(data['certifications'])
    )
    session.add(resume)
    session.commit()
    session.close()