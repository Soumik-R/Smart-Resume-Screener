# 🏗️ Project Architecture Documentation

## Smart Resume Screener - Technical Architecture

**Version**: 1.0.0  
**Last Updated**: October 17, 2025  
**Author**: SOUMIK ROY

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Patterns](#architecture-patterns)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [API Design](#api-design)
6. [Database Schema](#database-schema)
7. [Security Architecture](#security-architecture)
8. [Performance Optimization](#performance-optimization)

---

## 🎯 System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         React Frontend (Port 3000)                │  │
│  │  - Dashboard UI                                   │  │
│  │  - Upload Interface                               │  │
│  │  - Data Visualization                             │  │
│  │  - State Management (React Context)               │  │
│  └───────────────────┬──────────────────────────────┘  │
└────────────────────────┼───────────────────────────────┘
                         │ HTTP/REST
                         │ JSON Payloads
┌────────────────────────┼───────────────────────────────┐
│              APPLICATION LAYER                          │
│  ┌───────────────────▼──────────────────────────────┐  │
│  │      FastAPI Backend (Port 8000)                  │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐       │  │
│  │  │  Parser  │  │ Matcher  │  │    DB    │       │  │
│  │  │  Module  │  │  Module  │  │  Module  │       │  │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘       │  │
│  │       │             │              │              │  │
│  │       └─────────────┼──────────────┘              │  │
│  │                     │                             │  │
│  │         ┌───────────▼───────────┐                 │  │
│  │         │  Claude Sonnet 4.5    │                 │  │
│  │         │  AI Engine            │                 │  │
│  │         │  (Anthropic API)      │                 │  │
│  │         └───────────────────────┘                 │  │
│  └──────────────────────┬──────────────────────────┘  │
└─────────────────────────┼────────────────────────────┘
                          │ MongoDB Protocol
┌─────────────────────────┼────────────────────────────┐
│                  DATA LAYER                            │
│  ┌───────────────────▼──────────────────────────────┐ │
│  │         PostgreSQL Database                       │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐ │ │
│  │  │  Resumes   │  │ Job Desc   │  │  Matches   │ │ │
│  │  │  Table     │  │  Table     │  │   Table    │ │ │
│  │  └────────────┘  └────────────┘  └────────────┘ │ │
│  └──────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────┘
```

---

## 🏛️ Architecture Patterns

### 1. **Layered Architecture**

```
┌─────────────────────────────────────┐
│    Presentation Layer (React)        │
│    - UI Components                   │
│    - State Management                │
│    - Client-side Routing             │
├─────────────────────────────────────┤
│    API Layer (FastAPI)               │
│    - Request Handling                │
│    - Input Validation                │
│    - Response Formatting             │
├─────────────────────────────────────┤
│    Business Logic Layer              │
│    - Resume Parsing                  │
│    - Candidate Matching              │
│    - Score Calculation               │
├─────────────────────────────────────┤
│    Data Access Layer                 │
│    - Database Operations             │
│    - Query Optimization              │
│    - Connection Pooling              │
├─────────────────────────────────────┤
│    External Services Layer           │
│    - Claude AI API                   │
│    - File Storage                    │
│    - Email Services (future)         │
└─────────────────────────────────────┘
```

### 2. **RESTful API Design**

**Principles Applied**:
- Resource-based URLs
- HTTP methods for CRUD operations
- Stateless communication
- JSON data interchange
- Proper HTTP status codes

### 3. **MVC Pattern (Backend)**

```
Model (models.py)
├── Resume
├── JobDescription
├── MatchResult
└── Pydantic Schemas

View (main.py - API Routes)
├── Upload Routes
├── Processing Routes
├── Query Routes
└── Export Routes

Controller (parser.py, matcher.py, db.py)
├── Resume Parser
├── Matching Engine
└── Database Manager
```

---

## 🔧 Component Details

### Backend Components

#### 1. **main.py** - API Gateway
```python
"""
FastAPI Application Entry Point

Responsibilities:
- Initialize FastAPI app with CORS middleware
- Define all API routes and endpoints
- Handle request validation using Pydantic
- Implement error handling and logging
- Configure OpenAPI documentation

Architecture Pattern: API Gateway Pattern
"""

# Key Components:
app = FastAPI(
    title="Smart Resume Screener API",
    version="1.0.0",
    description="AI-powered candidate evaluation system"
)

# CORS Configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Routes organized by functionality:
# 1. Upload Routes: /api/upload
# 2. Processing Routes: /api/process
# 3. Query Routes: /api/shortlist, /api/stats
# 4. Export Routes: /api/export
# 5. Management Routes: /api/delete, /api/update
```

#### 2. **parser.py** - Document Processing Engine
```python
"""
Resume and Job Description Parser

Responsibilities:
- Extract text from PDF/DOCX files
- Clean and normalize text data
- Use Claude AI for structured extraction
- Validate extracted data against schema
- Handle multiple file formats

Architecture Pattern: Strategy Pattern for different file types
"""

# Text Extraction Strategies:
class PDFExtractor:
    """Extract text from PDF using PyPDF2"""
    
class DOCXExtractor:
    """Extract text from DOCX using python-docx"""
    
class TXTExtractor:
    """Extract text from plain text files"""

# AI-Powered Extraction:
def extract_resume_data(text: str) -> dict:
    """
    Use Claude Sonnet 4.5 to extract structured data
    
    Prompt Engineering:
    - Specific field requirements
    - JSON output format
    - Handling missing data
    - Validation rules
    """
```

#### 3. **matcher.py** - Intelligent Matching Engine
```python
"""
Resume-Job Description Matching Engine

Responsibilities:
- Parse job requirements from description
- Compare candidate profile with requirements
- Calculate multi-dimensional scores
- Generate justification and feedback
- Rank candidates based on scores

Architecture Pattern: Template Method Pattern
"""

# Matching Algorithm:
def match_candidate(resume: dict, jd: dict) -> dict:
    """
    Multi-dimensional matching algorithm
    
    Steps:
    1. Extract JD requirements
    2. Prepare comparison prompt for AI
    3. Get scores from Claude API
    4. Calculate weighted overall score
    5. Generate detailed feedback
    
    Scoring Formula:
    Overall = Σ(weight_i × score_i)
    where i ∈ {skills, experience, education, culture, achievements}
    """
```

#### 4. **db.py** - Database Abstraction Layer
```python
"""
PostgreSQL Database Operations

Responsibilities:
- Manage database connections
- Implement CRUD operations
- Handle transactions
- Optimize queries
- Connection pooling

Architecture Pattern: Repository Pattern
"""

# Repository Pattern Implementation:
class ResumeRepository:
    """Handle all resume-related database operations"""
    
class JobDescriptionRepository:
    """Handle all JD-related database operations"""
    
class MatchRepository:
    """Handle all match result operations"""

# Connection Management:
def get_db_connection():
    """
    Create and return database connection
    Uses connection pooling for performance
    """
```

#### 5. **models.py** - Data Models & Validation
```python
"""
Pydantic Models for Data Validation

Responsibilities:
- Define request/response schemas
- Implement field validation
- Type checking
- Default values
- Custom validators

Architecture Pattern: Data Transfer Object (DTO) Pattern
"""

# Request Models:
class UploadRequest(BaseModel):
    """Validate file upload requests"""
    
class ProcessRequest(BaseModel):
    """Validate processing requests"""

# Response Models:
class MatchResponse(BaseModel):
    """Structure for match result responses"""
    
class ShortlistResponse(BaseModel):
    """Structure for candidate shortlist"""

# Database Models:
class Resume(BaseModel):
    """Resume database schema"""
    
class JobDescription(BaseModel):
    """Job description database schema"""
```

---

### Frontend Components

#### 1. **App.js** - Root Component
```jsx
/**
 * Application Root Component
 * 
 * Responsibilities:
 * - Setup routing configuration
 * - Provide global context
 * - Initialize state management
 * - Define layout structure
 * 
 * Architecture Pattern: Container/Presentational Pattern
 */

function App() {
    return (
        <BrowserRouter>
            <Layout>
                <Header /> {/* Navigation bar */}
                <Content>
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/upload" element={<Upload />} />
                        <Route path="/dashboard/:jdId" element={<Dashboard />} />
                    </Routes>
                </Content>
                <Footer />
            </Layout>
        </BrowserRouter>
    );
}
```

#### 2. **Dashboard.js** - Main Dashboard
```jsx
/**
 * Dashboard Component - Main Results Viewer
 * 
 * Responsibilities:
 * - Display candidate shortlist
 * - Show statistical analytics
 * - Render radar charts
 * - Implement filters and search
 * - Handle What-If simulations
 * - Export functionality
 * 
 * State Management:
 * - candidates: List of matched candidates
 * - statistics: Aggregate stats
 * - filters: Active filters (threshold, search)
 * - selectedCandidate: For detail view
 * 
 * Components Used:
 * - Table (Ant Design)
 * - Statistics Cards
 * - RadarChart (Recharts)
 * - Modal (Ant Design)
 * - Button, Input, Select (Ant Design)
 */

const Dashboard = () => {
    const { jdId } = useParams();
    const [candidates, setCandidates] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState({
        threshold: 7.0,
        search: ''
    });
    
    // Fetch data from API
    useEffect(() => {
        fetchShortlist(jdId);
    }, [jdId]);
    
    // Render components
    return (
        <div className="dashboard">
            <StatisticsRow data={statistics} />
            <FiltersSection filters={filters} onChange={handleFilterChange} />
            <ShortlistTable data={filteredCandidates} />
            <RadarChartSection data={selectedCandidate} />
        </div>
    );
};
```

#### 3. **services/api.js** - API Service Layer
```javascript
/**
 * Centralized API Service
 * 
 * Responsibilities:
 * - Configure Axios instance
 * - Implement all API calls
 * - Handle errors globally
 * - Add request/response interceptors
 * 
 * Architecture Pattern: Service Layer Pattern
 */

// Axios configuration
const api = axios.create({
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Request interceptor (add auth tokens, etc.)
api.interceptors.request.use(
    config => {
        // Add authentication token if available
        return config;
    },
    error => Promise.reject(error)
);

// Response interceptor (handle errors globally)
api.interceptors.response.use(
    response => response.data,
    error => {
        // Global error handling
        console.error('API Error:', error);
        throw error;
    }
);

// API Methods:
export const uploadFiles = (formData) => api.post('/api/upload', formData);
export const processResumes = (jdId) => api.post('/api/process', { jdId });
export const getShortlist = (jdId) => api.get(`/api/shortlist/${jdId}`);
export const exportResults = (jdId) => api.get(`/api/export/${jdId}`);
```

---

## 🔄 Data Flow

### 1. **Resume Upload & Processing Flow**

```
User Action                  Frontend                Backend                 AI Service              Database
    │                           │                       │                        │                       │
    ├─(1) Select Files─────────►│                       │                        │                       │
    │                           │                       │                        │                       │
    │                           ├─(2) Validate Files    │                        │                       │
    │                           │   - Check size        │                        │                       │
    │                           │   - Check format      │                        │                       │
    │                           │                       │                        │                       │
    │                           ├─(3) POST /api/upload──►│                        │                       │
    │                           │   FormData            │                        │                       │
    │                           │                       │                        │                       │
    │                           │                       ├─(4) Save Files          │                       │
    │                           │                       │   to Storage            │                       │
    │                           │                       │                        │                       │
    │                           │                       ├─(5) Extract Text        │                       │
    │                           │                       │   (PyPDF2/docx)        │                       │
    │                           │                       │                        │                       │
    │                           │                       ├─(6) Send to Claude─────►│                       │
    │                           │                       │   Structured prompt     │                       │
    │                           │                       │                        │                       │
    │                           │                       │◄─(7) JSON Response──────┤                       │
    │                           │                       │   {name, skills, etc}   │                       │
    │                           │                       │                        │                       │
    │                           │                       ├─(8) Validate Data       │                       │
    │                           │                       │   (Pydantic)            │                       │
    │                           │                       │                        │                       │
    │                           │                       ├─(9) INSERT INTO DB──────────────────────────────►│
    │                           │                       │                        │                       │
    │                           │◄─(10) Success Response┤                        │                       │
    │                           │   {jd_id, resume_ids} │                        │                       │
    │                           │                       │                        │                       │
    │◄─(11) Navigate to────────┤                       │                        │                       │
    │    Dashboard              │                       │                        │                       │
```

### 2. **Matching & Ranking Flow**

```
Dashboard Load              Frontend                Backend                 AI Service              Database
    │                           │                       │                        │                       │
    ├─(1) GET /dashboard/:jdId─►│                       │                        │                       │
    │                           │                       │                        │                       │
    │                           ├─(2) GET /api/shortlist/:jdId──────►│             │                       │
    │                           │                       │                        │                       │
    │                           │                       ├─(3) SELECT * FROM──────────────────────────────►│
    │                           │                       │   matches WHERE jd_id   │                       │
    │                           │                       │                        │                       │
    │                           │                       │◄─(4) Match Results──────────────────────────────┤
    │                           │                       │                        │                       │
    │                           │                       ├─(5) Calculate Stats     │                       │
    │                           │                       │   - Mean score          │                       │
    │                           │                       │   - Max/Min             │                       │
    │                           │                       │   - Count above threshold│                      │
    │                           │                       │                        │                       │
    │                           │                       ├─(6) Sort by Score       │                       │
    │                           │                       │   ORDER BY overall_score DESC                    │
    │                           │                       │                        │                       │
    │                           │◄─(7) Response─────────┤                        │                       │
    │                           │   {candidates, stats} │                        │                       │
    │                           │                       │                        │                       │
    │                           ├─(8) Render Dashboard  │                        │                       │
    │                           │   - Table              │                        │                       │
    │                           │   - Charts             │                        │                       │
    │                           │   - Statistics         │                        │                       │
    │◄─(9) Display Results─────┤                       │                        │                       │
```

---

## 🗄️ Database Schema

### PostgreSQL Schema Design

```sql
-- Job Descriptions Table
CREATE TABLE job_descriptions (
    jd_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255),
    description TEXT NOT NULL,
    requirements TEXT[],
    skills_required TEXT[],
    experience_required INTEGER,
    education_required VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resumes Table
CREATE TABLE resumes (
    resume_id SERIAL PRIMARY KEY,
    candidate_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    location VARCHAR(255),
    summary TEXT,
    skills TEXT[],
    experience JSONB,  -- Array of experience objects
    education JSONB,   -- Array of education objects
    projects JSONB,    -- Array of project objects
    certifications TEXT[],
    file_path VARCHAR(500),
    file_type VARCHAR(20),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Match Results Table
CREATE TABLE matches (
    match_id SERIAL PRIMARY KEY,
    jd_id INTEGER REFERENCES job_descriptions(jd_id) ON DELETE CASCADE,
    resume_id INTEGER REFERENCES resumes(resume_id) ON DELETE CASCADE,
    
    -- Scores (0-10 scale)
    overall_score DECIMAL(4, 2) NOT NULL,
    skills_score DECIMAL(4, 2) NOT NULL,
    experience_score DECIMAL(4, 2) NOT NULL,
    education_score DECIMAL(4, 2) NOT NULL,
    cultural_fit_score DECIMAL(4, 2) NOT NULL,
    achievements_score DECIMAL(4, 2) NOT NULL,
    
    -- AI-generated content
    justification TEXT,
    feedback TEXT,
    strengths TEXT[],
    weaknesses TEXT[],
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Composite unique constraint
    UNIQUE(jd_id, resume_id)
);

-- Indexes for performance
CREATE INDEX idx_matches_jd_id ON matches(jd_id);
CREATE INDEX idx_matches_resume_id ON matches(resume_id);
CREATE INDEX idx_matches_overall_score ON matches(overall_score DESC);
CREATE INDEX idx_resumes_email ON resumes(email);
CREATE INDEX idx_jd_created_at ON job_descriptions(created_at DESC);
```

### Entity Relationship Diagram

```
┌──────────────────────┐
│  job_descriptions    │
│──────────────────────│
│ PK jd_id            │
│    title            │
│    company          │
│    description      │
│    requirements[]   │
│    skills_required[]│
│    created_at       │
└──────────┬───────────┘
           │
           │ 1
           │
           │ *
┌──────────▼───────────┐         ┌──────────────────────┐
│      matches         │   *     │      resumes         │
│──────────────────────│◄────┬───│──────────────────────│
│ PK match_id         │      1   │ PK resume_id        │
│ FK jd_id            │          │    candidate_name   │
│ FK resume_id        │          │    email            │
│    overall_score    │          │    phone            │
│    skills_score     │          │    skills[]         │
│    experience_score │          │    experience       │
│    education_score  │          │    education        │
│    cultural_fit_score│         │    file_path        │
│    achievements_score│         │    uploaded_at      │
│    justification    │          └─────────────────────┘
│    feedback         │
│    created_at       │
└─────────────────────┘
```

---

## 🔒 Security Architecture

### 1. **API Security**

```python
# Input Validation
class UploadRequest(BaseModel):
    """Pydantic validation prevents injection attacks"""
    file: UploadFile
    
    @validator('file')
    def validate_file(cls, v):
        # File size check (max 5MB)
        if v.size > 5 * 1024 * 1024:
            raise ValueError("File too large")
        
        # File type check
        allowed_types = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
        if v.content_type not in allowed_types:
            raise ValueError("Invalid file type")
        
        return v

# SQL Injection Prevention
# Using SQLAlchemy ORM with parameterized queries
def get_matches_by_jd(jd_id: int):
    """Parameterized query prevents SQL injection"""
    query = "SELECT * FROM matches WHERE jd_id = %s"
    return db.execute(query, (jd_id,))

# XSS Prevention
# React automatically escapes user input
# Additional sanitization on backend
def sanitize_input(text: str) -> str:
    """Remove potentially harmful characters"""
    return html.escape(text)
```

### 2. **Environment Variables**

```bash
# .env file (NEVER commit to repository)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
ANTHROPIC_API_KEY=your_secret_key_here
SECRET_KEY=your_jwt_secret_key
ALLOWED_ORIGINS=http://localhost:3000

# Usage in code
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
API_KEY = os.getenv('ANTHROPIC_API_KEY')
```

### 3. **CORS Configuration**

```python
# Restrict origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://your-production-domain.com"  # Production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"]
)
```

---

## ⚡ Performance Optimization

### 1. **Database Optimization**

```sql
-- Indexing Strategy
CREATE INDEX idx_matches_jd_score ON matches(jd_id, overall_score DESC);
CREATE INDEX idx_resumes_skills ON resumes USING GIN(skills);

-- Query Optimization
EXPLAIN ANALYZE
SELECT m.*, r.candidate_name, r.email
FROM matches m
JOIN resumes r ON m.resume_id = r.resume_id
WHERE m.jd_id = 123
AND m.overall_score >= 7.0
ORDER BY m.overall_score DESC
LIMIT 50;
```

### 2. **Caching Strategy**

```python
# Future implementation: Redis caching
from functools import lru_cache

@lru_cache(maxsize=128)
def get_jd_requirements(jd_id: int):
    """Cache frequently accessed JD requirements"""
    return db.get_job_description(jd_id)

# API Response caching
@app.get("/api/stats/{jd_id}")
@cache(expire=300)  # Cache for 5 minutes
async def get_statistics(jd_id: int):
    """Cache statistical results"""
    return calculate_statistics(jd_id)
```

### 3. **Frontend Optimization**

```jsx
// React.memo for expensive components
const RadarChart = React.memo(({ data }) => {
    // Only re-render if data changes
    return <Chart data={data} />;
});

// Lazy loading
const Dashboard = lazy(() => import('./pages/Dashboard'));

// Code splitting
<Suspense fallback={<Loading />}>
    <Dashboard />
</Suspense>

// Pagination for large lists
const ShortlistTable = ({ data }) => {
    const [page, setPage] = useState(1);
    const pageSize = 10;
    const paginatedData = data.slice((page-1)*pageSize, page*pageSize);
    
    return <Table data={paginatedData} pagination={{current: page, pageSize}} />;
};
```

---

## 📊 Monitoring & Logging

### Logging Strategy

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Usage
@app.post("/api/process")
async def process_resumes(request: ProcessRequest):
    logger.info(f"Processing resumes for JD: {request.jd_id}")
    try:
        result = await matcher.process(request.jd_id)
        logger.info(f"Successfully processed {len(result)} candidates")
        return result
    except Exception as e:
        logger.error(f"Error processing resumes: {str(e)}", exc_info=True)
        raise
```

---

**Document Version**: 1.0  
**Last Updated**: October 17, 2025  
**Maintained By**: SOUMIK ROY
