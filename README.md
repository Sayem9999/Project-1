# ProEdit (Project-1)

**Professional AI Video Editor with "Hollywood Pipeline" Architecture.**

ProEdit is an advanced automated video editing platform that uses a multi-agent AI system to turn raw footage into professional-grade content. It features a sophisticated "Hollywood Pipeline" where specialized AI agents (Director, Cutter, Audio, Colorist) collaborate to produce high-quality videos tailored for specific platforms (TikTok, YouTube, Instagram).

## 🚀 Key Features

*   **Hollywood Pipeline**: A LangGraph-based orchestration of specialized AI agents mimicking a real production studio.
    *   **Director Agent**: Analyzes footage and creates a creative vision.
    *   **Cutter Agent**: Handles precise trimming and pacing.
    *   **Audio Agent**: Mixes audio, adds music, and enhances speech.
    *   **Colorist Agent**: Applies color grading and aesthetic filters.
    *   **QC Agent**: Performs multi-dimensional quality control (Technical, Aesthetic, Content Safety).
*   **Specialist Capabilities**:
    *   **Hook Optimization**: AI-driven optimization of the first 3 seconds for viral retention.
    *   **Platform Adaptation**: Automatic resizing and pacing for different platforms (9:16, 16:9, etc.).
    *   **Brand Safety**: Automated content moderation and safety checks.
*   **Real-time Processing**: WebSocket-based progress tracking with detailed stage-by-stage visualization.
*   **Media Intelligence**: Deep technical analysis of source media (Resolution, Loudness, Scene Detection).
*   **Admin Panel**: Comprehensive dashboard for user management and job monitoring.

## 🛠 Tech Stack

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Styling**: Tailwind CSS + Custom "Hollywood Studio" Theme
- **UI Components**: Lucide React, Framer Motion
- **State/Data**: React Hooks, WebSockets

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Orchestration**: LangGraph (Agentic Workflow)
- **Task Queue**: Celery + Redis
- **Database**: PostgreSQL (Production) / SQLite (Local Dev)
- **AI Models**: Google Gemini, OpenAI GPT-4, Groq
- **Video Processing**: FFmpeg, PySceneDetect

### Infrastructure
- **Storage**: Cloudflare R2 / Local Filesystem
- **Deployment**: Render (Backend/DB), Vercel (Frontend)

## ⚡ Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- Node.js 20+
- Redis (Local or Remote)
- PostgreSQL (Optional, defaults to SQLite for local)

### Backend Setup

1.  **Navigate to backend:**
    ```bash
    cd backend
    ```

2.  **Create virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment:**
    Copy `.env.example` to `.env` and fill in your keys (Gemini, database, etc.).
    ```bash
    cp .env.example .env
    ```

5.  **Run Migrations:**
    ```bash
    python -m alembic upgrade head
    ```

6.  **Start Server:**
    ```bash
    python -m uvicorn app.main:app --reload
    ```
    API will be available at `http://localhost:8000`.

7.  **Start Celery Worker (for video processing):**
    ```bash
    python -m celery -A app.celery_app worker --loglevel=info
    ```

## Production Memory Mode (512MB Render)

Use API-only mode on Render web service, and run the worker separately.

1. Web service (`proedit-api`) must run with:
   - `RUN_EMBEDDED_CELERY=false`
2. Keep `REDIS_URL` configured on Render so jobs are queued.
3. Run Celery worker on your PC (Windows PowerShell):
   ```powershell
   cd backend
   .\.venv\Scripts\activate

   # Set production envs (use your real values from Render)
   $env:ENVIRONMENT = "production"
   $env:REDIS_URL = "rediss://<render-redis-url>"
   $env:DATABASE_URL = "postgresql+asyncpg://<render-postgres-url>"
   $env:SECRET_KEY = "<same-secret-key-used-by-api>"
   $env:GEMINI_API_KEY = "<optional>"
   $env:GROQ_API_KEY = "<optional>"
   $env:OPENAI_API_KEY = "<optional>"
   $env:R2_ACCOUNT_ID = "<r2-account-id>"
   $env:R2_ACCESS_KEY_ID = "<r2-access-key-id>"
   $env:R2_SECRET_ACCESS_KEY = "<r2-secret>"
   $env:R2_BUCKET_NAME = "proedit-uploads"
   $env:MODAL_TOKEN_ID = "<modal-token-id>"
   $env:MODAL_TOKEN_SECRET = "<modal-token-secret>"

   celery -A app.celery_app worker --pool=solo --concurrency=1 --without-gossip --without-mingle --without-heartbeat -Q video,celery --loglevel=info
   ```
   Or use:
   ```powershell
   .\run_worker.ps1
   ```
4. Keep this worker terminal running continuously while processing jobs.

### Frontend Setup

1.  **Navigate to frontend:**
    ```bash
    cd frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Configure Environment:**
    Copy `frontend/.env.local.example` to `frontend/.env.local` and update `NEXT_PUBLIC_API_BASE` if needed.

4.  **Start Development Server:**
    ```bash
    npm run dev
    ```
    UI will be available at `http://localhost:3000`.

## 📚 Documentation

- **API Documentation**: `http://localhost:8000/docs`
- **Architecture**: See `docs/architecture` for detailed system design.
