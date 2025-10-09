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
    resume = Resume(
        name=data.get('name', 'Unknown'),
        skills=str(data['skills']),
        experience=str(data['experience']),
        education=str(data['education'])
    )
    session.add(resume)
    session.commit()
    session.close()