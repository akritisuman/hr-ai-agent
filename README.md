# 🎯 HR Operations AI Agent

A production-ready, enterprise-grade AI system for intelligent CV ranking and candidate shortlisting. This system uses advanced AI to analyze job descriptions, compare CVs semantically, and rank candidates based on multiple factors.

## 🌟 Features

- **Multi-Format Support**: Process PDF, DOC, and DOCX CV files
- **Batch Processing**: Handle multiple CVs simultaneously (up to 50 per request)
- **Intelligent Ranking**: Multi-factor scoring system with AI-powered analysis
- **Semantic Matching**: Vector-based similarity search using Pinecone
- **Detailed Insights**: Comprehensive match scores, skill analysis, and explanations
- **Session Isolation**: Secure, isolated processing with automatic cleanup
- **Production-Ready**: Enterprise-grade architecture with error handling and logging

## 🏗️ Architecture

```
┌─────────────────┐
│  Streamlit UI   │  ← Chat-style interface
└────────┬────────┘
         │
┌────────▼────────┐
│   FastAPI API   │  ← RESTful backend
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────────┐
│LangChain│ │ Pinecone │
│ Agent  │ │  Vector  │
│        │ │   DB     │
└────────┘ └──────────┘
```

### Components

1. **Frontend (Streamlit)**: User interface for JD input, CV upload, and results visualization
2. **Backend (FastAPI)**: RESTful API handling requests, orchestration, and file management
3. **AI Layer (LangChain)**: GPT-4.1-powered agent for CV analysis and matching
4. **Vector Database (Pinecone)**: Stores embeddings for semantic similarity search
5. **Document Processing**: Handles PDF/DOC/DOCX parsing and text extraction

## 📋 Prerequisites

- Python 3.9+
- OpenAI API key (for GPT-4.1 and embeddings)
- Pinecone API key and account
- 10+ GB free disk space (for temporary file storage)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd hr_agent
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the root directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=hr-agent-cvs
PINECONE_ENVIRONMENT=us-east-1

# API Configuration (optional)
API_BASE_URL=http://localhost:8000
```

### 5. Initialize Pinecone Index

The application will automatically create the Pinecone index on first run if it doesn't exist. Ensure your Pinecone account has sufficient quota.

## 🎮 Usage

### Starting the Backend API

```bash
# Option 1: Using uvicorn directly
uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# Option 2: Using Python
python api.py
```

The API will be available at `http://localhost:8000`

### Starting the Frontend

```bash
streamlit run streamlit_app.py
```

The UI will be available at `http://localhost:8501`

### API Documentation

Once the backend is running, access interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📖 How It Works

### 1. Job Description Analysis

The system extracts:
- Required skills
- Tools and technologies
- Experience requirements
- Seniority level
- Key responsibilities

### 2. CV Processing

For each CV:
- Extract text content
- Split into semantic chunks
- Generate embeddings
- Store in vector database

### 3. Ranking Algorithm

Candidates are scored on:

| Factor | Weight | Description |
|--------|--------|-------------|
| **Skill Match** | 40% | Percentage of required skills found |
| **Experience** | 25% | Relevance and years of experience |
| **Tools/Tech** | 20% | Alignment with required technologies |
| **Seniority** | 10% | Match with role seniority level |
| **Semantic** | 5% | Overall semantic similarity |

Final score: **0-100** (weighted average)

### 4. Results

For each top candidate:
- Overall match score
- Detailed breakdown by factor
- Matched skills list
- Missing skills list
- AI-generated explanation
- Download link for CV

## 🔐 Security Features

- **Session Isolation**: Each request creates an isolated session
- **File Validation**: Type and size validation for uploads
- **Temporary Storage**: Files stored only during processing
- **Automatic Cleanup**: Sessions cleaned up after completion
- **No Data Leakage**: Strict session boundaries

## 📁 Project Structure

```
hr_agent/
├── streamlit_app.py      # Streamlit frontend
├── api.py                # FastAPI backend
├── agent.py              # LangChain AI agent
├── ingestion.py          # Document ingestion pipeline
├── ranking.py            # Ranking engine
├── utils/
│   ├── loaders.py        # Document loaders
│   ├── splitter.py       # Text splitting utilities
│   └── security.py       # Security and session management
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── .env                 # Environment variables (create this)
```

## 🧪 API Endpoints

### POST `/rank-cvs`

Rank CVs against a job description.

**Request:**
- `job_description` (form data): Job description text
- `files` (form data): List of CV files
- `top_n` (form data, optional): Number of top candidates (default: 3)

**Response:**
```json
{
  "session_id": "uuid",
  "top_candidates": [
    {
      "candidate_name": "John Doe",
      "match_score": 85.5,
      "matched_skills": ["Python", "FastAPI", "AWS"],
      "missing_skills": ["Docker"],
      "explanation": "Strong match with excellent skills...",
      "detailed_scores": {
        "skill_match": 90.0,
        "experience": 85.0,
        "tool_tech": 80.0,
        "seniority": 75.0,
        "semantic": 0.85
      }
    }
  ],
  "total_candidates": 10,
  "processing_time_seconds": 45.2
}
```

### GET `/download-cv/{session_id}/{filename}`

Download a CV file from a session.

### DELETE `/session/{session_id}`

Clean up a session and all associated data.

### GET `/health`

Health check endpoint.

## 🛠️ Configuration

### Model Selection

Edit `agent.py` to change the AI model:

```python
self.llm = ChatOpenAI(
    model_name="gpt-4.1",  # Change this
    temperature=0
)
```

### Ranking Weights

Adjust weights in `ranking.py`:

```python
WEIGHTS = {
    "skill_match": 0.40,  # Adjust these values
    "experience": 0.25,
    "tool_tech": 0.20,
    "seniority": 0.10,
    "semantic": 0.05
}
```

### File Limits

Modify limits in `utils/security.py`:

```python
MAX_FILE_SIZE_MB = 10  # Maximum file size
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx'}
```

## 🐛 Troubleshooting

### API Connection Errors

- Ensure the FastAPI backend is running
- Check `API_BASE_URL` in `.env` or Streamlit config
- Verify firewall settings

### Pinecone Errors

- Verify API key is correct
- Check Pinecone account quota
- Ensure index name is unique

**Dimension Mismatch Error**: If you see "Vector dimension does not match the index dimension":
  - The code now automatically detects your index dimension and adjusts embeddings
  - For best results, use an index with dimension 1536 (standard for OpenAI embeddings)
  - If your index has 512 dimensions, the system will truncate embeddings, but consider recreating the index with 1536 dimensions for better accuracy
  - To recreate: Delete the old index and let the system create a new one with the correct dimension

### Document Loading Errors

- Verify file formats are supported
- Check file size limits
- Ensure files are not corrupted

### OpenAI Errors

- Verify API key is valid
- Check account quota and billing
- Ensure model name is correct

## 📊 Performance

- **Processing Time**: ~30-60 seconds for 10 CVs
- **Concurrent Requests**: Supports multiple sessions simultaneously
- **Scalability**: Vector database enables fast similarity search
- **Memory Usage**: ~2-4 GB for typical workloads

## 🔄 Maintenance

### Cleanup Old Sessions

Sessions are automatically cleaned up after 24 hours. To manually clean:

```python
from utils.security import SessionManager
manager = SessionManager()
manager.cleanup_old_sessions(max_age_hours=24)
```

### Monitor Vector Database

Check Pinecone dashboard for:
- Index size and usage
- Query performance
- Storage costs

## 📝 License

This project is proprietary and confidential.

## 👥 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check logs for detailed error messages

## 🚀 Future Enhancements

- [ ] Support for additional file formats (TXT, RTF)
- [ ] Multi-language support
- [ ] Custom scoring weights per request
- [ ] Batch processing API
- [ ] Integration with ATS systems
- [ ] Advanced analytics dashboard
- [ ] Candidate comparison view
- [ ] Export results to Excel/PDF

---

**Built with ❤️ for efficient HR operations**

