# Smart Resume Screener

An intelligent resume screening and matching system powered by GPT-4o that automates candidate evaluation by extracting structured information from resumes and computing comprehensive fit scores against job descriptions.

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Core Features](#core-features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Matching Algorithm](#matching-algorithm)
- [Development](#development)
- [Testing](#testing)

## Overview

Smart Resume Screener is a full-stack application designed to streamline the resume screening process through intelligent parsing and matching. The system leverages GPT-4o for advanced natural language understanding to extract structured data from resumes and compute multi-dimensional fit scores based on skills, experience, education, and other relevant criteria.

### Key Capabilities

- **Intelligent Resume Parsing**: Extract structured information including personal details, skills, work experience, education, projects, and certifications
- **Job Description Analysis**: Parse and structure job requirements, responsibilities, and qualifications
- **Multi-Dimensional Matching**: Compute comprehensive fit scores across multiple dimensions including skills, experience, education, and soft skills
- **Batch Processing**: Efficiently process multiple resumes against a single job description
- **Persistent Storage**: MongoDB-based data persistence for resumes, job descriptions, and match results
- **RESTful API**: Comprehensive API endpoints for all system operations
- **Modern UI**: React-based frontend with interactive dashboard and analytics

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │          React Frontend (Port 3000)                       │  │
│  │  - Dashboard  - Upload UI  - Results Viewer              │  │
│  │  - Analytics  - Batch Processing Interface                │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP/REST
┌──────────────────────────▼──────────────────────────────────────┐
│                      Application Layer                           │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │        FastAPI Backend (Port 8000)                        │  │
│  │                                                            │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │  │
│  │  │   Parser     │  │   Matcher    │  │  Database    │   │  │
│  │  │   Module     │  │   Module     │  │   Module     │   │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │  │
│  │         │                  │                  │           │  │
│  │         └──────────────────┴──────────────────┘           │  │
│  │                        │                                  │  │
│  │                        ▼                                  │  │
│  │              ┌──────────────────┐                         │  │
│  │              │   OpenAI GPT-4o  │                         │  │
│  │              │   API Client     │                         │  │
│  │              └──────────────────┘                         │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │ MongoDB Protocol
┌──────────────────────────▼──────────────────────────────────────┐
│                       Data Layer                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              MongoDB Atlas Database                       │  │
│  │  - resumes collection                                     │  │
│  │  - job_descriptions collection                            │  │
│  │  - match_results collection                               │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Component Architecture

#### Backend Layer (FastAPI)

**Core Modules:**

1. **main.py** - Application entry point and API router
   - Initializes FastAPI application
   - Configures CORS middleware
   - Defines REST API endpoints
   - Handles request validation and error responses

2. **parser.py** - Document parsing engine
   - PDF text extraction using pdfplumber
   - GPT-4o integration for structured data extraction
   - Schema validation and data normalization
   - Support for multiple document formats

3. **matcher.py** - Matching and scoring engine
   - Job description requirement extraction
   - Resume-to-job matching algorithm
   - Multi-dimensional score calculation
   - Batch processing capabilities

4. **db.py** - Database abstraction layer
   - MongoDB connection management
   - CRUD operations for all collections
   - Connection pooling and error handling
   - Data validation and sanitization

5. **models.py** - Data models and schemas
   - Pydantic models for request/response validation
   - MongoDB document schemas
   - Type definitions and validators

#### Frontend Layer (React)

**Architecture Pattern:** Component-based architecture with context API for state management

**Key Components:**

- **Dashboard**: Overview and analytics
- **Upload Interface**: File upload with drag-and-drop
- **Results Viewer**: Match results with detailed breakdowns
- **Batch Processing**: Multi-resume processing interface

**State Management:** React Context API for global state

**Styling:** CSS modules with responsive design

#### Data Layer (MongoDB Atlas)

**Collections:**

1. **resumes**
   - Parsed resume data with structured fields
   - Skills array, experience history, education records
   - Metadata: upload timestamp, file information

2. **job_descriptions**
   - Structured job requirements
   - Skills requirements, experience criteria
   - Company and role information

3. **match_results**
   - Resume-job pair matching scores
   - Dimensional breakdowns
   - Timestamps and matching metadata

## Technology Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Core programming language |
| FastAPI | 0.119.0 | Web framework and REST API |
| Pydantic | 2.12.0 | Data validation and serialization |
| pymongo | 4.15.3 | MongoDB driver |
| OpenAI API | 2.3.0 | GPT-4o integration for NLP |
| pdfplumber | 0.11.7 | PDF text extraction |
| spaCy | 3.8.7 | NLP processing |
| uvicorn | 0.37.0 | ASGI server |

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19.2.0 | UI framework |
| Ant Design | 5.27.5 | Component library |
| Axios | 1.12.2 | HTTP client |
| React Router | 7.9.4 | Client-side routing |
| Chart.js | 4.5.1 | Data visualization |
| Framer Motion | 12.23.24 | Animation library |

### Database

| Technology | Version | Purpose |
|------------|---------|---------|
| MongoDB Atlas | 8.0+ | Cloud-hosted NoSQL database |

### External Services

| Service | Purpose |
|---------|---------|
| OpenAI GPT-4o | Intelligent text parsing and extraction |
| MongoDB Atlas | Cloud database hosting |

## Core Features

### Resume Parsing

**Extraction Capabilities:**
- Personal information (name, email, phone, location)
- Professional summary
- Technical and soft skills
- Work experience with detailed role descriptions
- Educational background
- Projects and achievements
- Certifications and licenses

**Processing Flow:**
1. PDF text extraction using pdfplumber
2. Text normalization and cleaning
3. GPT-4o API call with structured prompt
4. JSON response parsing and validation
5. Storage in MongoDB

### Job Description Analysis

**Extracted Elements:**
- Job title and company information
- Required technical skills
- Experience requirements
- Educational qualifications
- Soft skills and competencies
- Responsibilities and duties

### Intelligent Matching

**Scoring Dimensions:**
- **Skills Match** (40%): Technical and soft skills alignment
- **Experience Match** (30%): Years of experience and role relevance
- **Education Match** (20%): Degree level and field of study
- **Overall Fit** (10%): Holistic assessment

**Score Range:** 0-100 with detailed breakdown per dimension

### Batch Processing

Process multiple resumes against a single job description with:
- Parallel processing support
- Progress tracking
- Aggregate statistics
- Export to CSV functionality

## Project Structure

```
Smart-Resume-Screener/
├── backend/
│   ├── main.py                 # FastAPI application and routes
│   ├── parser.py               # Resume and JD parsing logic
│   ├── matcher.py              # Matching algorithm implementation
│   ├── db.py                   # MongoDB operations
│   ├── models.py               # Pydantic data models
│   ├── test_db.py              # Database connection tests
│   ├── test_mongo_connection.py # MongoDB connectivity tests
│   └── frontend/
│       ├── public/             # Static assets
│       ├── src/
│       │   ├── components/     # React components
│       │   ├── contexts/       # Context providers
│       │   ├── pages/          # Page components
│       │   ├── services/       # API client services
│       │   └── styles/         # CSS modules
│       └── package.json        # Frontend dependencies
├── docs/
│   ├── INSTALLATION_SUMMARY.md
│   ├── MONGODB_ATLAS_SETUP.md
│   ├── Phase3_Completion_Summary.md
│   ├── Phase4_Step1_OpenAI_Setup.md
│   ├── Phase4_Step2_Prompt_Engineering.md
│   └── SECURITY.md
├── samples/                    # Sample resumes for testing
├── srs-env/                    # Python virtual environment
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── SETUP.md                    # Setup instructions
```

## Installation

### Prerequisites

- Python 3.11 or higher
- Node.js 16+ and npm
- MongoDB Atlas account
- OpenAI API key

### Backend Setup

1. **Clone the repository:**
```bash
git clone https://github.com/Soumik-R/Smart-Resume-Screener.git
cd Smart-Resume-Screener
```

2. **Create and activate virtual environment:**
```bash
python -m venv srs-env
# Windows
srs-env\Scripts\activate
# Linux/Mac
source srs-env/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

4. **Configure environment variables:**
```bash
cd backend
cp .env.example .env
# Edit .env with your credentials
```

5. **Start the backend server:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd backend/frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start the development server:**
```bash
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Configuration

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o

# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DB_NAME=smart_resume_screener

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
MAX_FILE_SIZE_MB=5

# Security
API_KEY=your_api_key_here
```

### MongoDB Setup

Refer to `docs/MONGODB_ATLAS_SETUP.md` for detailed MongoDB Atlas configuration instructions.

## API Documentation

Full API documentation available at: http://localhost:8000/docs

## Matching Algorithm

### Algorithm Overview

The matching algorithm employs a multi-dimensional scoring approach that evaluates candidate fit across several key dimensions.

### Scoring Components

#### 1. Skills Match (40% weight)

**Process:**
- Extract required skills from job description
- Identify candidate skills from resume
- Calculate intersection and coverage
- Apply weighted scoring based on skill categories

**Formula:**
```
skills_score = (matched_skills / required_skills) × 100
weighted_skills = skills_score × 0.40
```

#### 2. Experience Match (30% weight)

**Evaluation Criteria:**
- Years of relevant experience
- Role title similarity
- Industry alignment
- Responsibility overlap

**Formula:**
```
experience_score = min(candidate_years / required_years, 1.0) × 100
weighted_experience = experience_score × 0.30
```

#### 3. Education Match (20% weight)

**Assessment Factors:**
- Degree level comparison
- Field of study relevance
- Institution reputation (if specified)
- Additional certifications

**Formula:**
```
education_score = degree_match × field_match × 100
weighted_education = education_score × 0.20
```

#### 4. Overall Fit (10% weight)

**Holistic Assessment:**
- Soft skills alignment
- Cultural fit indicators
- Career trajectory
- Additional qualifications

### Final Score Calculation

```
final_score = (weighted_skills + weighted_experience + 
               weighted_education + weighted_overall_fit)
```

### Score Interpretation

| Score Range | Interpretation | Recommendation |
|-------------|----------------|----------------|
| 90-100 | Excellent match | Strong candidate - immediate interview |
| 75-89 | Good match | Qualified candidate - consider for interview |
| 60-74 | Moderate match | Potential candidate - review carefully |
| 40-59 | Weak match | May lack key qualifications |
| 0-39 | Poor match | Not recommended |

## Development

### Running in Development Mode

**Backend:**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd backend/frontend
npm start
```

### Code Style

- Python: PEP 8 compliant
- JavaScript: ESLint with React configuration
- Format: Use Prettier for frontend code

### Adding New Features

1. **Backend Endpoint:**
   - Add route in `main.py`
   - Implement logic in appropriate module
   - Update models in `models.py`
   - Update API documentation

2. **Frontend Component:**
   - Create component in `src/components`
   - Add routing in `App.js`
   - Implement API calls in `src/services`
   - Update context if needed

## Testing

### Backend Tests

**Database Connection:**
```bash
cd backend
python test_db.py
python test_mongo_connection.py
```

**API Tests:**
```bash
python test_api_step3.py
```

**Verification Scripts:**
```bash
python verify_step3.py
python verify_step4.py
```

### Frontend Tests

```bash
cd backend/frontend
npm test
```

### Manual Testing

1. Upload a sample resume from `samples/` directory
2. Create a job description
3. Run matching and verify scores
4. Test batch processing with multiple resumes

## Documentation

Comprehensive documentation available in the `docs/` directory:

- **INSTALLATION_SUMMARY.md**: Detailed installation guide
- **MONGODB_ATLAS_SETUP.md**: MongoDB configuration
- **SECURITY.md**: Security best practices
- **Phase3_Completion_Summary.md**: Development milestones
- **Phase4_Step1_OpenAI_Setup.md**: OpenAI integration guide
- **Phase4_Step2_Prompt_Engineering.md**: Prompt optimization

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes with clear commit messages
4. Add tests for new functionality
5. Submit a pull request

## Acknowledgments

- OpenAI for GPT-4o API
- MongoDB Atlas for database hosting
- FastAPI framework contributors
- React and Ant Design communities
