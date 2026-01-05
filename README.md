# AI-Support-Agent

## Progress updates 
<details><summary> Day 1 - 03/12/25 </summary>
  
## Day 1 - 03/12/25
* Created main application entry point in ``app/main.py``.
* Expose a simple endpoint to confirm server availability, GET /health returns a basic JSON response with meaningful info: API version and timestamp:[^1][^2]

  ```python
  import fastapi
  from fastapi import FastAPI
  
  import datetime
  
  app = FastAPI()
  
  @app.get("/")
  async def root():
      return {"message": "Hello World"}
  
  @app.get("/health")
  async def health():
      return {"FastAPI version": fastapi.__version__,
              "Timestamp": datetime.datetime.now()
      }
  ```

[^1]: Harley Holcombe, 6 Jan 2009, "How do I get the current time in Python?", _Stack Overflow_, https://stackoverflow.com/a/415519
[^2]: Extra Data Types - FastAPI, https://fastapi.tiangolo.com/tutorial/extra-data-types/?h=uuid

* Using https://fastapi.tiangolo.com/tutorial/first-steps/ as a guide.
* Using ``fastapi dev main.py`` to load the web API. Accessible via ``http://127.0.0.1:8000/``, ``http://127.0.0.1:8000/health/``, and  ``http://127.0.0.1:8000/docs#/`` (which uses Swagger UI).
</details>

<details><summary> Day 2 - 04/12/25 </summary>
  
## Day 2 - 04/12/25
* Configured CORSMiddleware to support future frontend interactions and manage app settings cleanly.[^3]

[^3]: CORS (Cross-Origin Resource Sharing) - FastAPI, https://fastapi.tiangolo.com/tutorial/cors/?h=cors

* Moved the health function defintion to a separate file, inside ``app/routers/health.py``. ``main.py`` can access it by doing ``from app.routers.health import router as health_router`` and ``app.include_router(health_router)``.[^4]

  ``app/main.py``:

  ```python
  import fastapi
  from fastapi import FastAPI
  from fastapi.middleware.cors import CORSMiddleware
  
  from app.routers.health import router as health_router
  
  app = FastAPI()
  
  origins = [
      "https://localhost:8000",
  ]
  
  app.add_middleware(
      CORSMiddleware,
      allow_origins=origins,
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  
  app.include_router(health_router)
  
  @app.get("/")
  async def root():
      return {"message": "Hello World"}

  ```

  ``app/routers/health.py``:

  ```python
  from fastapi import APIRouter
  import fastapi
  import datetime
  
  router = APIRouter()
  
  @router.get("/health")
  async def health():
      return {
          "FastAPI version": fastapi.__version__,
          "Timestamp": datetime.datetime.now()
      }
  ```
  
[^4]: Bigger Applications - Multiple Files - FastAPI, https://fastapi.tiangolo.com/tutorial/bigger-applications/
  
* Added a ``.gitignore``:[^5]

  ```txt
  app/__pycache__/
  ```
  
* Added a ``requirements.txt``:[^5]

  ```txt
  fastapi
  uvicorn[standard]
  python-dotenv
  ```

  running ``pip install -r requirements.txt`` installs all dependencies easily.[^5]

[^5]: Virtual Environments - FastAPI, https://fastapi.tiangolo.com/virtual-environments/
  
* Switched from using ``fastapi dev main.py``[^6] (quick sandbox testing, accepts only relative importing, e.g. ``from .routers.health import router as health_router``) to load the web API to ``uvicorn app.main:app --reload --host 127.0.0.1 --port 8000``[^7][^8][^9] (recommended production-standard approach, accepts absolute importing, e.g. ``from app.routers.health import router as health_router``). The latter command didn't work initially (website hanged) but after running these commands in PowerShell (administrator mode):

  ```console
  netsh winsock reset
  netsh int ip reset
  ```

   and restarting my PC it worked.

[^6]: First Steps - FastAPI, https://fastapi.tiangolo.com/tutorial/first-steps/
[^7]: Deployment - Uvicorn, https://uvicorn.dev/deployment/
[^8]: Run a Server Manually - FastAPI, https://fastapi.tiangolo.com/deployment/manually/
[^9]: Debugging - FastAPI, https://fastapi.tiangolo.com/tutorial/debugging/
  
  
* Added a ``.env`` file:[^10]

  ```env
  # Deployment environment
  ENVIRONMENT=development
  
  # CORS allowed origins (comma-separated)
  CORS_ALLOWED_ORIGINS=["http://localhost:5173", "http://127.0.0.1:5173"]
  ```

  to hold secrets & environment-dependent values (not pushed to remote, added to ``.gitignore``).

[^10]: Settings and Environment Variables - FastAPI, https://fastapi.tiangolo.com/advanced/settings

* Added ``config.py``:[^10]

  ```python
  from pydantic_settings import BaseSettings, SettingsConfigDict
  from functools import lru_cache
  from typing import List
  
  
  class Settings(BaseSettings):
      ENVIRONMENT: str
      CORS_ALLOWED_ORIGINS: List[str]
  
      # Later you can add:
      # OPENAI_API_KEY: str
      # DB_URL: str
  
      model_config = SettingsConfigDict(
          env_file = ".env",
          env_file_encoding = "utf-8"
      )
  
  
  @lru_cache()
  def get_settings():
      return Settings()
  
  
  settings = get_settings()
  ```

  ``.env`` stores sensitive info (e.g., secrets, API keys, origins), ``config.py`` loads them into Python using a ``Settings`` class (using Pydantic v2).[^10][^11] Production-quality FastAPI apps always use .env + a config module. And we used ``pydantic_settings`` over ``python-dotenv`` to load the environment variables as it is cleaner, safer, faster, validated, and the recommended modern approach for FastAPI applications (type validation, required values checked, integration with FastAPI/Pydantic, default values built-in, and automatic override with OS env vars).

[^11]: Read settings from .env - Settings and Environment Variables - FastAPI, https://fastapi.tiangolo.com/advanced/settings/?h=#read-settings-from-env
  
* Added logging middleware,[^12] that logs method, path, and timing in the console:

  ``app/middleware/logging.py``:
  
  ```py
  import time
  from fastapi import Request
  from starlette.middleware.base import BaseHTTPMiddleware
  
  class LoggingMiddleware(BaseHTTPMiddleware):
      async def dispatch(self, request: Request, call_next):
          start_time = time.time()
  
          response = await call_next(request)
  
          duration = (time.time() - start_time) * 1000  # ms
  
          method = request.method
          path = request.url.path
  
          print(f"[LOG] {method} {path} completed in {duration:.2f} ms")
  
          return response
  ```

    and added in ``main.py``:

  ```python
  from app.middleware.logging import LoggingMiddleware

  # -------
  # LOGGING
  # -------
  app.add_middleware(LoggingMiddleware)
  ```

[^12]: Middleware - FastAPI, https://fastapi.tiangolo.com/tutorial/middleware/
  
* The current folder structure:[^13]

  ```
  AI-Support-Agent/
  ├── app/
  │   ├── main.py
  │   ├── config.py
  │   ├── middleware/
  │   │   └── logging.py
  │   └── routers/
  │       └── health.py
  ├── .env
  ├── .gitignore
  ├── requirements.txt
  └── README.md
  ```

  [^13]: How to Structure Your FastAPI Projects, Amir Lavasani, 
May 14, 2024, Medium, https://medium.com/@amirm.lavasani/how-to-structure-your-fastapi-projects-0219a6600a8f

</details>

<details><summary> Day 3 - 05/12/25 </summary>

## Day 3 - 05/12/25
* <details><summary>Enable users to upload a PDF file to the backend</summary>
  
  * <details><summary> New folder structure </summary>

    ```
    AI-Support-Agent/
      ├── app/
      │   ├── main.py
      │   ├── config.py
      │   ├── middleware/
      │   │   └── logging.py
      │   ├── services/
      │   │   └── file_storage.py <-- NEW (optional but clean)
      │   ├── storage/
      │   │   └── pdfs/           <-- auto-created
      │   └── routers/
      │       ├── health.py
      │       └── pdf_upload.py   <-- NEW
      ├── .env
      ├── .gitignore
      ├── requirements.txt
      └── README.md
    ```
    </details>
    
  * <details><summary>Storage helper</summary>

    ``app/services/file_storage.py``:

    ```python
    import os
    import uuid
    from fastapi import HTTPException, UploadFile
    
    # Base storage folder
    BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "pdfs")
    
    # Ensure directory exists
    os.makedirs(BASE_DIR, exist_ok=True)
    
    
    def save_pdf(file: UploadFile) -> dict:
        # Validate MIME type
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only PDF files are allowed."
            )
    
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}.pdf"
        filepath = os.path.join(BASE_DIR, filename)
    
        # Save file data
        with open(filepath, "wb") as out_file:
            out_file.write(file.file.read())
    
        # Return metadata
        return {
            "file_id": file_id,
            "filename": filename,
            "size_bytes": os.path.getsize(filepath),
            "content_type": file.content_type,
            "storage_path": filepath,
        }
    ```
  
    using UUID to create unique file IDs.[^2]

    </details>

  * <details><summary>Endpoint router for PDF upload</summary>
 
    ``app/routers/pdf_upload.py``:

    ```python
      from fastapi import APIRouter, UploadFile, File, HTTPException
      from app.services.file_storage import save_pdf
      
      router = APIRouter(prefix="/pdf", tags=["PDF Upload"])
      
      
      @router.post("/upload")
      async def upload_pdf(file: UploadFile = File(...)):
          if file is None:
              raise HTTPException(status_code=400, detail="No file uploaded.")
      
          metadata = save_pdf(file)
          return {
              "message": "PDF uploaded successfully",
              "metadata": metadata
          }
      ```
    </details>

  * <details><summary>Update main.py to include router</summary>
 
    ``app/main.py``:

    ```diff
      from fastapi import FastAPI
      from fastapi.middleware.cors import CORSMiddleware
      
      
      from app.config import settings
      from app.middleware.logging import LoggingMiddleware
      from app.routers.health import router as health_router
    + from app.routers.pdf_upload import router as pdf_router
      
      
      app = FastAPI(
          title="AI Support Agent",
          version="1.0.0"
      )
      
      
      # -----------
      # CORS CONFIG
      # -----------
      app.add_middleware(
          CORSMiddleware,
          allow_origins=settings.CORS_ALLOWED_ORIGINS,
          allow_credentials=True,
          allow_methods=["*"],
          allow_headers=["*"],
      )
      
      
      # -------
      # LOGGING
      # -------
      app.add_middleware(LoggingMiddleware)
      
      
      # -------
      # ROUTERS
      # -------
      app.include_router(health_router)
    + app.include_router(pdf_router)
      
      
      @app.get("/")
      async def root():
          return {"message": "Hello World"}
    ```
    </details>

  </details>

* <details><summary>Centralised error responses and validation rules</summary>

  * <details><summary> New folder structure </summary>

    ```
    AI-Support-Agent/
      ├── app/
      │   ├── main.py
      │   ├── config.py
      │   ├── middleware/
      │   │   └── logging.py
      │   ├── services/
      │   │   └── file_storage.py
      │   ├── storage/
      │   │   └── pdfs/
      │   ├── core/
      │   │   └── errors.py          <-- NEW (standardised error responses)
      │   └── routers/
      │       ├── health.py
      │       └── pdf_upload.py
      ├── .env
      ├── .gitignore
      ├── requirements.txt
      └── README.md
    ```
    
    </details>

  * <details><summary>Centralised error responses</summary>
 
    ``app/core/errors.py``:
 
    ```python
    from fastapi import HTTPException, status
    
    
    def bad_request(message: str):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": message}
        )
    
    
    def unsupported_file(message: str):
        return HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail={"error": message}
        )
    ```
 
    This keeps all error messages consistent across the API. Now every endpoint uses the same structure:

    ```
    { "error": "Your message here" }
    ```

    </details>

  * <details><summary>Implement Strong Validation Rules</summary>

    ``app/services/file_storage.py``:
 
    ```diff
      import os
      import uuid
    - from fastapi import HTTPException, UploadFile
    + from fastapi import UploadFile
    + from app.core.errors import unsupported_file, bad_request
      
      # Base storage folder
      BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "pdfs")
      
      # Ensure directory exists
      os.makedirs(BASE_DIR, exist_ok=True)
      
    + def validate_pdf(file: UploadFile):
    +     # Check presence
    +     if file is None:
    +         raise bad_request("No file was uploaded.")
      
    +     # Validate extension
    +     filename = file.filename.lower()
    +     if not filename.endswith(".pdf"):
    +         raise unsupported_file("File extension must be .pdf")
      
    +     # Validate MIME type
    +     if file.content_type != "application/pdf":
    +         raise unsupported_file("Invalid file type. Only PDF files are allowed.")
      
    +     return True

  
      def save_pdf(file: UploadFile) -> dict:
          # Validate MIME type
    -     if file.content_type != "application/pdf":
    -         raise HTTPException(
    -             status_code=400,
    -             detail="Invalid file type. Only PDF files are allowed."
    -         )
    +     validate_pdf(file)
    
          # Generate unique filename
          file_id = str(uuid.uuid4())
          filename = f"{file_id}.pdf"
          filepath = os.path.join(BASE_DIR, filename)
      
          # Save file data
          with open(filepath, "wb") as out_file:
              out_file.write(file.file.read())
      
          # Return metadata
          return {
              "file_id": file_id,
              "filename": filename,
              "size_bytes": os.path.getsize(filepath),
              "content_type": file.content_type,
              "storage_path": filepath,
          }
    ```

    Validation examples:

    * Valid PDF upload:
   
      ```json
      {
        "message": "PDF uploaded successfully",
        "metadata": {
          "file_id": "f09eca22-f86c-452a-a1da-76a5eb0d76a1",
          "filename": "f09eca22-f86c-452a-a1da-76a5eb0d76a1.pdf",
          "size_bytes": 55657,
          "content_type": "application/pdf",
          "storage_path": "E:\\AI-Support-Agent\\app\\storage\\pdfs\\f09eca22-f86c-452a-a1da-76a5eb0d76a1.pdf"
        }
      }
      ```

    * Upload JPG called ``image.jpg``:
   
      ```json
      {
        "detail": {
          "error": "File extension must be .pdf"
        }
      }
      ```

    * No file uploaded:

      ```json
      {
        "detail": {
          "error": "No file was uploaded."
        }
      }
      ```

    </details>


</details>

<details><summary> Day 4 - 11/12/25 </summary>

## Day 4 - 11/12/25

  * <details><summary> New folder structure </summary>

    ```
    AI-Support-Agent/
      ├── app/
      │   ├── main.py
      │   ├── config.py
      │   ├── middleware/
      │   │   └── logging.py
      │   ├── services/
      │   │   ├── file_storage.py
      │   │   └── pdf_service.py     <-- NEW
      │   ├── storage/
      │   │   └── pdfs/
      │   ├── core/
      │   │   └── errors.py
      │   └── routers/
      │       ├── health.py
      │       ├── pdf_upload.py
      │       └── pdf_extract.py     <-- NEW
      ├── .env
      ├── .gitignore
      ├── requirements.txt
      └── README.md
    ```
    </details>

* <details><summary> Update .gitignore </summary>

  Add this to ``.gitignore`` to prevent ``/__pycache__`` being pushed to remote:[^14]

  [^14]: Python Programming Course - Imperial College London COMP70053 Lesson 8 Chapter 5.3, https://python.pages.doc.ic.ac.uk/2022/lessons/core08/05-robot/03-ignore.html
  
  ```
  **/__pycache__/
  **/*.pyc
  ```

  </details>

* <details><summary> PDF Text Extraction </summary>

  * Added ``app/services/pdf_service.py``:
 
    ```py
    import pdfplumber
    from pathlib import Path
    
    
    # Raised when the PDF cannot be processed.
    class PDFExtractionError(Exception):
        pass
    
    
    # Extracts plain text from a PDF file using pdfplumber.
    def extract_text_from_pdf(file_path: Path) -> str:
        try:
            text_content = []
    
            with pdfplumber.open(file_path) as pdf:
                if len(pdf.pages) == 0:
                    raise PDFExtractionError("PDF contains no pages.")
    
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    text_content.append(page_text)
    
            full_text = "\n".join(text_content).strip()
    
            if not full_text:
                raise PDFExtractionError("PDF text extraction returned empty content.")
    
            return full_text
    
        except Exception as e:
            raise PDFExtractionError(f"Failed to extract PDF text: {str(e)}")
    
    ```

    which extracts text from the PDF using ``pdfplumber`` (added to ``requirements.txt`` and installed via ``pip install pdfplumber``).

  * Removed error handling from ``app/routers/pdf_upload.py`` (as ``save_pdf()`` from ``file_storage.py`` already handles that):
 
    ```diff
      from fastapi import APIRouter, UploadFile, File, HTTPException
      from app.services.file_storage import save_pdf
      
      router = APIRouter(prefix="/pdf", tags=["PDF Upload"])
      
      
      @router.post("/upload")
      async def upload_pdf(file: UploadFile = File(...)):
    -     if file is None:
    -         raise HTTPException(status_code=400, detail="No file uploaded.")
      
          metadata = save_pdf(file)
          return {
              "message": "PDF uploaded successfully",
              "metadata": metadata
          }
    ```

  </details>

* <details><summary> Temp Text Return </summary>

  * Added ``app/routers/pdf_extract.py``:
 
    ```py
    from fastapi import APIRouter, HTTPException
    from app.services.file_storage import get_pdf_path
    from app.services.pdf_service import extract_text_from_pdf, PDFExtractionError
    from pathlib import Path
    
    router = APIRouter(prefix="/pdf", tags=["PDF Extraction"])
    
    
    @router.post("/{file_id}/extract")
    def extract_pdf_text(file_id: str):
        try:
            pdf_path = Path(get_pdf_path(file_id))
            text = extract_text_from_pdf(pdf_path)
    
            return {
                "file_id": file_id,
                "text_length": len(text),
                "text_preview": text[:1000],  # prevent massive response
            }
    
        except PDFExtractionError as e:
            raise HTTPException(status_code=422, detail=str(e))
    ```

  * Updated ``app/main.py``:
 
    ```diff
      from fastapi import FastAPI
      from fastapi.middleware.cors import CORSMiddleware
      
      
      from app.config import settings
      from app.middleware.logging import LoggingMiddleware
      from app.routers.health import router as health_router
    - from app.routers.pdf_upload import router as pdf_router
    + from app.routers.pdf_upload import router as pdf_upload_router
    + from app.routers.pdf_extract import router as pdf_extract_router
      
      
      app = FastAPI(
          title="AI Support Agent",
          version="1.0.0"
      )
      
      
      # -----------
      # CORS CONFIG
      # -----------
      app.add_middleware(
          CORSMiddleware,
          allow_origins=settings.CORS_ALLOWED_ORIGINS,
          allow_credentials=True,
          allow_methods=["*"],
          allow_headers=["*"],
      )
      
      
      # -------
      # LOGGING
      # -------
      app.add_middleware(LoggingMiddleware)
      
      
      # -------
      # ROUTERS
      # -------
      app.include_router(health_router)
    - app.include_router(pdf_router)
    + app.include_router(pdf_upload_router)
    + app.include_router(pdf_extract_router)
      
      
      @app.get("/")
      async def root():
          return {"message": "Hello World"}
    ```

  * Result:

    <img width="956" height="825" alt="image" src="https://github.com/user-attachments/assets/d77553e2-bd2f-4f42-8f14-05434917285b" />
     
     * When uploading a valid PDF:

       ```json
        {
          "message": "PDF uploaded successfully",
          "metadata": {
            "file_id": "d64c5531-892a-42b1-9d62-af9661448200",
            "filename": "Computer Simulation of Saturn's Ring Structure.pdf",
            "stored_filename": "d64c5531-892a-42b1-9d62-af9661448200.pdf",
            "path": "E:\\...\\AI-Support-Agent\\app\\storage\\pdfs\\d64c5531-892a-42b1-9d62-af9661448200.pdf",
            "size_bytes": 3026909,
            "content_type": "application/pdf"
          }
        }
       ```

    * When entering a non-valid format:
   
      ```json
      {
        "detail": {
          "error": "File extension must be .pdf"
        }
      }
      ```

    * Extracting text from valid file ID:
   
      ```json
      {
        "file_id": "d64c5531-892a-42b1-9d62-af9661448200",
        "text_length": 42442,
        "text_preview": "Computer Simulation of Saturn’s Ring\nStructure\nNew Mexico\nSupercomputing Challenge\nFinal Report\nApril 3, 2013\nTeam 58\nLos Alamos High School\nTeam Members\nCole Kendrick\nTeachers\nBrian Kendrick\nProject Mentor\nBrian Kendrick\nSummary\nThe main goal of this project is to develop a computer program to model the creation of\nstructure in Saturn’s ring system. The computer program will be used to answer these\nquestions: (1) How are gaps in Saturn’s Rings formed; (2) how accurately can I model\ngap formation with a 3D N-Body simulation; and (3) will my simulation compare to\nobserved features, theoretical data, and professional simulations. Newton’s laws of\nmotion and gravity as well as the velocity Verlet method are being used to orbit the\nparticles around Saturn. Gaps in Saturn’s ring system are caused by three main methods:\n(1) Gravitational resonances; (2) moons that orbit inside the ring; and (3) an asteroid or\ncomet impact. Gravitational resonances are a major part of formation in the ring sy"
      }
      ```

    * Attempting to extract text from non-valid file ID:
   
      ```json
      {
        "detail": {
          "error": "PDF not found."
        }
      }
      ```

  </details>

</details>

<details><summary> Day 5 - 13/12/25 </summary>

## Day 5 - 13/12/25

* <details><summary> MongoDB Integration </summary>

  * Chose to use MongoDB Atlas free tier instead of local MongoDB as it means:
    * No local install headaches
    * No service to keep running
    * Works the same locally and in production
    * Teaches the “real” way MongoDB is used
    * Free forever (with limits)

    I can always switch to local MongoDB later in ~5 minutes.

  * I already have a MongoDB account, so just had to setup a new project with a free-tier cluster, create a database user with read/write access, allowed network access from anywhere (can change later).
  * When connecting to the cluster, I simply select the latest Python driver. This gives me the command to install:
 
    ```console
    python -m pip install "pymongo[srv]"
    ```

    and a connection string:

    ```py
    mongodb+srv://appuser:<db_password>@cluster0.ycojzhc.mongodb.net/?appName=Cluster0
    ```

    Replacing <db_password> with the password for the appuser database user. And ensuring any option params are URL encoded.

  * Adding to ``.env`` the connection string (replacing ``YOUR_PASSWORD`` with the password of the database user I just created):
 
    ```env
    MONGODB_URI=mongodb+srv://appuser:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/?appName=CLUSTER_NAME
    MONGODB_DB=ai_support_agent
    ```

  * Adding to ``requirements.txt``:
 
    ```txt
    pymongo>=4.6
    ```

  * Created the MongoDB connection file, ``app/db/mongodb.py``:
 
    ```py
    from pymongo import MongoClient
    from app.config import settings
    
    client = MongoClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB]
    
    documents_collection = db["documents"]
    ```

    Now I have: One client, one DB, one collection.

  * Document repository (persistance layer), ``app/services/document_repository.py``:
 
    ```py
    from datetime import datetime
    from app.db.mongodb import documents_collection
    
    
    def create_document(metadata: dict) -> dict:
        document = {
            "file_id": metadata["file_id"],
            "original_filename": metadata["filename"],
            "stored_filename": metadata["stored_filename"],
            "size_bytes": metadata["size_bytes"],
            "content_type": metadata["content_type"],
            "status": "UPLOADED",
            "created_at": datetime.utcnow(),
        }
    
        documents_collection.insert_one(document)
        return document
    ```

    Now I have two layers of persistance: a local file storage (``app/storage/pdfs`` handled by ``app/services/file_storage.py``), and MongoDB (document repository).

  * Updating ``app/routers/pdf_upload.py`` to wire MongoDB into upload flow:
 
    ```diff
      from fastapi import APIRouter, UploadFile, File, HTTPException
      from app.services.file_storage import save_pdf
    + from app.services.document_repository import create_document
      
      
      router = APIRouter(prefix="/pdf", tags=["PDF Upload"])
      
      
      @router.post("/upload")
      async def upload_pdf(file: UploadFile = File(...)):
          metadata = save_pdf(file)
    +     document = create_document(metadata)
      
          return {
              "message": "PDF uploaded successfully",
              "metadata": metadata,
    +         "file_id": document["file_id"],
    +         "status": document["status"]
          }
      ```

  * Restarting the server (``uvicorn app.main:app --reload --host 127.0.0.1 --port 8000``), uploading a PDF via Swagger (``http://127.0.0.1:8000/docs``), and going to Atlas → Browse Collections in the MongoDB project cluster, I can see the new document added:
 
    ```json
    {
      "_id":{"$oid":"693f80edcadadd721e4ecd75"},
      "file_id":"27ff3caa-2fbc-4418-b16f-bbb0af29c4a9",
      "original_filename":"Print cover sheet - Get a document legalised - GOV.UK-2.pdf",
      "stored_filename":"27ff3caa-2fbc-4418-b16f-bbb0af29c4a9.pdf",
      "size_bytes":90281,
      "content_type":"application/pdf",
      "status":"UPLOADED",
      "created_at":2025-12-15T03:30:53.956+00:00
    }
    ```


  </details>

* <details><summary> Store Extracted Text </summary>

  * Currently the system workflow is:
 
    ```
    1. Save file to disk
    2. Save metadata to MongoDB (status = UPLOADED)
    ```

  * Want to extend it to:
 
    ```
    1. Save file to disk
    2. Save metadata (UPLOADED)
    
    3. Read PDF from disk
    4. Extract text
    5. Store extracted text in MongoDB
    6. Update status = EXTRACTED
    ```

  * Will add two new fields to the existing document format in MongoDB:
 
    ```
    {
      "extracted_text": "full plain text...",  <-- NEW
      "status": "EXTRACTED",                   <-- new status
      "extracted_at": ISODate(...)             <-- NEW
    }
    ```

  * Add method to store extracted text and function to get file ID (for later), update ``app/services/document_repository.py``:
 
    ```diff
      from datetime import datetime
      from app.db.mongodb import documents_collection
      
      
      def create_document(metadata: dict) -> dict:
          document = {
              "file_id": metadata["file_id"],
              "original_filename": metadata["filename"],
              "stored_filename": metadata["stored_filename"],
              "size_bytes": metadata["size_bytes"],
              "content_type": metadata["content_type"],
              "status": "UPLOADED",
              "created_at": datetime.utcnow(),
          }
      
          documents_collection.insert_one(document)
          return document
      
      
    + def get_document_by_file_id(file_id: str) -> dict | None:
    +     return documents_collection.find_one({"file_id": file_id})
      
      
    + def store_extracted_text(file_id: str, text: str):
    +     result = documents_collection.update_one(
    +         {"file_id": file_id},
    +         {
    +             "$set": {
    +                 "extracted_text": text,
    +                 "status": "EXTRACTED",
    +                 "extracted_at": datetime.utcnow(),
    +             }
    +         }
    +     )
    + 
    +     if result.matched_count == 0:
    +         raise ValueError("Document not found")
    ```

  * Updated ``app/routers/pdf_extract.py``:
 
    ```diff
      from fastapi import APIRouter, HTTPException
      from pathlib import Path
      
      from app.services.file_storage import get_pdf_path
      from app.services.pdf_service import extract_text_from_pdf, PDFExtractionError
    + from app.services.document_repository import (
    +     store_extracted_text,
    +     get_document_by_file_id,
    + )
      
      router = APIRouter(prefix="/pdf", tags=["PDF Extraction"])
      
      
      @router.post("/{file_id}/extract")
      def extract_pdf_text(file_id: str):
    +     document = get_document_by_file_id(file_id)
    
    +     if not document:
    +         raise HTTPException(status_code=404, detail="Document not found")
    
    +     if document.get("status") == "EXTRACTED":
    +         return {
    +             "message": "Text already extracted",
    +             "file_id": file_id,
    +         }
      
          try:
              pdf_path = Path(get_pdf_path(file_id))
              text = extract_text_from_pdf(pdf_path)
      
    +         store_extracted_text(file_id, text)
      
              return {
                  "file_id": file_id,
                  "text_length": len(text),
                  "text_preview": text[:1000],  # prevent massive response
              }
      
          except PDFExtractionError as e:
              raise HTTPException(status_code=422, detail=str(e))
      ```

      which resolves the file path, extracts text, stores in MongoDB, and returns a preview. But now with the addition that if the document has already had its text extracted, it should give an error, rather than extracting again.

  * Later I can add:
 
    ```mongodb
    GET /pdf/{file_id}/text
    ```

    for when the user needs the full context.

  * To test, I re-ran: ``uvicorn app.main:app --reload --host 127.0.0.1 --port 8000``.
  * Uploading an invalid file:

    ```json
    {
      "detail": {
        "error": "File extension must be .pdf"
      }
    }
    ```
    
  * Uploading a valid PDF:
 
    ```json
    {
      "message": "PDF uploaded successfully",
      "metadata": {
        "file_id": "bcba93d7-8f17-4809-8598-53b9a0f5d96d",
        "filename": "Computer Simulation of Saturn's Ring Structure.pdf",
        "stored_filename": "bcba93d7-8f17-4809-8598-53b9a0f5d96d.pdf",
        "path": "E:\\...\\AI-Support-Agent\\app\\storage\\pdfs\\bcba93d7-8f17-4809-8598-53b9a0f5d96d.pdf",
        "size_bytes": 3026909,
        "content_type": "application/pdf"
      },
      "file_id": "bcba93d7-8f17-4809-8598-53b9a0f5d96d",
      "status": "UPLOADED"
    }
    ```

  * Extracting an invalid ID:
 
    ```json
    {
      "detail": "Document not found"
    }
    ```

  * Extracting a valid ID:
 
    ```json
    {
      "file_id": "bcba93d7-8f17-4809-8598-53b9a0f5d96d",
      "text_length": 42442,
      "text_preview": "Computer Simulation of Saturn’s Ring\nStructure\nNew Mexico\nSupercomputing Challenge\nFinal Report\nApril 3, 2013\nTeam 58\nLos Alamos High School\nTeam Members\nCole Kendrick\nTeachers\nBrian Kendrick\nProject Mentor\nBrian Kendrick\nSummary\nThe main goal of this project is to develop a computer program to model the creation of\nstructure in Saturn’s ring system. The computer program will be used to answer these\nquestions: (1) How are gaps in Saturn’s Rings formed; (2) how accurately can I model\ngap formation with a 3D N-Body simulation; and (3) will my simulation compare to\nobserved features, theoretical data, and professional simulations. Newton’s laws of\nmotion and gravity as well as the velocity Verlet method are being used to orbit the\nparticles around Saturn. Gaps in Saturn’s ring system are caused by three main methods:\n(1) Gravitational resonances; (2) moons that orbit inside the ring; and (3) an asteroid or\ncomet impact. Gravitational resonances are a major part of formation in the ring sy"
    }
    ```

  * Extracting a valid ID that has already been extracted:
 
    ```json
    {
      "message": "Text already extracted",
      "file_id": "bcba93d7-8f17-4809-8598-53b9a0f5d96d"
    }
    ```

  * On MongoDB the document goes from:
 
    ```
    _id: ObjectID('6940244cd59fc43fe0bd8d73')
    file_id: "bcba93d7-8f17-4809-8598-53b9a0f5d96d"
    original_filename: "Computer Simulation of Saturn's Ring Structure.pdf"
    stored_filename: "bcba93d7-8f17-4809-8598-53b9a0f5d96d.pdf"
    size_bytes: 3026909
    content_type: "application/pdf"
    status: "UPLOADED"
    created_at: 2025-12-15T15:07:56.295+00:00
    ```

    to:

    ```
    _id: ObjectID('6940244cd59fc43fe0bd8d73')
    file_id: "bcba93d7-8f17-4809-8598-53b9a0f5d96d"
    original_filename: "Computer Simulation of Saturn's Ring Structure.pdf"
    stored_filename: "bcba93d7-8f17-4809-8598-53b9a0f5d96d.pdf"
    size_bytes: 3026909
    content_type: "application/pdf"
    status: "UPLOADED"
    created_at: 2025-12-15T15:07:56.295+00:00
    extracted_at: 2025-12-15T15:12:47.007+00:00
    extracted_text: "Computer Simulation of Saturn’s Ring Structure New Mexico Supercomputi…"
    ```

    MongoDB Atlas UI automatically truncates ``extracted_text``, but quickly verifying by copying the document into Notepad proves that it does indeed store the entire document (5,889 words 43,604 characters).
    
  </details>

* <details><summary> New folder structure </summary>

    ```
    AI-Support-Agent/
      ├── app/
      │   ├── main.py
      │   ├── config.py
      │   ├── middleware/
      │   │   └── logging.py
      │   ├── services/
      │   │   ├── file_storage.py
      │   │   ├── pdf_service.py
      │   │   └── document_repository.py   <-- NEW
      │   ├── storage/
      │   │   └── pdfs/
      │   ├── core/
      │   │   └── errors.py
      │   ├── routers/
      │   │   ├── health.py
      │   │   ├── pdf_upload.py
      │   │   └── pdf_extract.py
      │   └── db/
      │       └── mongodb.py                <-- NEW
      ├── .env
      ├── .gitignore
      ├── requirements.txt
      └── README.md
    ```
  </details>

</details>

<details><summary> Day 6 - 16/12/25 </summary>

## Day 6 - 16/12/25

* <details><summary> Setup Qdrant </summary>

  * I chose to use Docker instead of a local binary as it means zero installation pain, same setup works in production later, easy persistance, and easy teardown/reset. Plus I already have Docker Desktop installed.
  * I opened Docker Desktop, waited for it to say "Docker Desktop is running", and verified by running ``docker version`` in cmd, which showed both Client and Server info.
  * I created a Qdrant persistence folder:
 
    ```
    AI-Support-Agent/
    └── qdrant_data/
    ```

    and added it to ``.gitignore``:

    ```
    # Qdrant local data
    qdrant_data/
    ```
    
  * Then I ran Qdrant with Docker:[^15]
 
    ```cmd
    docker run -d --name qdrant -p 6333:6333 -v "%cd%\qdrant_data:/qdrant/storage" qdrant/qdrant
    ```

    [^15]: Qdrant installation guide, https://qdrant.tech/documentation/guides/installation/#docker

  * Running ``docker ps`` I can see:
 
    ```cmd
    CONTAINER ID   IMAGE           COMMAND             CREATED          STATUS         PORTS                              NAMES
    792d5b6076b5   qdrant/qdrant   "./entrypoint.sh"   10 seconds ago   Up 6 seconds   0.0.0.0:6333->6333/tcp, 6334/tcp   qdrant
    ```

  * Added to ``requirements.txt``:
 
    ```
    qdrant-client
    ```

    and re-ran ``pip install -r requirements.txt``

  * Created a Qdrant client wrapper, ``app/db/qdrant.py``:[^16]
 
    ```py
    from qdrant_client import QdrantClient

    qdrant_client = QdrantClient(
        host="localhost",
        port=6333
    )
    ```
 
    similar to the client wrapper for MongoDB in ``app/db/mongodb.py``.
    
    [^16]: Qdrant Local Quickstart, https://qdrant.tech/documentation/quickstart/#initialize-the-client

  * Created a temporary test endpoint, ``app/routers/qdrant_health.py`` to verify backend can reach Qdrant:[^17]
 
    ```py
    from fastapi import APIRouter
    from app.db.qdrant import qdrant_client
    
    router = APIRouter(prefix="/qdrant", tags=["Qdrant"])
    
    @router.get("/health")
    def qdrant_health():
        collections = qdrant_client.get_collections()
        return {
            "status": "ok",
            "collections": [c.name for c in collections.collections]
        }
    ```

    [^17]: Qdrant API Reference - List all collections, https://api.qdrant.tech/v-1-12-x/api-reference/collections/get-collections

  * Updated ``main.py`` to include the new Qdrant router:
 
    ```py
    from app.routers.qdrant_health import router as qdrant_health_router

    app.include_router(qdrant_health_router)
    ```

  * And I can successfully see ``GET /qdrant/health`` which outputs:
 
    ```json
    {
      "status": "ok",
      "collections": []
    }
    ```

  </details>

* <details><summary> Create Vector Collection </summary>

  * For the distance metric I will use Cosine similarity over Euclidean distance as this allows it to focus on semantic direction (meaning) rather than vector magnitude (length).[^18]

    <img width="937" height="429" alt="image" src="https://github.com/user-attachments/assets/f94f676c-5c8b-4494-804d-e443aa53f3c5" />

    [^18]: What is Cosine similarity?, IBM, https://www.ibm.com/think/topics/cosine-similarity

  * The word embedding model we'll likely use is ``text-embedding-3-small`` from OpenAI which has a dimension size of 1536.[^19]
 
    [^19]: Vector embeddings, Open AI API, https://platform.openai.com/docs/guides/embeddings

  * I chose to name the collection ``documents_embeddings``, to make it clear what the embeddings are used for.

  * Here is how I implemented Qdrant client + collection creation in ``app/db/qdrant.py``:
 
    ```py
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams
    
    QDRANT_HOST = "localhost"
    QDRANT_PORT = 6333
    
    COLLECTION_NAME = "documents_embeddings"
    VECTOR_SIZE = 1536  # OpenAI embedding dimension
    
    
    def get_qdrant_client() -> QdrantClient:
        return QdrantClient(
            host=QDRANT_HOST,
            port=QDRANT_PORT,
        )
    
    
    def create_collection_if_not_exists():
        client = get_qdrant_client()
    
        collections = client.get_collections().collections
        existing_names = {c.name for c in collections}
    
        if COLLECTION_NAME in existing_names:
            return  # already exists
    
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )
    ```

    This is infrastructure, not routing. We don't want to recreate collections on every request.
    
  * Adding this to ``app/main.py`` create the collection once at startup:
 
    ```py
    from app.db.qdrant import create_collection_if_not_exists

    @app.on_event("startup")
    def startup_event():
        create_collection_if_not_exists()
    ```

  * And updating ``app/routers/qdrant_health.py``:
 
    ```diff
      from fastapi import APIRouter
    - from app.db.qdrant import qdrant_client
    + from app.db.qdrant import get_qdrant_client
      
      router = APIRouter(prefix="/qdrant", tags=["Qdrant"])
      
      @router.get("/health")
      def qdrant_health():
    -     collections = qdrant_client.get_collections()
    -     return {
    -         "status": "ok",
    -         "collections": [c.name for c in collections.collections]
    -     }
    +     try:
    +         client = get_qdrant_client()
    +         client.get_collections()
    +         return {"qdrant": "ok"}
    +     except Exception as e:
    +         raise HTTPException(status_code=500, detail=str(e))
    ```

  * Restarting the backend:

    ```cmd
    uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
    ```

  * And going to ``http://localhost:6333/collections
`` in the browser, I can successfully see:

    ```json
    {"result":{"collections":[{"name":"documents_embeddings"}]},"status":"ok","time":4.501e-6}
    ```

  * So we've successfully created a dedicated collection with cosine distance and fixed vector size aligned to OpenAI embeddings.

  </details>

* <details><summary> New folder structure </summary>

    ```
    AI-Support-Agent/
      ├── app/
      │   ├── main.py
      │   ├── config.py
      │   ├── middleware/
      │   │   └── logging.py
      │   ├── services/
      │   │   ├── file_storage.py
      │   │   ├── pdf_service.py
      │   │   └── document_repository.py
      │   ├── storage/
      │   │   └── pdfs/
      │   ├── core/
      │   │   └── errors.py
      │   ├── routers/
      │   │   ├── health.py
      │   │   ├── pdf_upload.py
      │   │   ├── pdf_extract.py
      │   │   └── qdrant_health.py    <-- NEW
      │   └── db/
      │       ├── mongodb.py
      │       └── qdrant.py           <-- NEW
      ├── qdrant_data/
      │   ├── ...
      │   └── collections/
      │       └── documents_embeddings/
      │           └── ...
      ├── .env
      ├── .gitignore
      ├── requirements.txt
      └── README.md
    ```
  </details>

</details>

<details><summary> Day 7 - 20/12/25 </summary>

## Day 7 - 20/12/25

* <details><summary> Generate Embeddings and Store Vectors in Qdrant </summary>

  <!--
  * In ``app/db/qdrant.py`` I switched back to the simpler singleton client rather than a ``get_qdrant_client()`` function.
 
    ``app/db/qdrant.py``:

    ```diff
    QDRANT_HOST = "localhost"
    QDRANT_PORT = 6333
    
    - def get_qdrant_client() -> QdrantClient:
    - return QdrantClient(
    -     host=QDRANT_HOST,
    -     port=QDRANT_PORT,
    - )
    
    + qdrant_client = QdrantClient(
    +     host=QDRANT_HOST,
    +     port=QDRANT_PORT,
    + )
    ```
  -->

  * In ``.env`` I added the OpenAI key, ``OPENAI_API_KEY=sk-xxxx``.[^20]

     [^20]: Developer quickstart | OpenAI API, https://platform.openai.com/docs/quickstart?desktop-os=windows

  * Added ``openai>=1.0.0`` to ``requirements.txt``.
  * Added to ``main.py``:
 
    ```py
    from dotenv import load_dotenv
    load_dotenv() # Load the environment variables
    ```

  * Added a function, ``get_document_text()`` to ``document_repository.py``:
 
    ```py
    def get_document_text(file_id: str) -> str | None:
        doc = documents_collection.find_one(
            {"file_id": file_id},
            {"extracted_text": 1}
        )
        return doc.get("extracted_text") if doc else None
    ```

  * Created ``app/services/embedding_service.py``:
 
    ```py
    import uuid
    
    from openai import OpenAI
    from app.db.qdrant import get_qdrant_client
    
    client = OpenAI()
    
    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 100
    EMBEDDING_MODEL = "text-embedding-3-small"
    
    
    def chunk_text(text: str):
        chunks = []
        start = 0
    
        while start < len(text):
            end = start + CHUNK_SIZE
            chunks.append(text[start:end])
            start += CHUNK_SIZE - CHUNK_OVERLAP
    
        return chunks
    
    
    def embed_and_store(file_id: str, text: str):
        chunks = chunk_text(text)

        qdrant_client = get_qdrant_client()
    
        embeddings = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=chunks
        )
    
        points = []
        for idx, emb in enumerate(embeddings.data):
            points.append({
                "id": str(uuid.uid4()),
                "vector": emb.embedding,
                "payload": {
                    "file_id": file_id,
                    "chunk_index": idx,
                    "text": chunks[idx],
                }
            })
    
        qdrant_client.upsert(
            collection_name="documents_embeddings",
            points=points
        )
    
        return len(points)
    ```

  * Created ``app/routers/embeddings.py``:
 
    ```py
    from fastapi import APIRouter, HTTPException
    from app.services.document_repository import get_document_text
    from app.services.embedding_service import embed_and_store
    
    router = APIRouter(prefix="/embeddings", tags=["Embeddings"])
    
    
    @router.post("/{file_id}")
    def generate_embeddings(file_id: str):
        text = get_document_text(file_id)
        if not text:
            raise HTTPException(status_code=404, detail="No extracted text found")
    
        count = embed_and_store(file_id, text)
    
        return {
            "file_id": file_id,
            "chunks_embedded": count
        }
    ```

  * Then registered the router in ``main.py``:
 
    ```py
    from app.routers.embeddings import router as embeddings_router
    app.include_router(embeddings_router)
    ```

  * Restarting Docker Desktop, then running ``docker start qdrant``, and finally starting FastAPI with ``uvicorn app.main:app --reload --host 127.0.0.1 --port 8000``, I can see ``POST /embeddings/{file_id}`` in SwaggerUI. Entering a valid file ID gives me this response:
 
    ```json
    {
      "file_id": "27ff3caa-2fbc-4418-b16f-bbb0af29c4a9",
      "chunks_embedded": 2
    }
    ```
 
    which tells me that the PDF was successfully loaded, and ``"chunks_embedded": 2`` tells me that the PDF was split into 2 chunks. Each chunk was embedded using the OpenAI embedding model ``text-embedding-3-small``, and each embedding was stored in Qdrant.

    When going to ``http://localhost:6333/collections/documents_embeddings``, I can see:

    ```json
    {
      "result":{
        "status":"green",
        "optimizer_status":"ok",
        "indexed_vectors_count":0,
        "points_count":2,
        "segments_count":2,
        "config":{
          "params":{
            "vectors":{"size":1536,"distance":"Cosine"},
            "shard_number":1,
            "replication_factor":1,
            "write_consistency_factor":1,
            "on_disk_payload":true
          },
          "hnsw_config":{"m":16,"ef_construct":100,"full_scan_threshold":10000,"max_indexing_threads":0,"on_disk":false},
          "optimizer_config":{"deleted_threshold":0.2,"vacuum_min_vector_number":1000,"default_segment_number":0,"max_segment_size":null,"memmap_threshold":null,"indexing_threshold":10000,"flush_interval_sec":5,"max_optimization_threads":null},
          "wal_config":{"wal_capacity_mb":32,"wal_segments_ahead":0,"wal_retain_closed":1},
          "quantization_config":null
        },
        "payload_schema":{}
      },
      "status":"ok",
      "time":0.000322229
    }
    ```

    ``"points_count": 2`` tells me that 2 vectors exist, they are persisted, they belong to the documents_embeddings collection, and the collection is healthy (status: green). The ``text-embedding-3-small`` model produces a 1536-dimensional vector for each chunk (numeric representation of its semantic meaning), 2 chunks means 2 vectors.

  * This all works fine, but I noticed that when I try generate embeddings for a PDF I've already used, it works and generates duplicate embeddings, ``"points_count"`` keeps increasing. The reason for this is that I set the ``"id"`` for the point in ``embed_and_store()`` in ``app/services/embedding_service.py`` to be ``str(uuid.uuid4())``. This creates a valid UUID but the problem is that it is unique even for duplicate PDFs, to make it deterministic, I tried doing ``f"{file_id}_{idx}"`` to make it deterministic, however I got an error saying it was not a valid UUID. The solution was to use uui5 like so:

    ```py
    points = []
    for idx, emb in enumerate(embeddings.data):
        base_uuid = uuid.UUID(file_id)
        point_id = uuid.uuid5(base_uuid, str(idx))
        
        points.append({
            # "id": str(uuid.uuid4()), # valid UUID but not deterministic
            # "id": f"{file_id}_{idx}", # deterministic but not valid UUID
            "id": str(point_id), # valid UUID and deterministic
            "vector": emb.embedding,
            "payload": {
                "file_id": file_id,
                "chunk_index": idx,
                "text": chunks[idx],
            }
        })
    ```

    now when I try to generate embeddings for the same PDF, it rewrites the old one, instead of making duplicate embeddings.

  * To delete the embeddings and start from scratch, I firstly did ``docker stop qdrant``, then deleted the ``/qdrant_data`` folder (will get automatically recreated), then ran ``docker start qdrant``, and finally restarted FastAPI by doing ``uvicorn app.main:app --reload``. In ``http://localhost:6333/collections`` I can see:
 
    ```
    {"result":{"collections":[{"name":"documents_embeddings"}]},"status":"ok","time":4.6e-6}
    ```

    and in ``http://localhost:6333/collections/documents_embeddings`` I can see ``"points_count"0``. When I generate embeddings for a PDF it now says ``"points_count":2``, and when I try to generate embeddings again for the same PDF it stays at ``"points_count":2``.

  </details>
  
* <details><summary> New folder structure </summary>

    ```
    AI-Support-Agent/
      ├── app/
      │   ├── main.py
      │   ├── config.py
      │   ├── middleware/
      │   │   └── logging.py
      │   ├── services/
      │   │   ├── file_storage.py
      │   │   ├── pdf_service.py
      │   │   ├── document_repository.py
      │   │   └── embedding_service.py       <-- NEW
      │   ├── storage/
      │   │   └── pdfs/
      │   ├── core/
      │   │   └── errors.py
      │   ├── routers/
      │   │   ├── health.py
      │   │   ├── pdf_upload.py
      │   │   ├── pdf_extract.py
      │   │   ├── qdrant_health.py
      │   │   └── embeddings.py              <-- NEW
      │   └── db/
      │       ├── mongodb.py
      │       └── qdrant.py
      ├── qdrant_data/
      │   └── ...
      ├── .env
      ├── .gitignore
      ├── requirements.txt
      └── README.md
    ```
  </details>

</details>

<details><summary> Day 8 - 25/12/25 </summary>

## Day 8 - 25/12/25

* <details><summary> Setting up the project in Arch Linux on my laptop </summary>

  * In order to setup the project in Arch Linux on my laptop I simply cloned the repo, and installed the necessary prerequisites:

    ```console
    sudo pacman -S python docker docker-compose git
    ```

  * Enable Docker:
 
    ```console
    sudo systemctl enable docker
    sudo systemctl start docker
    ```

    running:

    ```console
    systemctl status docker
    ```

    I can see:

    ```console
    Active: active (running)
    ```

    In order to use certain Docker commands, I needed to add my user to the docker group:

    ```console
    sudo usermod -aG docker $USER
    ```

    and reboot.

    

  * Created a virtual environment:
 
    ```console
    python -m venv .venv
    source .venv/bin/activate
    ```

    and verifying with:

    ```console
    echo $VIRTUAL_ENV
    ```

  * Installed Python deps:
 
    ```console
    pip install -r requirements.txt
    ```

  * Copied the .env file from my PC to my laptop (never pushed to Git):
 
    ```env
    OPENAI_API_KEY=sk-...
    MONGODB_URI=...
    ENVIRONMENT=development
    ```

  * Started MongoDB Atlas (ensuring laptop IP is allowed)
  * Started Qdrant (local to laptop):
 
    ```console
    docker run -d --name qdrant -p 6333:6333 -v $(pwd)/qdrant_data:/qdrant/storage qdrant/qdrant
    ```

  and verifying with ``docker ps``. This creates the local ``qdrant_data/``.

  * And lastly, restarted FastAPI:
 
    ```console
    uvicorn app.main:app --reload
    ```

  * I just noticed that the FastAPI website allows you to upload the same PDF multiple times, in the future I might fix it so that it doesn't let you upload the same PDF again.
    
  </details>

* <details><summary> Vector Search Endpoint </summary>

  * Created ``app/core/embeddings.py`` to centralize embedding settings which other files can access:
 
    ```py
    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIM = 1536
    ```

    I found it useful using this ``grep`` command to recursively find all occurrences of the string "1536" in files in the project folder:[^21]

    ```console
    grep -r "1536" .
    ```

    [^21]: How to use "grep" command to find text including subdirectories, askubuntu.com, https://askubuntu.com/a/55333

  * Created ``app/services/search_service.py``:
 
    ```py
    from openai import OpenAI
    from qdrant_client.models import ScoredPoint
    from app.db.qdrant import get_qdrant_client, COLLECTION_NAME
    from app.core.embeddings import EMBEDDING_MODEL
    
    client = OpenAI()
    
    def search_similar_chunks(query: str, top_k: int = 5):
        qdrant_client = get_qdrant_client()
    
        # 1. Embed the query
        query_embedding = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=query
        ).data[0].embedding
    
        # 2. Query Qdrant
        results: list[ScoredPoint] = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            limit=top_k,
        ).points
    
        # 3. Shape response
        return [
            {
                "score": point.score,
                "file_id": point.payload["file_id"],
                "chunk_index": point.payload["chunk_index"],
                "text": point.payload["text"],
            }
            for point in results
        ]
    ```

    I was having trouble getting this set up but the mistake was that I was not using the correct Qdrant function to do searching. For the latest version of Qdrant, the correct function is ``.query_points(...)``.[^22]

    [^22]: Search - Qdrant, https://qdrant.tech/documentation/concepts/search/

  * Created the router, ``app/routers/search.py``, which uses the ``search_similar_chunks(query, top_k)`` function defined in ``search_service.py``:
 
    ```py
    from fastapi import APIRouter, HTTPException
    from app.services.search_service import search_similar_chunks
    
    router = APIRouter(prefix="/search", tags=["Vector Search"])
    
    
    @router.post("/")
    def vector_search(query: str, top_k: int = 5):
        try:
            results = search_similar_chunks(query, top_k)
            return {
                "query": query,
                "top_k": top_k,
                "results": results
            }
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    ```

  * As I am now on my laptop, it has its own local ``qdrant_data/`` folder with its own embeddings.
  * After generating embeddings for PDFs saved already in MongoDB Atlas, and verifying by checking that ``points_count`` > 0 in ``http://localhost:6333/collections/documents_embeddings
``, I entered the query "Saturn's rings" into Vector Search ``POST /search/`` and set ``top_k`` to 5, which returned:
 
    ```json
    {
      "query": "Saturn's rings",
      "top_k": 5,
      "results": [
        {
          "score": 0.68428075,
          "file_id": "bcba93d7-8f17-4809-8598-53b9a0f5d96d",
          "chunk_index": 11,
          "text": "’s rings are\nsymmetrical, splitting the rings into a small patch would allow for a higher particle\ndensity and pickup more moon interactions. The Patch method (shown below in Figure\n6) is another way for computing Saturn’s rings without modeling the whole entire\nsystem. Ring particles are now distributed within the patch area which is determined by\nthe angle Δθ. The particles orbit Saturn moving downward, when a particle exceeds the\npatch boundary it is rotated by the angle Δθ to the top of the patch. Each particle has a\ncounter that gets incremented when that particle gets ‘reset’. This counter allows the\nprogram to be able to compute the actual position of the particle as if it were normally\norbiting Saturn. The moons orbit normally around Saturn.\n8\nFigure 6: Diagram of the patch method,"
        },
        {
          "score": 0.6666744,
          "file_id": "bcba93d7-8f17-4809-8598-53b9a0f5d96d",
          "chunk_index": 40,
          "text": "467. Print.\nEsposito, L. “Structure and Evolution of Saturn's Rings.” Icarus 67 (1986): 345-357.\nPrint.\nDones, L. “A Recent Cometary Origin for Saturn's Rings?” Icarus 92 (1991): 194-203.\nPrint.\nColwell, E. J. “ The disruption of planetary satellites and the creation of planetary\nrings.” Planet Space Sci. Vol 42, No. 12. (1994): 1139-1149. Print.\nMurray, C. D., Beurle, K., Cooper, J. N.., Evans, W. M.., Williams, A. G.., Charnoz, S..\n“The determination of the struction of Saturn's F ring by nearby moonlets.” Nature Vol.\n453. (2008). Print.\nHvoždara, M., Kohút, I. “Gravity field due to a homogeneous oblate spheroid: Simple\nsolution form and numerical calculations.” Contributions to Geophysics and Geodesy\nVol. 41/4 (2001): 307-327). Print.\nNdikilar, C., Usman, A., Meludu, O. “Gravitational S"
        },
        {
          "score": 0.6467543,
          "file_id": "bcba93d7-8f17-4809-8598-53b9a0f5d96d",
          "chunk_index": 7,
          "text": "individual ring particles randomly\ndistributed from Saturn’s D Ring to the edge of Saturn’s F ring which accounts for the\nvisible sections of the ring system. These particles orbit around Saturn using Newton's\nLaws of gravity and the Velocity Verlet method. My simulation currently treats 15 of the\nmost important moons. Due to the large force particles feel from Saturn, the moon\ninteractions are captured in separate R , V , and A arrays. If the moon\nmoon moon moon\ninteractions are included in the original R, V, and A arrays, their effects get essentially\nburied due to the large interaction from Saturn. This causes the moon effects to never\nadd up significantly (they are smaller than the numerical errors). Including moon\ninteractions in a separate array allows the simulation to pick up moon "
        },
        {
          "score": 0.6463238,
          "file_id": "bcba93d7-8f17-4809-8598-53b9a0f5d96d",
          "chunk_index": 9,
          "text": " the ring system changed as different moons were\nadded or subtracted. Most simulations were run with one million ring particles and a\none second time step. Figure 4 (below) compares a detailed photo of Saturn’s ring\nstructure with my 3D simulation results. Velocity magnitude is plotted, showing spikes\nwhich are due to interactions from the moons (labeled with the numbers). The five\nspikes on the right edge are due to moons that orbit within the ring. The other three\nspikes toward the middle of the ring are caused by resonances. The 2:1 resonance with\nMimas mentioned earlier is the largest resonance picked up by my simulation. These\nspikes from the moon interactions match up with the structure of Saturn’s ring which\nproves that my simulation is able to pickup large features of the ring syst"
        },
        {
          "score": 0.6439747,
          "file_id": "bcba93d7-8f17-4809-8598-53b9a0f5d96d",
          "chunk_index": 43,
          "text": "ordi, J., Criddle, K., Ionasescu, R., Jones, J., Mackenzie,\nR., Meek, M., Parcher, D., Pelletier, F., Owen, W. Jr., Roth, D., Roundhill, I., Stauch, J.\n“The Gravity Field of the Saturnian System From Satellite Observations and Spacecraft\nTracking Data.” The Astronomical Journal 132 (2006): 2520-2526. Print.\nCuzzi, J., Burns, J., Charnoz, S., Clark, R., Colwell, J., Dones. L., Esposito, L.,\nFilacchione, G., French, R., Hedman, M., Kempf, S., Marouf, E., Murray, C., Nicholson,\nP., Porco, C., Schmidt, J. Showalter, M., Spilker, L., Spitale, J., Srama, R., Sremčević,\nM., Tiscareno, M., Weiss, J. “An Evolving View of Saturn's Dynamic Rings.” Science\n327 (2010): 1470. Print.\nGoldreich, P., Tremaine, S. “The Dynamics of Planetary Rings.” Ann. Rev. Astron.\nAstrophys. 20 (1982):249-283. Print.\nMeye"
        }
      ]
    }
    ```

  </details>

* <details><summary> Simple Re-Ranking Thinking Task </summary>

  1. Score threshold filtering (high priority)

     * **Idea:** Discard results below a minimum similarity score (e.g. cosine similarity < 0.5)
     * Vector search currently always returns results, even those which are weakly related. A threshold prevents irrelevant chunks being included.
     * Could make the threshold adjustable.

  2. Chunk-level re-ranking with keyword boosting

     * **Idea:** Re-rank results by combining vector similarity score with keyword overlap between query and chunk text.
     * Embeddings capture semantics but can miss exact terms (names, numbers, technical keywords). keyword overlap boosts precision.
     * Light text matching (no NLP required).
     * Hybrid scoring: ``final_score = 0.7 * vector_score + 0.3 * keyword_score``
    
  3. Document-level aggregation & de-duplication

     * **Idea:** Group chunks by `file_id`` and avoid returning too many chunks from the same document.
     * Prevents a single document from dominating results and improves answer diversity.
     * Limit max chunks per document (e.g. 2-3).
    
     * Rank documents first, then chunks within them.

  4. Recency bias

     * **Idea:** Prefer newer documents when similarity scores are close.
     * In real systems, newer documents often contain more relevant or updated information.
     * Add a slight score boost for recency.
     * Requires ``created_at``/``uploaded_at`` metadata.

  5. Contextual chunk expansion (low priority)

     * **Idea:** When a chunk is selected, also include adjacent chunks (``chunk_index ± 1``) for better context.
     * PDF chunking can split important sentences across boundaries.
     * Used only after top results are chosen.
     * Expands conext without polluting retrieval stage.

  </details>

* <details><summary> New folder structure </summary>

    ```
    AI-Support-Agent/
      ├── app/
      │   ├── main.py
      │   ├── config.py
      │   ├── middleware/
      │   │   └── logging.py
      │   ├── services/
      │   │   ├── file_storage.py
      │   │   ├── pdf_service.py
      │   │   ├── document_repository.py
      │   │   ├── embedding_service.py
      │   │   └── search_service.py          <-- NEW
      │   ├── storage/
      │   │   └── pdfs/
      │   ├── core/
      │   │   ├── errors.py
      │   │   └── embeddings.py              <-- NEW
      │   ├── routers/
      │   │   ├── health.py
      │   │   ├── pdf_upload.py
      │   │   ├── pdf_extract.py
      │   │   ├── qdrant_health.py
      │   │   ├── embeddings.py
      │   │   └── search.py                  <-- NEW
      │   └── db/
      │       ├── mongodb.py
      │       └── qdrant.py
      ├── qdrant_data/
      │   └── ...
      ├── .env
      ├── .gitignore
      ├── requirements.txt
      └── README.md
    ```
  </details>

</details>

<details><summary> Day 9 - 28/12/25 </summary>

## Day 9 - 28/12/25

* <details><summary> Chat Completion </summary>

  * Created ``app/services/chat_service.py``:
 
    ```py
    from openai import OpenAI

    client = OpenAI()
    
    MODEL = "gpt-4o-mini"
    
    SYSTEM_PROMPT = (
        "You are an AI assistant that answers questions using ONLY the provided context. "
        "If the answer is not contained in the context, say you do not know."
    )
    
    def generate_answer(question: str, context_chunks: list[str]) -> str:
        if not context_chunks:
            return "I do not know based on the provided documents."
    
        context = "\n\n---\n\n".join(context_chunks)
    
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""
    Context:
    {context}
    
    Question:
    {question}
    """
            },
        ]
    
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.2,  # lower = less creative, more factual
        )
    
        return response.choices[0].message.content
    ```

  * And created its accompanying router, ``app/router/chat.py``:
 
    ```py
    from fastapi import APIRouter, Query
    from app.services.search_service import search_similar_chunks
    from app.services.chat_service import generate_answer
    
    router = APIRouter(prefix="/chat", tags=["Chat"])
    
    
    @router.post("")
    def chat(
        question: str = Query(..., min_length=3),
        top_k: int = Query(3, ge=1, le=5),
    ):
        # 1. Retrieve relevant chunks
        results = search_similar_chunks(question, top_k)
    
        chunks = [r["text"] for r in results]
    
        # 2. Generate answer
        answer = generate_answer(question, chunks)
    
        return {
            "question": question,
            "answer": answer,
            "chunks_used": len(chunks),
        }
    ```

  * Hooked the router to ``main.py``:
 
    ```py
    from app.routers.chat import router as chat_router

    app.include_router(chat_router)
    ```

  * I can now see the ``POST /chat`` endpoint in SwaggerUI (``http://127.0.0.1:8000/docs``).
  * However, when I entered the prompt: "What causes the structure seen in Saturn’s rings according to the paper?" with ``top_k`` = 5, it just returned:
 
    ```json
    {
      "question": "What causes the structure seen in Saturn’s rings according to the paper?",
      "answer": "I do not know.",
      "chunks_used": 5
    }
    ```

  * My first guess was that the Saturn pdf was not embedded correctly, but I could see that it was as I had re-generated embeddings and could see ``points_count`` > 0 in ``http://localhost:6333/collections/documents_embeddings``.
  * The issue was actually just that the ``SYSTEM_PROMPT`` in ``app/services/chat_service.py`` was too strict.
  * I changed ``SYSTEM_PROMPT``:
 
    ```diff
    - SYSTEM_PROMPT = (
    -     "You are an AI assistant that answers questions using ONLY the provided context. "
    -     "If the answer is not contained in the context, say you do not know."
    - )
    
    + SYSTEM_PROMPT = (
    +     "You are an AI assistant answering questions based on the provided context from a document. "
    +     "Use the context to infer and summarize the answer when possible. "
    +     "If the context does not contain enough information to answer, say you do not know."
    + )
    ```

    and now when I enter the prompt: "What causes the structure seen in Saturn’s rings according to the paper?" with ``top_k`` = 5 into ``POST /chat`` it returns:

    ```json
    {
      "question": "What causes the structure seen in Saturn’s rings according to the paper?",
      "answer": "The structure seen in Saturn's rings is influenced by various factors, including the gravitational effects of nearby moonlets, as indicated by the work of Murray et al. (2008) and other studies. Additionally, the formation of structures such as \"braids\" in the F Ring is discussed by Lissauer and Peale (1986), while the role of shepherding satellites in maintaining sharp edges and other features in the rings is highlighted by Borderies et al. (1982) and others. Overall, gravitational interactions and the dynamics of ring particles play a significant role in shaping the structure of Saturn's rings.",
      "chunks_used": 5
    }
    ```

  * This is a good response, however I notice that it does not mention "resonances" in its answer for "What causes the structure seen in Saturn’s rings according to the paper?", which is one of the main reasons and is mentioned in the PDF. We can fix that later with better chunk selection / re-ranking.
    
  </details>

* <details><summary> Multi-Turn Conversation Handling </summary>

  * Added ``app/services/conversation_service.py``:
 
    ```py
    from datetime import datetime
    from uuid import uuid4
    from app.db.mongodb import db
    
    
    MAX_MESSAGES = 10  # keep last N messages total
    
    
    def create_conversation() -> str:
        conversation_id = str(uuid4())
        db.conversations.insert_one({
            "conversation_id": conversation_id,
            "messages": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        })
        return conversation_id
    
    
    def get_messages(conversation_id: str) -> list[dict]:
        convo = db.conversations.find_one(
            {"conversation_id": conversation_id},
            {"_id": 0, "messages": 1}
        )
        return convo["messages"] if convo else []
    
    
    def add_message(conversation_id: str, role: str, content: str):
        db.conversations.update_one(
            {"conversation_id": conversation_id},
            {
                "$push": {
                    "messages": {
                        "$each": [{
                            "role": role,
                            "content": content,
                            "timestamp": datetime.utcnow(),
                        }],
                        "$slice": -MAX_MESSAGES,
                    }
                },
                "$set": {"updated_at": datetime.utcnow()},
            },
            upsert=True,
        )
    ```

    specifing ``MAX_MESSAGES = 10`` limits the memory window to the last 10 messages (5 from the user, 5 from the AI).

  * Updated ``app/routers/chat.py``:
 
    ```diff
    - from fastapi import APIRouter, Query
    + from fastapi import APIRouter
    + from pydantic import BaseModel
    + from typing import Optional
    
      from app.services.search_service import search_similar_chunks
      from app.services.chat_service import generate_answer
    + from app.services.conversation_service import (
          create_conversation,
          get_messages,
          add_message,
      )
    
      router = APIRouter(prefix="/chat", tags=["Chat"])
      
    + class ChatRequest(BaseModel):
    +     question: str
    +     top_k: int = 5
    +     conversation_id: Optional[str] = None

    
      @router.post("")
    - def chat(
    -     question: str = Query(..., min_length=3),
    -     top_k: int = Query(3, ge=1, le=5),
    - ):
    -     # 1. Retrieve relevant chunks
    -     results = search_similar_chunks(question, top_k)
    - 
    -     chunks = [r["text"] for r in results]
    - 
    -     # 2. Generate answer
    -     answer = generate_answer(question, chunks)
    - 
    -     return {
    -         "question": question,
    -         "answer": answer,
    -         "chunks_used": len(chunks),
    -     }
    + def chat(request: ChatRequest):
    + # 1. Create or reuse conversation
    + conversation_id = request.conversation_id
    + if not conversation_id:
    +     conversation_id = create_conversation()
    +
    + # 2. Load previous messages
    + previous_messages = get_messages(conversation_id)
    +
    + # 3. Vector search
    + search_results = search_similar_chunks(
    +     request.question,
    +     top_k=request.top_k,
    + )
    +
    + context_chunks = [r["text"] for r in search_results]
    +
    + # 4. Generate answer
    + answer = generate_answer(
    +     question=request.question,
    +     context_chunks=context_chunks,
    + )
    +
    + # 5. Store messages
    + add_message(conversation_id, "user", request.question)
    + add_message(conversation_id, "assistant", answer)
    +
    + # 6. Return response
    + return {
    +     "conversation_id": conversation_id,
    +     "question": request.question,
    +     "answer": answer,
    +     "chunks_used": len(context_chunks),
    + }
    ```

  * Now in SwaggerUI, ``POST /chat`` is a single input box to paste a JSON-formatted request, rather than input parameters.
  * When I click "Try it now" and edit the input box to be:
 
    ```json
    {
      "question": "What causes the structure of Saturn’s rings?",
      "top_k": 5
    }
    ```

    and click "Execute", it outputs:

    ```json
    {
      "conversation_id": "e90daf47-2d73-4211-9ee0-76864312225c",
      "question": "What causes the structure of Saturn’s rings?",
      "answer": "The structure of Saturn's rings is influenced by various factors, including gravitational interactions with nearby moons, the dynamics of ring particles, and the effects of resonances. For example, studies have shown that moonlets, such as Prometheus, create structure in Saturn's F Ring through their gravitational influence. Additionally, the formation of features like \"braids\" and the Cassini Division can be attributed to gravitational perturbations and the stability of the ring particles. The dynamics of the particles, including their distribution and interactions, also play a crucial role in shaping the rings' structure.",
      "chunks_used": 5
    }
    ```

    and when I then input (using the ``conversation_id`` above):

    ```json
    {
      "question": "What role do resonances play?",
      "top_k": 5,
      "conversation_id": "e90daf47-2d73-4211-9ee0-76864312225c"
    }
    ```

    it outputs:

    ```json
    {
      "conversation_id": "e90daf47-2d73-4211-9ee0-76864312225c",
      "question": "What role do resonances play?",
      "answer": "Resonances play a crucial role in the dynamics of Saturn's ring system by influencing the orbits of ring particles. They occur when the gravitational effects of moons interact with the particles in the rings, causing specific locations in the ring to experience increased acceleration. This leads to shifts in the orbits of the particles at resonance locations, which can result in the formation of gaps within the rings. For example, the 2:1 resonance with the moon Mimas creates the Huygen’s gap in the Cassini Division. Resonances depend on the stability of the moon's orbit; if the moon's orbit changes, the resonance location will also change, affecting the overall structure of the rings.",
      "chunks_used": 5
    }
    ```

    showing that it understood the context of the question from the earlier question in the conversation.
  * Omitting ``conversation_id`` creates a new conversation.
  * Providing an existing ``conversation_id`` resumes that conversation.

  * In MongoDB Atlas I can see the new ``conversations`` collection, which has the current conversation saved:
 
    ```shell
    _id: ObjectId('69514c2d51d8879031f840e0')
    conversation_id: "e90daf47-2d73-4211-9ee0-76864312225c"
    messages: Array (4)
      0: Object
        role: "user"
        content: "What causes the structure of Saturn’s rings?"
        timestamp: 2025-12-28T15:26:43.037+00:00
      1: Object
        role: "assistant"
        content: "The structure of Saturn's rings is influenced by various factors, incl…"
        timestamp: 2025-12-28T15:26:43.072+00:00
      2: Object
        role: "user"
        content: "What role do resonances play?"
        timestamp: 2025-12-28T15:28:10.931+00:00
      3: Object
        role: "assistant"
        content: "Resonances play a crucial role in the dynamics of Saturn's ring system…"
        timestamp: 2025-12-28T15:28:10.966+00:00
    created_at: 2025-12-28T15:26:37.043+00:00
    updated_at: 2025-12-28T15:28:10.966+00:00
    ```

    which means chat history is persistant (I can continue the same conversation from another machine, so long as I know the ``conversation_id``. In practice, the website could provide a list of current ``conversation_id``'s instead of the user needing to remember/store them.

  * One thing I could add later is a way to delete conversations from memory by providing the ``conversation_id``.

  </details>
  
* <details><summary> New folder structure </summary>

    ```
    AI-Support-Agent/
      ├── app/
      │   ├── main.py
      │   ├── config.py
      │   ├── middleware/
      │   │   └── logging.py
      │   ├── services/
      │   │   ├── file_storage.py
      │   │   ├── pdf_service.py
      │   │   ├── document_repository.py
      │   │   ├── embedding_service.py
      │   │   ├── search_service.py
      │   │   ├── chat_service.py            <-- NEW
      │   │   └── conversation_service.py    <-- NEW
      │   ├── storage/
      │   │   └── pdfs/
      │   ├── core/
      │   │   ├── errors.py
      │   │   └── embeddings.py
      │   ├── routers/
      │   │   ├── health.py
      │   │   ├── pdf_upload.py
      │   │   ├── pdf_extract.py
      │   │   ├── qdrant_health.py
      │   │   ├── embeddings.py
      │   │   ├── search.py
      │   │   └── chat.py                    <-- NEW
      │   └── db/
      │       ├── mongodb.py
      │       └── qdrant.py
      ├── qdrant_data/
      │   └── ...
      ├── .env
      ├── .gitignore
      ├── requirements.txt
      └── README.md
    ```
  </details>

</details>

<details><summary> Day 10 - 28/12/25 </summary>

## Day 10 - 28/12/25

* <details><summary> First Full Demo </summary>

  * In the previous Day, I tested uploading a document, asking a question, and getting an answer.

  </details>

* <details><summary> Code Cleanup </summary>

  * I have removed unused files and added comments where necessary.

  </details>

</details>

<details><summary> Day 11 - 28/12/25 </summary>

## Day 11 - 28/12/25

* <details><summary> Simple Chat UI and Connect to Backend </summary>

  * Verified that ``Node.js LTS`` is installed:
 
    ```console
    node -v
    npm -v
    ```

  * Created the frontend (running from project root):
 
    ```console
    npm create vite@latest frontend -- --template react-ts
    ```

    which creates the ``frontend/`` folder. I selected "No" to "Use rolldown-vite (Experimental)?", and "Yes" to "Install with npm and start now?".

    Equivalently, I could've manually done:

    ```console
    cd frontend
    npm install  # first time only
    npm run dev
    ```

  * Going to ``http://localhost:5173``, I can see the default Vite + React page.
 
  * Updating ``frontend/src/App.tsx``:
 
    ```tsx
    import { useState } from "react";
    
    type Message = {
      role: "user" | "assistant";
      content: string;
    };
    
    function App() {
      const [messages, setMessages] = useState<Message[]>([]);
      const [question, setQuestion] = useState("");
      const [conversationId, setConversationId] = useState<string | null>(null);
      const [loading, setLoading] = useState(false);
    
      const sendMessage = async () => {
        if (!question.trim()) return;
    
        const userMessage: Message = { role: "user", content: question };
        setMessages((prev) => [...prev, userMessage]);
        setQuestion("");
        setLoading(true);
    
        const body: any = {
          question,
          top_k: 5,
        };
    
        if (conversationId) {
          body.conversation_id = conversationId;
        }
    
        const res = await fetch("http://localhost:8000/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
    
        const data = await res.json();
    
        setConversationId(data.conversation_id);
    
        const assistantMessage: Message = {
          role: "assistant",
          content: data.answer,
        };
    
        setMessages((prev) => [...prev, assistantMessage]);
        setLoading(false);
      };
    
      return (
        <div style={{ maxWidth: 600, margin: "40px auto", fontFamily: "sans-serif" }}>
          <h2>Chatbot</h2>
    
          <div style={{ border: "1px solid #ccc", padding: 12, minHeight: 300 }}>
            {messages.map((m, i) => (
              <div key={i} style={{ marginBottom: 10 }}>
                <strong>{m.role === "user" ? "You" : "AI"}:</strong>
                <div>{m.content}</div>
              </div>
            ))}
            {loading && <div>Thinking...</div>}
          </div>
    
          <div style={{ display: "flex", marginTop: 10 }}>
            <input
              style={{ flex: 1, padding: 8 }}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            />
            <button onClick={sendMessage} style={{ marginLeft: 8 }}>
              Send
            </button>
          </div>
        </div>
      );
    }
    
    export default App;
    ```

  * I can now see a simple input box titled "Chatbot" and a basic send button. After asking it a question related to one of the chunked and embedded PDFs, it gave a correct answer. And when asking a follow-up question that required context from the previous conversation, it correctly understood and output a correct response:
 
    <img width="627" height="471" alt="image" src="https://github.com/user-attachments/assets/2531d7bb-4350-4601-b73c-5ec9b46c2bf1" />

    Frontend sends ``POST /chat`` with basic fetch ``fetch("http://localhost:8000/chat", { ... })``, FastAPI responds with JSON, UI renders the answer.

  * There is a ``Thinking...`` state UI to indicate the query response is being processed. Implemented with:

    ```tsx
    const [loading, setLoading] = useState(false);
    ```

    and

    ```tsx
    <button disabled={loading}>
      {loading ? "Thinking..." : "Send"}
    </button>
    ```

  * In MongoDB Atlas, in ``ai_support_agent/conversations/``, I can see the new conversation:
 
    ```cmd 
    _id: ObjectId('6951792c04fac433b03d0ca7')
    conversation_id: "0f840df9-890b-4fa9-8edb-ae5ae0731436"
    messages: Array (4)
      0: Object
        role: "user"
        content: "What address do I send documents to be legalised?"
        timestamp: 2025-12-28T18:38:42.424+00:00
      1: Object
        role: "assistant"
        content: "You should send your documents and cover sheet via Royal Mail tracked …"
        timestamp: 2025-12-28T18:38:42.468+00:00
      2: Object
        role: "user"
        content: "Can you repeat the postcode and delivery service?"
        timestamp: 2025-12-28T18:39:49.108+00:00
      3: Object
        role: "assistant"
        content: "The postcode is MK11 9NS, and the delivery service is Royal Mail track…"
        timestamp: 2025-12-28T18:39:49.147+00:00
    created_at: 2025-12-28T18:38:36.027+00:00
    updated_at: 2025-12-28T18:39:49.147+00:00

  * Later I would like to implement conversation-switching to the frontend, to allow to user to switch between conversations or create a new conversation.
  * I also notice that when refreshing the page, the conversation is reset. This is expected as we haven't implemented a feature to retrieve the last conversation from MongoDB yet.
 
* <details><summary> New folder structure </summary>

    ```
    AI-Support-Agent/
      ├── app/
      │   ├── main.py
      │   ├── config.py
      │   ├── middleware/
      │   │   └── logging.py
      │   ├── services/
      │   │   ├── file_storage.py
      │   │   ├── pdf_service.py
      │   │   ├── document_repository.py
      │   │   ├── embedding_service.py
      │   │   ├── search_service.py
      │   │   ├── chat_service.py
      │   │   └── conversation_service.py
      │   ├── storage/
      │   │   └── pdfs/
      │   ├── core/
      │   │   ├── errors.py
      │   │   └── embeddings.py
      │   ├── routers/
      │   │   ├── health.py
      │   │   ├── pdf_upload.py
      │   │   ├── pdf_extract.py
      │   │   ├── qdrant_health.py
      │   │   ├── embeddings.py
      │   │   ├── search.py
      │   │   └── chat.py
      │   └── db/
      │       ├── mongodb.py
      │       └── qdrant.py
      ├── qdrant_data/
      │   └── ...
      ├── frontend/                  <-- NEW
      │   ├── node_modules/          <-- NEW
      │   │   └── ...                <-- NEW
      │   ├── public/                <-- NEW
      │   │   └── ...                <-- NEW
      │   ├── src/                   <-- NEW
      │   │   ├── App.tsx            <-- NEW
      │   │   └── ...                <-- NEW
      │   └── ...
      ├── .env
      ├── .gitignore
      ├── requirements.txt
      └── README.md
    ```
  </details>

</details>

<details><summary> Day 12 - 29/12/25 </summary>

## Day 12 - 29/12/25

* <details><summary> Persistant Chat History </summary>

  * In order to make chat history persistant, and query the latest conversation on page load, I just needed to add a function to ``app/services/conversation_service.py`` to pull the latest conversation from MongoDB:
 
    ```py
    def get_latest_conversation():
    return db.conversations.find_one(
        {},
        sort=[("updated_at", -1)]
    )
    ```

  * I then needed to add a ``GET /chat/latest`` endpoint to the router, ``app/routers/chat.py``, that uses that function:
 
    ```py
    from app.services.conversation_service import (
      create_conversation,
      get_conversation,
      add_message,
      get_latest_conversation,
    )

    @router.get("/latest")
    def get_latest_chat():
        conversation = get_latest_conversation()
    
        if not conversation:
            return {
                "conversation_id": None,
                "messages": []
            }
    
        return {
            "conversation_id": conversation["conversation_id"],
            "messages": conversation["messages"][-10:],  # last 10 messages
        }
    ```

  * And lastly, update the frontend, ``frontend/src/App.tsx``:
 
    ```tsx
    import { useState, useEffect } from "react";

    ...

    function App() {
      ...
    
      useEffect(() => {
        const loadLatestConversation = async () => {
          try {
            const res = await fetch("http://localhost:8000/chat/latest");
            const data = await res.json();
      
            if (data.conversation_id && data.messages) {
              setConversationId(data.conversation_id);
              setMessages(data.messages);
            }
          } catch (err) {
            console.error("Failed to load latest conversation", err);
          }
        };
      
        loadLatestConversation();
      }, []);

      ...
    }

    export default App;
    ```

    adding one useEffect that runs on page load to call ``GET /chat/latest`` and hydrate ``conversationId`` and ``messages``. Put the ``useEffect(...);`` component inside ``App()``, just after the ``useState`` declarations.

  * Now when I refresh the frontend website, ``http://localhost:5173/``, I can see the latest conversation preloaded.

  </details>

* <details><summary> Pagination/Scroll </summary>

  * I still would like to add a feature that lets me switch conversations, and create a new conversation. I will try to implement that later.
 
  * Currently the chatbox just grows taller to fit the new messages, I would prefer if the chatbox was a fixed size and was scrollable vertically, or split into pages. I prefer the ability to scroll, that does mean that all the messages would need to be loaded in, but since we're only saving the last 10 messages, that shouldn't be an issue.
 
    <img width="1826" height="797" alt="chatbot" src="https://github.com/user-attachments/assets/e34e9ae4-5230-49f4-b4c2-91d79de5ec7f" />

  * To make the chatbox scrollable, I simply had to replace one line in ``frontend/src/App.tsx``:
 
    ```diff
    - <div style={{ border: "1px solid #ccc", padding: 12, minHeight: 300 }}>
    + <div style={{
    +     border: "1px solid #ccc",
    +     padding: 12,
    +     height: 350,
    +     overflowY: "auto",
    +   }}
    + >
    ```

  * The result:
 
    <img width="614" height="512" alt="image" src="https://github.com/user-attachments/assets/41287058-4583-42a2-a693-dee2030c96f7" />

  </details>

</details>

<details><summary> Day 13 - 29/12/25 </summary>

## Day 13 - 29/12/25

* <details><summary> Conversation List Sidebar </summary>

  * I was successfully able to implement a sidebar that allows the user to switch between conversations, and start a new conversation.
  * I firstly created a function, ``list_conversations()``, to return a list of the last 20 conversations in order of updated time, in JSON format with just their ``conversation_id`` and ``title``. The ``title`` of the conversation will just be the user's first input query truncated, later I could update this to be a more relevant generated title.
  * I also created a function, ``get_conversation()`` to return a ``conversation_id``-specified conversation as a ``dict`` containing its ``conversation_id``, ``title``, and ``messages``.
 
  * ``app/services/conversation_service.py``:
 
    ```py
    def list_conversations(limit: int = 20):
        return list(
            db.conversations.find(
                {},
                {
                    "_id": 0,               # don't include MongoDB _id
                    "conversation_id": 1,
                    "title": 1,
                }
            )
            .sort("updated_at", -1)
            .limit(limit)
        )

    def get_conversation(conversation_id: str) -> list[dict]:
        convo = db.conversations.find_one(
            {"conversation_id": conversation_id},
            {"_id": 0} # include everything except MongoDB _id
        )
        # return convo["messages"] if convo else []
        return convo # could be None if not found
    ```

  * I then added the routers to accompany them in ``app/routers/chat.py``:

    ```py
    from app.services.conversation_service import (
        create_conversation,
        get_conversation,
        add_message,
        get_latest_conversation,
        list_conversations,
    )

    router = APIRouter(prefix="/chat", tags=["Chat"])
    
    @router.get("/conversations")
    def get_conversations():
        convs = list_conversations()
        return [
            {
                "conversation_id": str(c["conversation_id"]),
                "title": c.get("title", "New chat"),
            }
            for c in convs
        ]
    
    @router.get("/{conversation_id}")
    def get_conversation_messages(conversation_id: str):
        convo = get_conversation(conversation_id)
    
        if not convo:
            raise HTTPException(status_code=404, detail="Conversation not found")
    
        return {
            "conversation_id": convo["conversation_id"],
            "messages": convo["messages"],
        }
    ```

  * After verifying that the ``GET /chat/conversations`` and ``GET /chat/{conversation_id}`` endpoints work, I now needed to add the sidebar feature to the frontend.

    ``frontend/src/App.tsx``:

    ```tsx
    type Conversation = {
      conversation_id: string;
      title?: string;
    };

    function App() {
      ...
      const [conversations, setConversations] = useState<Conversation[]>([]);

      ...
      useEffect(() => {
        const loadConversations = async () => {
          const res = await fetch("http://localhost:8000/chat/conversations");
          const data = await res.json();
          setConversations(data);
        };
      
        loadConversations();
      }, []);
    
      const startNewChat = () => {
        setConversationId(null);
        setMessages([]);
      };
    
      const loadConversation = async (id: string) => {
        setConversationId(id);
        setMessages([]);
        setLoading(true);
    
        const res = await fetch(`http://localhost:8000/chat/${id}`);
        const data = await res.json();
      
        setMessages(data.messages);
        setLoading(false);
      };
    ```
 
  * Modified ``return(...)`` in ``App.tsx``:
 
    ```tsx
    return (
      <div style={{ display: "flex", height: "100vh", fontFamily: "sans-serif" }}>
        
        {/* Sidebar */}
        <div
          style={{
            width: 220,
            borderRight: "1px solid #ddd",
            padding: 10,
            overflowY: "auto",
          }}
        >
          <button
            onClick={startNewChat}
            style={{ width: "100%", marginBottom: 10 }}
          >
            + New Chat
          </button>
    
          {conversations.map((c) => (
            <div
              key={c.conversation_id}
              onClick={() => loadConversation(c.conversation_id)}
              style={{
                padding: "6px 8px",
                cursor: "pointer",
                background:
                  c.conversation_id === conversationId ? "#aaa" : "transparent",
              }}
            >
              {c.title || "New Chat"}
            </div>
          ))}
        </div>
    
        {/* Chat panel */}
        <div
          style={{
            flex: 1,
            maxWidth: 700,
            margin: "40px auto",
            padding: "0 20px",
          }}
        >
          <h2>Chatbot</h2>
    
          <div
            style={{
              border: "1px solid #ccc",
              padding: 12,
  	          width: 650,
              height: 600,
              overflowY: "auto",
            }}
          >
            {messages.map((m, i) => (
              <div key={i} style={{ marginBottom: 10 }}>
                <strong>{m.role === "user" ? "You" : "AI"}:</strong>
                <div>{m.content}</div>
              </div>
            ))}
            {loading && <div>Thinking...</div>}
          </div>
    
          <div style={{ display: "flex", marginTop: 10 }}>
            <input
              style={{ flex: 1, padding: 8 }}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              disabled={loading}
            />
            <button
              onClick={sendMessage}
              style={{ marginLeft: 8 }}
              disabled={loading}
            >
              Send
            </button>
          </div>
        </div>
      </div>
    );
    ```

  * Here is the result:
 
    <img width="960" height="919" alt="image" src="https://github.com/user-attachments/assets/eae52fdf-5448-4395-b2cf-20bedb19c997" />

  * Next I would like to add a button to upload a PDF from the frontend. Could make it so the user is not allowed to upload the same PDF twice, and limit the size of the PDF. And add emotion detection with transformers sentiment models.

  </details>

</details>

<details><summary> Day 14 - 30/12/25 </summary>

## Day 14 - 30/12/25

* <details><summary> Improved Context Strategy </summary>

  * Currently, the previous messages aren't being used to influence the context chunks. E.g. when asking the question **"What causes the structure of Saturn's rings?"** and the follow-up question **"What role do resonances play?"**, the AI does not use the previous question at all to base its decision on the context chunks. Instead, it just looks for any chunks that are relevant to the question **"What role do resonances play?"**. The issue with this is that if I had a PDF on music, it could get confused with that and think any mention of musical resonances is related to my conversation on gravitational resonances in Saturn's rings.
 
  * How the current pipeline works (steps 3-5 happen inside ``chat(request: ChatRequest)``):

    * **Step 1:** User sends a message
    * **Step 2:** ``chat(request: ChatRequest)`` in ``app/routers/chat.py`` is called (``ChatRequest`` is a class containing a ``question``, ``top_k``, and ``conversation_id`` (optional)).
    * **Step 3:** Previous messages loaded
    * **Step 4:** ``search_similar_chunks(request.question, request.top_k)`` (from ``app/services/search_service.py``)
    * **Step 5:** ``generate_answer(request.question, context_chunks)`` (from ``app/services/chat_service.py``)
   
  * As you can see, the chunks searched (using OpenAI embedding model) are only given the new question, not the previous messages.
And the generated answer (using gpt-4o-mini) is only given the new question and new searched chunks.
  * One idea I was thinking of is search similar chunks with just the new question as normal, but then filter chunks which have a vector embedding not similar to the previous question's vector embedding.
  * However, a better and standard approach is to rewrite the user's query with gpt-4o-mini, giving it the last 4 messages (2 from the user, 2 from the AI), and use this rewritten query for all future tasks (finding relevant context chunks, generating the AI response).
  * It will be a good idea to store both the user's actual query and the rewritten query in MongoDB, so that the frontend displays the user's actual queries, but the backend uses the better AI-generated rewritten query.
 
  * ``app/services/chat_service.py``:
 
    ```py
    def rewrite_query(question: str, previous_messages: list[dict]) -> str:
        if not previous_messages:
            return question
    
        # keep last 4 turns (2 from user, 2 from AI)
        last_n_messages = previous_messages[-4:]
    
        messages = [
            {
                "role": "system",
                "content": (
                    "Rewrite the user's latest question into a fully self-contained "
                    "question using the prior user questions as context. "
                    "If the question is already self-contained, return it unchanged."
                )
            }
        ]
    
        for message in last_n_messages:
            messages.append({
                "role": message["role"],
                "content": message.get("rewrite", message["content"])
            })
    
        # append the new question to the message history
        messages.append({
            "role": "user",
            "content": question
        })
    
        # generate the rewritten query with the message history context
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0,      # Zero-temperature rewriting
        )
    
        return response.choices[0].message.content.strip()
    ```

    using ``.get("rewrite", message["content"])`` to prefer the rewritten query if it exists, else use the actual query.


  * ``app/services/conversation_service.py``:
 
    ```py
    def add_message(conversation_id: str, role: str, content: str, rewrite: str | None = None):
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow(),
        }
    
        if rewrite:
            message["rewrite"] = rewrite
    
        db.conversations.update_one(
            {"conversation_id": conversation_id},
            {
                "$push": {
                    "messages": {
                        "$each": [message],
                        "$slice": -MAX_MESSAGES,
                    }
                },
                "$set": {"updated_at": datetime.utcnow()},
            },
            upsert=True,
        )
    ```

  * ``app/routers/chat.py``:
 
    ```py
    def chat(request: ChatRequest):
        # 1. Create or reuse conversation
        conversation_id = request.conversation_id
        if not conversation_id:
            conversation_id = create_conversation()
    
        # 2. Load previous messages
        convo = get_conversation(conversation_id)
        previous_messages = convo["messages"]
    
        # 3. Rewrite query
        rewritten_query = rewrite_query(
            request.question,
            previous_messages
        )
    
        # 4. Vector search using rewritten query
        search_results = search_similar_chunks(
            rewritten_query,
            top_k=request.top_k,
        )
        context_chunks = [r["text"] for r in search_results]
    
        # 5. Generate answer using rewritten query
        answer = generate_answer(
            question=rewritten_query,
            context_chunks=context_chunks,
        )
    
        # 6. Store new messages
        rewrite = rewritten_query if rewritten_query != request.question else None
        add_message(conversation_id, "user", request.question, rewrite)
        add_message(conversation_id, "assistant", answer)
    
        # 7. Return response
        return {
            "conversation_id": conversation_id,
            "question": request.question,
            "rewrite": rewrite,
            "answer": answer,
            "chunks_used": len(context_chunks),
        }
    ```

  * This worked in the backend, I can now see the new field ``"rewrite"`` in the user's follow-up query, containing a correctly rewritten query with contextual awareness:
 
    ```cmd
    conversation_id "06420279-383c-4e39-a8a9-3e03ab569701"
    title: "New chat"
    messages: Array (4)
      0: Object
        role: "user"
        content: "What is the return delivery method?"
        timestamp: 2025-12-30T16:03:36.870+00:00
      1: Object
        role: "assistant"
        content: "The return delivery method is that you will arrange for the return of your documents by adding stamps onto a self-addressed envelope, which you'll include with your documents. The cost for the stamps typically ranges from £1 to £8, and it varies."
        timestamp: 2025-12-30T16:03:36.910+00:00
      2: Object
        role: "user"
        content: "Convert the price to USD"
        timestamp: 2025-12-30T16:03:58.196+00:00
        rewrite: "What is the equivalent price in USD for the return delivery method that typically costs between £1 to £8?"
      3: Object
        role: "assistant"
        content: "I do not know."
        timestamp: 2025-12-30T16:03:58.252+00:00
    created_at: 2025-12-30T16:03:32.346+00:00
    updated_at: 2025-12-30T16:03:58.252+00:00
    ```
 
    <img width="960" height="920" alt="image" src="https://github.com/user-attachments/assets/f77a10dc-94c3-479a-b47f-125d53cb3de3" />


  * However, as you can see, the AI assistant responded with **"I do not know"** when asked to perform a simple currency conversion.

  * One reason for the issue could be that it was not able to find any relevant context chunks from the embedded PDFs:
 
    ```py
    def generate_answer(question: str, context_chunks: list[str]) -> str:
        if not context_chunks:
            return "I do not know based on the provided documents."
    ```

  * However, as it did not say that exact sentence, I can rule that out. Also, the current system will return the most relevant chunks, no matter how low the actual relevancy score is. And since there are more than 5 chunks, it is guaranteed that ``context_chunks`` will be non-empty.
  * The issue was actually just that the ``SYSTEM_PROMPT`` was too strict still.
  * Currently, ``SYSTEM_PROMPT`` reads:
 
    ```py
    SYSTEM_PROMPT = (
        "You are an AI assistant answering questions based on the provided context from a document. "
        "Use the context to infer and summarize the answer when possible. "
        "If the context does not contain enough information to answer, say you do not know."
    )
    ```
  * The issue with this is that, for user queries like: **"Convert the price to USD"**, the context chunks do not contain any information relevant to this query, as it is a simple query to convert currency.
  * To fix this, I just had to update ``SYSTEM_PROMPT`` to be more lenient:
 
    ```py
    SYSTEM_PROMPT = (
        "You are an AI assistant answering questions using the provided document context. "
        "Use the context as the primary source of information. "
        "If the question requires a simple transformation, calculation, or conversion "
        "(such as currency conversion or unit conversion) based on values found in the context, "
        "you may perform that transformation using general knowledge. "
        "If the context does not provide any relevant information at all, say you do not know."
    )
    ```

  * Which resulted in:
 
    <img width="959" height="917" alt="image" src="https://github.com/user-attachments/assets/5d367f18-4bfe-457d-9e22-adcaca7429ed" />

  * This is a better response than simply **"I do not know."**, although I would prefer if it was slightly more concise.
  * One future improvement would be for the system to detect if the rewritten query contains words like "convert", "conversion", "equivalent", "how much is", "calculate", "total", etc., and to generate a response without using any context chunks. This would potentially save on token-usage as it means we don't have to pass entire context chunks, however, it might accidentally mistake retrieval queries for general queries. So for now I will opt not to make that change.
 
  * By using rewritten queries and storing them in MongoDB, we are now able to succinctly preserve context without needing to pass the last 4 messages.

  * So now when the system receives a new user query, it:
    * rewrites the query based on the last 4 messages (2 user queries (will opt for the rewritten query if it exists) and 2 AI responses) and the user's actual query
    * uses the contextually-aware rewritten query to find context chunks
    * uses the contextually-aware rewritten query along with the context chunks to generate a response
    * stores the new user query (actual), rewritten query, and AI response in MongoDB

  * One other thing I do is store the context chunk ID's in MongoDB. This might be better than needing to search for context chunks for every new query, especially when the context remains the same. However, the user could easily change the subject, meaning that the context chunks would need to change. So for now I will stick to re-searching for context chunks with each new query.
  * What I could add is a way for the chatbot to reference/cite the PDF they are sourcing their info from.

  </details>

</details>

<details><summary> Day 15 - 31/12/25 </summary>

## Day 15 - 31/12/25

* <details><summary> File size limit </summary>

  * Added a file size limiter. At first I tried to implement it by adding a check in ``file_storage.py``, but this did not work.
  * The solution was to add a ``middleware``:
 
    ``app/middleware/file_too_large.py``:

    ```py
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request
    from starlette.responses import JSONResponse
    from starlette import status
    
    MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20MB
    
    class LimitUploadSizeMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            content_length = request.headers.get("content-length")
    
            if content_length and int(content_length) > MAX_UPLOAD_SIZE:
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={"error": "20MB file upload limit exceeded"},
                )
    
            return await call_next(request)
    ```

    and register it in ``main.py``:

    ```py
    from app.middleware.file_size_limit import LimitUploadSizeMiddleware

    app.add_middleware(LimitUploadSizeMiddleware)
    ```

  * The result when trying to upload a 70MB PDF:
 
    <img width="918" height="917" alt="image" src="https://github.com/user-attachments/assets/7690f2c4-bcf8-4630-9a37-da6453315963" />


  </details>

* <details><summary> Prevent duplicate PDFs </summary>

  * In order to prevent the same PDF being uploaded again, I used ``hashlib`` to generate a unique hash for the contents of the PDF, checking if the hash matches with any of the hashes of the PDFs in the MongoDB documents collection, and if not, saving the PDF with its hash in the JSON.

   * ``app/services/file_storage.py``:
     
      ```py
      import hashlib
      from app.core.errors import unsupported_file, bad_request, duplicate_file
      from app.db.mongodb import db
      
      def save_pdf(file: UploadFile) -> dict:
          # Validate PDF
          validate_pdf(file)
      
          # Generate unique filename
          file_id = str(uuid.uuid4())
          filename = f"{file_id}.pdf"
          filepath = os.path.join(BASE_DIR, filename)
      
          #  Read file bytes
          file_bytes = file.file.read()
      
          # Save file data
          with open(filepath, "wb") as out_file:
              out_file.write(file_bytes)
      
          # Reset pointer so file can be re-read if needed later
          file.file.seek(0)
      
          # Duplicate pdf
          file_hash = compute_file_hash(file)
          existing = db.documents.find_one({"file_hash": file_hash})
          if existing:
              raise duplicate_file("This PDF has already been uploaded.")
      
          # Return metadata
          return {
              "file_id": file_id,
              "filename": file.filename,
              "file_hash": file_hash,
              "stored_filename": filename,
              "path": filepath,
              "size_bytes": os.path.getsize(filepath),
              "content_type": file.content_type,
          }
      ```

  * ``app/core/errors.py``:
 
    ```py
    def duplicate_file(message: str):
        return HTTPException(
                status_code=409,
                detail={"error": message}
        )
    ```

  * ``app/services/document_repository.py``:

    ```py
    def create_document(metadata: dict) -> dict:
        document = {
            "file_id": metadata["file_id"],
            "original_filename": metadata["filename"],
    	"file_hash": metadata["file_hash"],
            # "stored_filename": metadata["stored_filename"],
            "size_bytes": metadata["size_bytes"],
            "content_type": metadata["content_type"],
            "status": "UPLOADED",
            "created_at": datetime.utcnow(),
        }
    
        documents_collection.insert_one(document)
        return document
    ```

  * Now when I try to upload a duplicate PDF it returns:
 
    <img width="893" height="917" alt="image" src="https://github.com/user-attachments/assets/4df60ae2-a0c3-4948-80b8-f907b6b1e0a4" />

  * And in MongoDB, I can see the PDF is stored with its unique hash:
 
    <img width="651" height="175" alt="image" src="https://github.com/user-attachments/assets/1789d287-037c-401a-9677-5ecea86c8704" />


  </details>
  
* <details><summary> New folder structure </summary>
  
    ```
    AI-Support-Agent/
      ├── app/
      │   ├── main.py
      │   ├── config.py
      │   ├── middleware/
      │   │   ├── logging.py
      │   │   └── file_size_limit.py         <-- NEW
      │   ├── services/
      │   │   ├── file_storage.py
      │   │   ├── pdf_service.py
      │   │   ├── document_repository.py
      │   │   ├── embedding_service.py
      │   │   ├── search_service.py
      │   │   ├── chat_service.py
      │   │   └── conversation_service.py
      │   ├── storage/
      │   │   └── pdfs/
      │   ├── core/
      │   │   ├── errors.py
      │   │   └── embeddings.py
      │   ├── routers/
      │   │   ├── health.py
      │   │   ├── pdf_upload.py
      │   │   ├── pdf_extract.py
      │   │   ├── qdrant_health.py
      │   │   ├── embeddings.py
      │   │   ├── search.py
      │   │   └── chat.py
      │   └── db/
      │       ├── mongodb.py
      │       └── qdrant.py
      ├── qdrant_data/
      │   └── ...
      ├── frontend/
      │   ├── node_modules/
      │   │   └── ...
      │   ├── public/
      │   │   └── ...
      │   ├── src/
      │   │   ├── App.tsx
      │   │   └── ...
      │   └── ...
      ├── .env
      ├── .gitignore
      ├── requirements.txt
      └── README.md
    ```
  </details>

</details>

<details><summary> Day 16 - 01/01/26 </summary>

## Day 16 - 01/01/26

* <details><summary> PDF upload and list sidebar </summary>

  * In order to add the list of uploaded PDFs to the sidebar, I first made a function in ``app/services/document_repository.py`` to list all the PDFs, and a function to delete a PDF:
 
    ```py
    def list_all_pdfs():
        return list(documents_collection.find(
            {}, 
            {
                "_id": 0,
                "extracted_text": 0,
                "stored_filename": 0,
                "content_type": 0
            }
        ))

    def delete_pdf_by_file_id(file_id: str):
        pdf = documents_collection.find_one({"file_id": file_id})
    
        if not pdf:
            raise HTTPException(404, "PDF not found")
    
        # 1. Delete file from disk
        # 2. Delete chunks from Qdrant
        # 3. Delete DB record
    
        documents_collection.delete_one({"file_id": file_id})
    
        return {"ok": True}
    ```

  * Made a new router, ``app/routers/pdf_list.py`` that uses ``list_all_pdfs()``:
 
    ```py
    from fastapi import APIRouter
    from app.services.document_repository import list_all_pdfs
    
    router = APIRouter(prefix="/pdf", tags=["PDF List"])
    
    @router.get("/list")
    async def list_pdfs():
        return list_all_pdfs()
    ```

  * And a new router, ``app/routers/pdf_delete.py``, that uses ``delete_pdf_by_file_id(file_id: str)``:
 
    ```py
    from fastapi import APIRouter
    from app.services.document_repository import delete_pdf_by_file_id
    
    router = APIRouter(prefix="/pdf", tags=["PDF Delete"])
    
    @router.delete("/{file_id}")
    async def delete_pdf(file_id: str):
        return delete_pdf_by_file_id(file_id)
    ```

  * And finally registering the routers in ``main.py``:
 
    ```py
    from app.routers.pdf_list import router as pdf_list_router
    from app.routers.pdf_delete import router as pdf_delete_router

    app.include_router(pdf_list_router)
    app.include_router(pdf_delete_router)
    ```

  * To display the list of PDFs in the frontend sidebar, I added this to ``frontend/src/App.tsx``:
 
    ```tsx
    import { useState, useEffect, useRef } from "react";

    type Pdf = {
      file_id: string;
      original_filename: string;
      status: "processing" | "ready" | "failed";
    };

    function App() {
      const [pdfs, setPdfs] = useState<Pdf[]>([]);
      const fileInputRef = useRef<HTMLInputElement | null>(null);

      useEffect(() => {
        fetch("http://localhost:8000/pdf/list")
          .then(res => res.json())
          .then(setPdfs);
      }, []);

      const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;
      
        const formData = new FormData();
        formData.append("file", file);
      
        setUploading(true);
      
        const res = await fetch("http://localhost:8000/pdf/upload", {
          method: "POST",
          body: formData,
        });
      
        if (res.ok) {
          const pdf = await res.json();
          setPdfs(prev => [...prev, pdf]);
        } else {
          const err = await res.json();
          alert(err?.detail?.error ?? "Upload failed");
        }
      
        setUploading(false);
      };
    
      const deletePdf = async (fileId: string) => {
        if (!confirm("Delete this PDF?")) return;
      
        await fetch(`http://localhost:8000/pdf/${fileId}`, {
      method: "DELETE",
        });
      
        setPdfs(prev => prev.filter(p => p.file_id !== fileId));
      };

      return (
        <div style={{ display: "flex", height: "100vh", fontFamily: "sans-serif" }}>
          
          {/* Sidebar */}
          <div
            style={{
              width: 220,
              borderRight: "1px solid #ddd",
              padding: 10,
              overflowY: "auto",
            }}
          >
            {/* Conversations */}
            <button
              onClick={startNewChat}
              style={{ width: "100%", marginBottom: 10 }}
            >
              + New Chat
            </button>
      
            {conversations.map((c) => (
              <div
                key={c.conversation_id}
                onClick={() => loadConversation(c.conversation_id)}
                style={{
                  padding: "6px 8px",
                  cursor: "pointer",
                  background:
                    c.conversation_id === conversationId ? "#aaa" : "transparent",
                }}
              >
                {c.title || "New Chat"}
              </div>
            ))}
    
            {/* Documents */}
          	<input
          	  type="file"
          	  accept="application/pdf"
          	  hidden
          	  ref={fileInputRef}
          	  onChange={handleUpload}
          	/>
          	
          	<button 
          	  onClick={() => fileInputRef.current?.click()}
                    style={{ width: "100%", marginBottom: 10 }}
          	>
          	  + Upload PDF
          	</button>
                 	
          	{pdfs.map(pdf => (
          	  <div 
          	      key={pdf.file_id}
          	      style={{
          		display: "flex",
          		alignItems: "flex-start",
          		gap: 6,
          		marginBottom: 6,
          	      }}
          	  >
          	    
          	    {/* Emoji column */}
          	    <span style={{ flexShrink: 0 }}>📄</span>
          
          	    {/* Filename column */}
          	    <span
          		style={{
          		    wordBreak: "break-word",
          		    overflowWrap: "anywhere",
          		    whiteSpace: "normal",
          		    flex: 1,
          		    lineHeight: "1.3",
          		}}
          	    >
          	      {pdf.original_filename}
          	      {pdf.status === "processing" && " (processing)"}
          	    </span>
          
          	    {/* Delete button */}
          	    <button
          	      onClick={() => deletePdf(pdf.file_id)}
          	      style={{
          		color: "red",
          		background: "transparent",
          		fontSize: 12,
          		padding: "2px 4px",
          		lineHeight: 1,
          		marginLeft: "auto" }}
          	    >
          	      ✕
          	    </button>
          	  </div>
          	))}
          </div>
    ```

  * The result:
 
    <img width="957" height="914" alt="image" src="https://github.com/user-attachments/assets/629ab90f-c412-424f-9f8c-8e02e0627486" />


  * Some frontend design issues that I fixed were:
    * The PDF filename not wrapping onto the next line
    * The delete button being too big
    * Newly uploaded PDF's filename not displaying:
      * Fixed by ensuring the variable name was the exact same (``"original_filename"``) in ``app/services/pdf_upload.py``, ``app/services/document_repository.py``, and ``frontend/src/App.tsx``.

  * There is still an issue where if I upload a PDF and try to upload it again, instead of giving me the expected error, it just does nothing (neither uploads the PDF again nor prints an error). The issue goes away when I refresh the page first before trying to upload the same PDF again, this time displaying the error message as expected. But ideally, I want it to print the error without needing to refresh the page.
  * Also when deleting a PDF, it won't upload the same PDF again unless I refresh the page.
  * The fix for the two issues above was to ALWAYS reset the file input after upload:

    ```diff
      const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;
      
        const formData = new FormData();
        formData.append("file", file);
      
        setUploading(true);
      
        const res = await fetch("http://localhost:8000/pdf/upload", {
          method: "POST",
          body: formData,
        });
      
        if (res.ok) {
          const pdf = await res.json();
          setPdfs(prev => [...prev, pdf]);
        } else {
          const err = await res.json();
          alert(err?.detail?.error ?? "Upload failed");
        }
    
    +   if (fileInputRef.current) {
    +   	fileInputRef.current.value = "";
    +   }
      
        setUploading(false);
      };
    ```

  * Now I can upload and delete the same file, and upload it again, without needing to refresh. And I get the error message when trying to upload a PDF that's already on the list, as expected.
  * One future improvement would be to add a button to delete conversations, similar to the button to delete PDFs.
  * Also need to add a button to extract from the PDF once it's been uploaded.
  * I'm considering also adding a way to have multiple instances for different users, each having their own conversations and documents.
  * The chunks are stored in ``qdrant_data/`` which is local to the machine, this means if the same user uses another machine, their uploaded files will be the same (pulled from MongoDB) but the extracted files and chunks won't be the same.
  * When deleting a PDF, I am currently just deleting it from MongoDB. If the PDF had been chunked and extracted (i.e. added to ``qdrant_data/``), the chunks would also need to be deleted.

        

  </details>
  
* <details><summary> New folder structure </summary>

    ```diff
      AI-Support-Agent/
        ├── app/
        │   ├── main.py
        │   ├── config.py
        │   ├── middleware/
        │   │   ├── logging.py
        │   │   └── file_size_limit.py
        │   ├── services/
        │   │   ├── file_storage.py
        │   │   ├── pdf_service.py
        │   │   ├── document_repository.py
        │   │   ├── embedding_service.py
        │   │   ├── search_service.py
        │   │   ├── chat_service.py
        │   │   └── conversation_service.py
        │   ├── storage/
        │   │   └── pdfs/
        │   ├── core/
        │   │   ├── errors.py
        │   │   └── embeddings.py
        │   ├── routers/
        │   │   ├── health.py
        │   │   ├── pdf_upload.py
        │   │   ├── pdf_extract.py
    +   │   │   ├── pdf_delete.py              <-- NEW
    +   │   │   ├── pdf_list.py                <-- NEW
        │   │   ├── qdrant_health.py
        │   │   ├── embeddings.py
        │   │   ├── search.py
        │   │   └── chat.py
        │   └── db/
        │       ├── mongodb.py
        │       └── qdrant.py
        ├── qdrant_data/
        │   └── ...
        ├── frontend/
        │   ├── node_modules/
        │   │   └── ...
        │   ├── public/
        │   │   └── ...
        │   ├── src/
        │   │   ├── App.tsx
        │   │   └── ...
        │   └── ...
        ├── .env
        ├── .gitignore
        ├── requirements.txt
        └── README.md
    ```
  </details>

</details>

<details><summary> Day 17 - 02/01/25 </summary>

## Day 17 - 02/01/25

* <details><summary> Moved all pdf routers to single file </summary>

  * Combined all the pdf routers (``pdf_delete.py``, ``pdf_extract.py``, ``pdf_list.py``, ``pdf_upload.py``) to a single file, ``app/routers/pdf.py``:
 
    ```py
    from fastapi import APIRouter, UploadFile, File, HTTPException
    from app.services.file_storage import save_pdf, get_pdf_path
    from app.services.pdf_service import extract_text_from_pdf, PDFExtractionError
    from app.services.document_repository import (
        create_document,
        store_extracted_text,
        get_document_by_file_id,
        delete_pdf_by_file_id,
        list_all_pdfs,
    )
    
    
    router = APIRouter(prefix="/pdf", tags=["PDF"])
    
    
    @router.post("/upload")
    async def upload_pdf(file: UploadFile = File(...)):
        metadata = save_pdf(file)
        document = create_document(metadata)
    
        return {
            # "message": "PDF uploaded successfully",
            # "metadata": metadata,
            "file_id": document["file_id"],
            "original_filename": document["original_filename"],
            "status": document["status"]
        }
    
    
    @router.post("/{file_id}/extract")
    def extract_pdf_text(file_id: str):
        document = get_document_by_file_id(file_id)
    
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
    
        if document.get("status") == "EXTRACTED":
            return {
                "message": "Text already extracted",
                "file_id": file_id,
            }
    
        try:
            pdf_path = Path(get_pdf_path(file_id))
            text = extract_text_from_pdf(pdf_path)
    
            store_extracted_text(file_id, text)  # MongoDB
    
            return {
                "file_id": file_id,
                "text_length": len(text),
                "text_preview": text[:1000],  # prevent massive response
            }
    
        except PDFExtractionError as e:
            raise HTTPException(status_code=422, detail=str(e))
    
    
    @router.get("/list")
    async def list_pdfs():
        return list_all_pdfs()
    
    
    @router.delete("/{file_id}")
    async def delete_pdf(file_id: str):
        return delete_pdf_by_file_id(file_id)
    ```

  </details>

* <details><summary> Sidebar menu to rename and delete conversations </summary>

  * Added functions to rename and delete conversations in ``app/services/conversation_service.py``:
 
    ```py
    def rename_conversation_by_id(conversation_id: str, new_title: str):
        result = db.conversations.update_one(
            {"conversation_id": conversation_id},
            {"$set": {
                "title": new_title,
                "updated_at": datetime.utcnow()
                }
            }
        )
        return result
    
    
    def delete_conversation_by_id(conversation_id: str):
        result = db.conversations.delete_one({"conversation_id": conversation_id})
        return result
    ```

  * Made two routers to handle renaming and deleting conversations using the functions above in ``app/routers/chat.py``:
 
    ```py
    @router.patch("/{conversation_id}/rename")
    async def rename_conversation(conversation_id: str, new_title: str):
        result = rename_conversation_by_id(conversation_id, new_title)
    
        if result.matched_count == 0:
            raise file_not_found("Conversation not found")
        
        return {"conversation_id": conversation_id, "title": new_title}
    
    
    @router.delete("/{conversation_id}")
    async def delete_conversation(conversation_id: str):
        result = delete_conversation_by_id(conversation_id)
    
        if result.deleted_count == 0:
            raise file_not_found("Conversation not found")
    
        return {"deleted": True}
    ```

  * And finally updated the frontend, ``frontend/src/App.tsx``, to add the menu icon for each of the conversations, the dropdown menu containing the buttons to "Rename" and "Delete", and connecting them to the backend:
 
    ```tsx
    function App() {
      const [menuOpenId, setMenuOpenId] = useState<string | null>(null);

      const openMenu = (e: React.MouseEvent, convo: Conversation) => {
        e.stopPropagation();
        setMenuOpenId(convo.conversation_id === menuOpenId ? null : convo.conversation_id);
      };

      const handleRename = async (convo: Conversation) => {
        const newTitle = prompt("Enter new conversation title:", convo.title || "");
        if (!newTitle) return;
      
        const res = await fetch(`http://localhost:8000/chat/${convo.conversation_id}/rename?new_title=${encodeURIComponent(newTitle)}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
        });
      
        if (res.ok) {
          setConversations((prev) =>
            prev.map((c) =>
              c.conversation_id === convo.conversation_id ? { ...c, title: newTitle } : c
            )
          );
        } else {
          alert("Failed to rename conversation");
        }
      
        setMenuOpenId(null);
      };
      
      const handleDelete = async (convo: Conversation) => {
        if (!confirm("Are you sure you want to delete this conversation?")) return;
      
        const res = await fetch(`http://localhost:8000/chat/${convo.conversation_id}`, {
          method: "DELETE",
        });
      
        if (res.ok) {
          setConversations((prev) =>
            prev.filter((c) => c.conversation_id !== convo.conversation_id)
          );
      
          // Clear chat panel if this conversation was open
          if (convo.conversation_id === conversationId) {
            setConversationId(null);
            setMessages([]);
          }
        } else {
          alert("Failed to delete conversation");
        }
      
        setMenuOpenId(null);
      };
    ```

    ```diff
    	{/* Conversations list */}
    	{conversations.map((c) => (
    	  <div
    	    key={c.conversation_id}
                onClick={() => loadConversation(c.conversation_id)}
    	    style={{
    	      display: "flex",
    +	      alignItems: "center",
    +	      justifyContent: "space-between",
    	      padding: "6px 8px",
    	      cursor: "pointer",
    	      background: c.conversation_id === conversationId ? "#aaa" : "transparent",
    +	      position: "relative",
    	    }}
    	  >
    	    {c.title || "New Chat"}
    	
    +	    {/* 3-dot menu */}
    +	    <span style={{ cursor: "pointer" }}
    +		onClick={(e) => {
    +		    e.stopPropagation();
    +		    openMenu(e, c);
    +		}}
    +	    >
    +	      ⋯
    +	    </span>
    	    
    +	    {menuOpenId === c.conversation_id && (
    +	      <div
    +	        style={{
    +	          position: "absolute",
    +	          background: "#444",
    +	          border: "1px solid #ccc",
    +		  padding: 4,
    +	          top: "100%",
    +		  right: 0,
    +	          zIndex: 100,
    +		  minWidth: 80,
    +	        }}
    +	      >
    +	        <div
    +	          style={{ padding: "4px 8px", cursor: "pointer" }}
    +	          onClick={(e) => {
    +		      e.stopPropagation();
    +		      handleRename(c);
    +		  }}
    +	        >
    +	          Rename
    +	        </div>
    +	        <div
    +	          style={{ padding: "4px 8px", cursor: "pointer", color: "red" }}
    +	          onClick={(e) => {
    +		      e.stopPropagation();
    +		      handleDelete(c);
    +		  }}
    +	        >
    +	          Delete
    +	        </div>
    +	      </div>
    +	    )}
    +	  </div>
    +	))}
    ```

  * Added a click listener to ``App.tsx`` so that the dropdown menu automatically closes when the user clicks elsewhere:
 
    ```tsx
    useEffect(() => {
      const handleClickOutside = () => setMenuOpenId(null);
      document.addEventListener("click", handleClickOutside);
      return () => document.removeEventListener("click", handleClickOutside);
    }, []);
    ```

  * Added this single line to ``loadConversation`` in ``App.tsx`` to prevent the website reloading the current conversation if the user clicks on the current conversation in the sidebar. This prevents a wasteful reload:
 
    ```diff
      const loadConversation = async (id: string) => {
    +   if (id == conversationId) return; // prevent wasteful reload
    
        setConversationId(id);
        setMessages([]);
    
        const res = await fetch(`http://localhost:8000/chat/${id}`);
        const data = await res.json();
      
        setMessages(data.messages);
      };
    ```
    
  * The result:
    * Sidebar with menu buttons next to the conversations:

      <img width="960" height="914" alt="image" src="https://github.com/user-attachments/assets/f181966e-3705-4b8d-95d1-00d686b0f1af" />

    * Clicking on the menu button:

      <img width="427" height="353" alt="image" src="https://github.com/user-attachments/assets/7874f944-3bec-4644-ac0f-54c525bbd842" />

    * Clicking "Rename":

      <img width="958" height="954" alt="image" src="https://github.com/user-attachments/assets/187e9742-cf42-4d25-8357-6d3eb382e538" />

      * Pressing "OK":
     
        <img width="360" height="278" alt="image" src="https://github.com/user-attachments/assets/bc3fd856-c87b-4eec-ba75-a5e097434d26" />

    * Clicking "Delete":
   
      <img width="958" height="957" alt="image" src="https://github.com/user-attachments/assets/683c4ebe-788b-4401-a913-137d097a382f" />

      * Pressing "OK":

        <img width="959" height="915" alt="image" src="https://github.com/user-attachments/assets/afd50e31-2caf-4e7c-9931-2ea74019c63d" />

  </details>

* <details><summary> Future additions </summary>

  * Need to add a button to extract from PDFs after uploading.
  * Possibly add functionality for multiple users, each having their own collection of conversations and documents, and a menu to login?
  * Possibly store ``qdrant_data/`` in MongoDB for persistance across multiple devices?
  * Handle deletion of chunks from Qdrant when an extracted PDF is deleted.
  * Sentiment analysis, key entities extraction, knowledge graph relationships, PDF report generation.

  </details>

* <details><summary> New folder structure </summary>

    ```diff
      AI-Support-Agent/
        ├── app/
        │   ├── main.py
        │   ├── config.py
        │   ├── middleware/
        │   │   ├── logging.py
        │   │   └── file_size_limit.py
        │   ├── services/
        │   │   ├── file_storage.py
        │   │   ├── pdf_service.py
        │   │   ├── document_repository.py
        │   │   ├── embedding_service.py
        │   │   ├── search_service.py
        │   │   ├── chat_service.py
        │   │   └── conversation_service.py
        │   ├── storage/
        │   │   └── pdfs/
        │   ├── core/
        │   │   ├── errors.py
        │   │   └── embeddings.py
        │   ├── routers/
        │   │   ├── health.py
    -   │   │   ├── pdf_upload.py
    -   │   │   ├── pdf_extract.py
    -   │   │   ├── pdf_delete.py
    -   │   │   ├── pdf_list.py
    +   │   │   ├── pdf.py		                 <-- NEW
        │   │   ├── qdrant_health.py
        │   │   ├── embeddings.py
        │   │   ├── search.py
        │   │   └── chat.py
        │   └── db/
        │       ├── mongodb.py
        │       └── qdrant.py
        ├── qdrant_data/
        │   └── ...
        ├── frontend/
        │   ├── node_modules/
        │   │   └── ...
        │   ├── public/
        │   │   └── ...
        │   ├── src/
        │   │   ├── App.tsx
        │   │   └── ...
        │   └── ...
        ├── .env
        ├── .gitignore
        ├── requirements.txt
        └── README.md
    ```
  </details>

</details>

<details><summary> Day 18 - 03/01/25 </summary>

## Day 18 - 03/01/25

* <details><summary> Fixed frontend error message for file too large </summary>

  * As mentioned earlier when implementing error handling for files that are too big, I needed to make it a ``Middleware``:
 
    ```py
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request
    from starlette.responses import JSONResponse
    from starlette import status
    
    MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20MB
    
    class LimitUploadSizeMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            content_length = request.headers.get("content-length")
    
            if content_length and int(content_length) > MAX_UPLOAD_SIZE:
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={"error": "20MB file upload limit exceeded"},
                )
    
            return await call_next(request)
    ```

    rather than like the typical error handlers in ``app/core/errors.py``:

    ```py
    from fastapi import HTTPException, status
    
    def bad_request(message: str):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": message}
        )
    ```

  * This worked fine in the backend, I had to make a small fix to make it identical:
 
    ```diff
    - content={"error": "20MB file upload limit exceeded"},
    + content={"detail": {"error": "20MB file upload limit exceeded"}},
    ```

  * But other than that I expected it to work the same on the frontend, a pop-up with the error message on the screen. However when I uploaded a PDF >20MB no pop-up displayed.
  * This was the first time where ChatGPT did not help, but Claude Sonnet 4.5 did help. I already made sure the size limit middleware was added **after** CORS middleware. 
 
    ```
    # -----------
    # CORS CONFIG
    # -----------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    
    # -------
    # LOGGING
    # -------
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(LimitUploadSizeMiddleware)
    ```

  * The fix was to simply add the CORS headers manually:
 
    ```py
    response = JSONResponse(
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        content={"detail": {"error": "20MB file upload limit exceeded"}},
    )
    # Add CORS headers manually
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response
    ```

  * As described by Sonnet: _"The issue is that your middleware is returning a JSONResponse without the necessary CORS headers. When FastAPI normally handles requests, it adds CORS headers through your CORS middleware, but your custom middleware is short-circuiting the request before those headers get added."_
 
  * The result:
 
    <img width="960" height="957" alt="image" src="https://github.com/user-attachments/assets/0c9af1e9-ff97-449f-ac75-ee686deffa08" />

  </details>
  
* <details><summary> Added backend extraction and embedding to frontend upload process </summary>

  * I firstly moved the embedding router into ``app/routers/pdf.py``, to centralize processes related to PDFs:
 
    ```py
    @router.post("/embed/{file_id}")
    def generate_embeddings(file_id: str):
        text = get_document_text(file_id)
        if not text:
            raise HTTPException(status_code=404, detail="No extracted text found")
    
        count = embed_and_store(file_id, text)
        
        update_embed_status(file_id, count)
    
        return {
            "file_id": file_id,
            "chunks_embedded": count
        }
    ```
 
  * Added a function to ``app/services/document_repository.py`` to update the ``status`` to ``EMBEDDED`` and store the number of ``chunks_embedded`` and ``extracted_at`` date:
 
    ```py
    def update_embed_status(file_id: str, count: int):
        result = documents_collection.update_one(
            {"file_id": file_id},
            {
                "$set": {
                    "status": "EMBEDDED",
                    "chunks_embedded": count,
                    "extracted_at": datetime.utcnow(),
                }
            }
        )
    
        if result.matched_count == 0:
            raise ValueError("Document not found")
    ```

  * And lastly updated the frontend, ``frontend/src/App.tsx``:
 
    ```diff
      type Pdf = {
        file_id: string;
        original_filename: string;
    -   status: "processing" | "UPLOADED" | "EXTRACTED" | "failed";
    +   status: "processing" | "extracting" | "embedding" |"UPLOADED" | "EXTRACTED" | "EMBEDDED" | "failed";
      };
    ```

    ```diff
      const uploadPdf = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
        if (!file) return;
      
        const formData = new FormData();
        formData.append("file", file);
      
        setUploading(true);
      
        const res = await fetch("http://localhost:8000/pdf/upload", {
          method: "POST",
          body: formData,
        });
    
        if (!res.ok) {
    	const err = await res.json();
    	alert(err?.detail?.error ?? "Upload failed");
    	setUploading(false);
    	return;
        }
    
        const pdf = await res.json();
    
        // Add PDF immediately
        setPdfs(prev => [...prev, pdf]);
    
        // Reset input so same file can be re-uploaded if deleted
        if (fileInputRef.current) {
        	fileInputRef.current.value = "";
        }
      
        setUploading(false);
    
    +   // trigger extraction
    +   extractPdf(pdf.file_id);
      };
    ```

    ```tsx
    const extractPdf = async (fileId: string) => {
      // Optimistically mark as extracting
      setPdfs(prev =>
        prev.map(p =>
          p.file_id === fileId ? { ...p, status: "extracting" } : p
        )
      );
    
      const res = await fetch(
        `http://localhost:8000/pdf/extract/${fileId}`,
        { method: "POST" }
      );
    
      if (!res.ok) {
        setPdfs(prev =>
          prev.map(p =>
            p.file_id === fileId ? { ...p, status: "failed" } : p
          )
        );
        return;
      }
    
      setPdfs(prev =>
        prev.map(p =>
          p.file_id === fileId ? { ...p, status: "EXTRACTED" } : p
        )
      );
  
      // trigger embedding
      embedPdf(fileId);
    };
  
  
    const embedPdf = async (fileId: string) => {
      // Optimistically mark as embedding
      setPdfs(prev =>
        prev.map(p =>
          p.file_id === fileId ? { ...p, status: "embedding" } : p
        )
      );
    
      const res = await fetch(
        `http://localhost:8000/pdf/embed/${fileId}`,
        { method: "POST" }
      );
    
      if (!res.ok) {
        setPdfs(prev =>
          prev.map(p =>
            p.file_id === fileId ? { ...p, status: "failed" } : p
          )
        );
        return;
      }
    
      setPdfs(prev =>
        prev.map(p =>
          p.file_id === fileId ? { ...p, status: "EMBEDDED" } : p
        )
      );
    };
    ```

    ```diff
	    {/* Filename column */}
	    <span style={{
	      wordBreak: "break-word",
	      overflowWrap: "anywhere",
	      whiteSpace: "normal",
	      flex: 1,
	      lineHeight: "1.3",
	    }}>
          {pdf.original_filename}
    -     {pdf.status === "processing" && " (processing)"}
    +     {pdf.status === "extracting" && " (extracting...)"}
    +     {pdf.status === "embedding" && " (embedding...)"}
    +     {pdf.status === "failed" && " (FAILED ❌)"}
	    </span>
    ```

  * The result:
 
    * After uploading a PDF, it displays the ``(extracting...)`` phase on the frontend:
   
      <img width="237" height="59" alt="image" src="https://github.com/user-attachments/assets/7eeb2f80-ced1-4a52-be42-05f7a0e7617b" />

    * After the ``(extracting...)`` phase, it displays the ``(embedding...)`` phase:
   
      <img width="239" height="58" alt="image" src="https://github.com/user-attachments/assets/dc6d6ef3-3bf2-4d36-a84d-b77002bc7a0b" />

    * And if no errors occurred throughout, it displays the file in the sidebar as normal:
   
      <img width="238" height="42" alt="image" src="https://github.com/user-attachments/assets/296d559a-2f01-4227-b0fb-88f0c42cff0d" />

    * In the backend:
   
      <img width="578" height="216" alt="image" src="https://github.com/user-attachments/assets/8da21cb9-c180-40b1-b4cb-f5ccee4e0835" />

  * And now when asking a question related to the PDF, the AI is able to give a correct response, showing that it has successfully uploaded, extracted, and embedded the PDF:
 
    <img width="1042" height="914" alt="image" src="https://github.com/user-attachments/assets/07603eb3-2495-4174-8a30-f745478541bc" />

  * Lastly, I notice that the system is decent at detecting when it is necessary to rewrite the user's query, although the rewrite seems to not be formed as a question but rather an answer to the user's query, which is not what we want:
 
    <img width="593" height="494" alt="image" src="https://github.com/user-attachments/assets/3637ac4d-6370-4f21-8be6-1de200010780" />

    ```
    "content": "Can you summarise and explain the first part?"
    "rewrite":
      "The first part of question 1 on problem sheet 2 involves using the Maxwell distribution function to derive important statistical properties of gas particles in thermal equilibrium. Here's a summary and explanation of the key components:

      1. **Maxwell Distribution Function**: This function describes the distribution of speeds of particles in an ideal gas at a given temperature \(T\). It is a fundamental result in statistical mechanics and is given by:
         \[
         f(v) = \left( \frac{m}{2\pi kT} \right)^{3/2} e^{-\frac{mv^2}{2kT}}
         \]
         where \(m\) is the mass of the particles, \(k\) is the Boltzmann constant, and \(T\) is the absolute temperature.
      
      2. **Average Speed \(\langle |v| \rangle\)**: The first part asks to show that the average speed of a particle in the gas can be calculated as:
         \[
         \langle |v| \rangle = \sqrt{\frac{8kT}{\pi m}}
         \]
         This result indicates that the average speed depends on the temperature and the mass of the particles. Higher temperatures lead to higher average speeds.
      
      3. **Mean Square Speed \(\langle v^2 \rangle\)**: The second part requires showing that the mean square speed of the particles is given by:
         \[
         \langle v^2 \rangle = \frac{3kT}{m}
         \]
         This result is significant because it relates the average kinetic energy of the particles to the temperature of the gas. Specifically, it shows that the average kinetic energy per degree of freedom is \(\frac{1}{2}kT\), consistent with the equipartition theorem.
      
      In summary, the first part of the question establishes fundamental relationships between the speed of gas particles, their mass, and the temperature of the gas, which are crucial for understanding the behavior of gases in statistical mechanics."
    ```

  * This is the ``rewrite_query()`` function in ``app/services/chat_service.py``, I thought it would work fine and the prompt is reasonable, but I guess I might need to adjust it:
 
    ```py
    def rewrite_query(question: str, previous_messages: list[dict]) -> str:
        if not previous_messages:
            return question
    
        # keep last 4 turns (2 from user, 2 from AI)
        last_n_messages = previous_messages[-4:]
    
        messages = [
            {
                "role": "system",
                "content": (
                    "Rewrite the user's latest question into a fully self-contained "
                    "question using the prior messages as context. "
                    "If the question is already self-contained, return it unchanged."
                )
            }
        ]
    
        for message in last_n_messages:
            messages.append({
                "role": message["role"],
                "content": message.get("rewrite", message["content"])
            })
    
        # append the new question to the message history
        messages.append({
            "role": "user",
            "content": question
        })
    
        # generate the rewritten query with the message history context
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0,      # Zero-temperature rewriting
        )
    
        return response.choices[0].message.content.strip()
    ```
    
  </details>

* <details><summary> Future additions </summary>

  * Possibly add functionality for multiple users, each having their own collection of conversations and documents, and a menu to login?
  * Possibly store ``qdrant_data/`` in MongoDB for persistance across multiple devices?
  * Handle deletion of chunks from Qdrant when an extracted PDF is deleted.
  * Sentiment analysis, key entities extraction, knowledge graph relationships, PDF report generation.
  * Add PDF title to extracted text (for context awareness)
  * Make newly created conversation visible in sidebar without needing to refresh

  </details>

</details>

<details><summary> Day 19 - 04/01/25 </summary>

## Day 19 - 04/01/25

* <details><summary> Export chat as PDF </summary>

	* Added ``app/services/report_generator.py``:

		```py
		from reportlab.platypus import (
						SimpleDocTemplate,
						Paragraph,
						Spacer,
						PageBreak,
				)
		from reportlab.lib.styles import getSampleStyleSheet
		from reportlab.lib.pagesizes import A4
		from datetime import datetime
		from pathlib import Path
		
		REPORTS_DIR = Path("reports")
		REPORTS_DIR.mkdir(parents=True, exist_ok=True)
		
		
		def generate_report_pdf(conversation: dict, output_path: str):
				doc = SimpleDocTemplate(
						output_path,
						pagesize=A4,
						rightMargin=40,
						leftMargin=40,
						topMargin=40,
						bottomMargin=40,
				)
		
				styles = getSampleStyleSheet()
				story = []
		
				# Title
				story.append(Paragraph(
						f"<b>{conversation.get('title', 'Conversation Report')}</b>",
						styles["Title"],
				))
				story.append(Spacer(1, 12))
		
				# Metadata
				story.append(Paragraph(
						f"<b>Conversation ID:</b> {conversation['conversation_id']}",
						styles["Normal"],
				))
		
				created_at = conversation.get("created_at")
				updated_at = conversation.get("updated_at")
		
				if created_at:
						story.append(Paragraph(
								f"<b>Created:</b> {created_at.strftime('%Y-%m-%d %H:%M:%S')}",
								styles["Normal"],
						))
		
				if updated_at:
						story.append(Paragraph(
								f"<b>Last updated:</b> {updated_at.strftime('%Y-%m-%d %H:%M:%S')}",
								styles["Normal"],
						))
		
				story.append(Spacer(1, 20))
		
				# Messages (Q&A)
				messages = conversation["messages"]
		
				for i in range(0, len(messages), 2):
						user_msg = messages[i]
						assistant_msg = messages[i + 1] if i + 1 < len(messages) else None
		
						story.append(Paragraph(
								f"<b>Q:</b> {user_msg['content']}",
								styles["Normal"],
						))
						story.append(Spacer(1, 6))
		
						if assistant_msg:
								story.append(Paragraph(
										f"<b>A:</b> {assistant_msg['content']}",
										styles["Normal"],
								))
		
						story.append(Spacer(1, 14))
		
				doc.build(story)
		```
    
	* Added router to ``app/routers/chat.py``:
    
		```py
		from app.services.report_generator import generate_report_pdf
		
		@router.get("/{conversation_id}/report")
		def generate_report(conversation_id: str):
				conversation = get_conversation(conversation_id)
		
				if not conversation:
						raise HTTPException(status_code=404, detail="Conversation not found")
		
				output_path = f"reports/{conversation_id}.pdf"
				generate_report_pdf(conversation, output_path)
		
				return FileResponse(
						output_path,
						media_type="application/pdf",
						filename="conversation_report.pdf",
				)
		```

	* Updated the frontend, ``frontend/src/App.tsx``:
 
		```tsx
		const exportConvo = async (convo: Conversation) => {
			const res = await fetch(`http://localhost:8000/chat/${convo.conversation_id}/report`, {
				method: "GET",
			});
		
			if (!res.ok) {
				alert("Failed to generate report");
			}
		
			setMenuOpenId(null);
		};
		```

	* Updated the dropdown menu in the frontend to include "Export as PDF":
 
		```tsx
		<div
			style={{ padding: "4px 8px", cursor: "pointer" }}
			onClick={(e) => {
				e.stopPropagation();
				exportConvo(c);
			}}
		>
			Export as PDF
		</div>
		```

	* The result:
 
		* "Export as PDF" option in dropdown menu:
		
			<img width="325" height="347" alt="image" src="https://github.com/user-attachments/assets/c3561d97-b903-4277-9301-9448efbfc7e2" />
		
		* Generated PDF report using ``reportlab``:
		
			<img width="944" height="700" alt="image" src="https://github.com/user-attachments/assets/19bc563d-f7de-4b9d-b0d5-2064f38a422a" />

	* The generated PDFs are stored currently in ``reports/`` which I have added to ``.gitignore``. It would be better if it opened a file explorer for the user to choose where they are saved.

  </details>

* <details><summary> Improve chatbot responses </summary>

	* As mentioned in the previous update, the chatbot's responses seem to not be very good when asking simple questions like _"summarise the points"_.
 	* I tried fixing the AI's responses by having the system rewrite the user's query using the prior 4 messages, however this seems to have backfired.
	* To keep things simple, I have removed the ``rewrite_query()`` step from the pipeline in ``app/routers/chat.py``:

		
	   	```diff
			@router.post("")
			def chat(request: ChatRequest):
					# 1. Create or reuse conversation
					conversation_id = request.conversation_id
					if not conversation_id:
							conversation_id = create_conversation()
			
					# 2. Load previous messages
					convo = get_conversation(conversation_id)
					previous_messages = convo["messages"]
			
		-	    # 3. Rewrite query
		-	    rewritten_query = rewrite_query(
		-	        request.question,
		-	        previous_messages
		-	    )
			
					# 4. Vector search using rewritten query
					search_results = search_similar_chunks(
							request.question,
		-	        rewritten_query,
							top_k=request.top_k,
					)
					context_chunks = [r["text"] for r in search_results]
			
					# 5. Generate answer using rewritten query
					answer = generate_answer(
							question=request.question,
		-	        question=rewritten_query,
							previous_messages=previous_messages,
							context_chunks=context_chunks,
					)
			
					# 6. Store new messages
		-	    rewrite = rewritten_query if rewritten_query != request.question else None
		-	    add_message(conversation_id, "user", request.question, rewrite)
					add_message(conversation_id, "user", request.question)
					add_message(conversation_id, "assistant", answer)
			
					# 7. Return response
					return {
							"conversation_id": conversation_id,
							"question": request.question,
		-	        "rewrite": rewrite,
							"answer": answer,
							"chunks_used": len(context_chunks),
					}
	    ```

	* Instead of rewriting the user's query using the previous messages for contextual awareness, I instead give the ``generate_answer()`` function the previous messages. So the ``gpt-4o-mini`` model is just run once, with the ``SYSTEM_PROMPT``, relevant document chunks, previous messages, and latest user query all fed as input.

		``app/services/chat_service.py``:
	
		```py
		def generate_answer(question: str, previous_messages: list[dict], context_chunks: list[str]) -> str:
				if not context_chunks:
						return "I do not know based on the provided documents."
		
				context = "\n\n---\n\n".join(context_chunks)
		
				messages = [
						{
								"role": "system",
								"content": SYSTEM_PROMPT
						},
						{
								"role": "system",
								"content":f"""{context}"""
						}
				]
				
				if previous_messages:
						last_n_messages = previous_messages[-4:]
						
						for message in last_n_messages:
								messages.append({
										"role": message["role"],
										"content": message.get("rewrite", message["content"])
								})
		
				# append the new question to the message history
				messages.append({
						"role": "user",
						"content": question
				})
		
				response = client.chat.completions.create(
						model=MODEL,
						messages=messages,
						temperature=0.2,  # lower = less creative, more factual
				)
		
				return response.choices[0].message.content
		```

	* This actually results in much better responses. The AI understands the context better, as it is given everything, rather than the document context and chat context in two separate instances.
	* I found that when using the ``rewrite_query()`` function, the AI-generated response would try to answer the user's query, rather than rewriting the user's query to make it more contextually aware. This problem is gone now.
	* Examples of bad responses with the old method:

 		<img width="649" height="574" alt="image" src="https://github.com/user-attachments/assets/63460256-8b80-4a14-9bb5-822036b9f924" />

		<img width="651" height="289" alt="image" src="https://github.com/user-attachments/assets/fe4d2130-a54f-40bd-86fc-f806058f4e10" />

	* Example of good responses with the new method:

		<img width="654" height="384" alt="image" src="https://github.com/user-attachments/assets/3754e9b4-2ea1-426a-b5c4-3135f7b4d632" />


	</details>

* <details><summary> Future additions </summary>

	* Format chatbot response if provided with Markdown/LaTex-style formatting
	* Possibly add functionality for multiple users, each having their own collection of conversations and documents, and a menu to login?
 	* Possibly store qdrant_data/ in MongoDB for persistance across multiple devices?
 	* Handle deletion of chunks from Qdrant when an extracted PDF is deleted.
 	* Sentiment analysis, key entities extraction, knowledge graph relationships.
  	* Improve generated PDF report.
 	* Add PDF title to extracted text (for context awareness)
 	* Make newly created conversation visible in sidebar without needing to refresh

	</details>
  
* <details><summary> New folder structure </summary>

    ```diff
      AI-Support-Agent/
        ├── app/
        │   ├── main.py
        │   ├── config.py
        │   ├── middleware/
        │   │   ├── logging.py
        │   │   └── file_size_limit.py
        │   ├── services/
        │   │   ├── file_storage.py
        │   │   ├── pdf_service.py
        │   │   ├── document_repository.py
        │   │   └── embedding_service.py
        │   │   ├── search_service.py
        │   │   ├── chat_service.py
        │   │   ├── conversation_service.py
    +   │   │   └── report_generator.py			<-- NEW
        │   ├── storage/
        │   │   └── pdfs/
        │   ├── core/
        │   │   ├── errors.py
        │   │   └── embeddings.py
        │   ├── routers/
        │   │   ├── health.py
        │   │   ├── pdf.py
        │   │   ├── qdrant_health.py
        │   │   ├── embeddings.py
        │   │   ├── search.py
        │   │   └── chat.py
        │   └── db/
        │       ├── mongodb.py
        │       └── qdrant.py
        ├── qdrant_data/
        │   └── ...
    +   ├── reports/							<-- NEW
    +   │   └── ...					    		<-- NEW
        ├── frontend/
        │   ├── node_modules/
        │   │   └── ...
        │   ├── public/
        │   │   └── ...
        │   ├── src/
        │   │   ├── App.tsx
        │   │   └── ...
        │   └── ...
        ├── .env
        ├── .gitignore
        ├── requirements.txt
        └── README.md
    ```
	</details>

</details>

<details><summary> Day 20 - 05/01/25 </summary>

## Day 20 - 05/01/25

* <details><summary> Display new chat on sidebar immediately </summary>

  * Previously newly created chats would not appear until after refreshing the page.
  * By adding this line to ``sendMessage`` in ``frontend/src/App.tsx``, the chat appears immediately in the sidebar once the user sends the first message:
 
    ```tsx
    // If the conversation is not yet in the sidebar, add it
    setConversations((prev) => {
      const exists = prev.some(c => c.conversation_id === data.conversation_id);
      if (!exists) {
        return [
          { conversation_id: data.conversation_id, title: data.title || "New Chat" },
          ...prev,
        ];
      }
      return prev;
    });
    ```

    </details>

* <details><summary> Future additions </summary>

	* Format chatbot response if provided with Markdown/LaTex-style formatting
	* Possibly add functionality for multiple users, each having their own collection of conversations and documents, and a menu to login?
 	* Possibly store qdrant_data/ in MongoDB for persistance across multiple devices?
 	* Handle deletion of chunks from Qdrant when an extracted PDF is deleted.
 	* Sentiment analysis, key entities extraction, knowledge graph relationships.
  	* Improve generated PDF report.
 	* Add PDF title to extracted text (for context awareness)

	</details>

</details>


<!--
<details><summary> Day N - 05/12/25 </summary>

## Day N - 05/12/25

* <details><summary> xxx </summary>

  ...

  </details>
  
* <details><summary> New folder structure </summary>
    !! USE THE LAST FOLDER STRUCTURE NOT THIS ONE !!
    ```diff
      AI-Support-Agent/
        ├── app/
        │   ├── main.py
        │   ├── config.py
        │   ├── middleware/
        │   │   ├── logging.py
        │   │   └── file_size_limit.py
        │   ├── services/
        │   │   ├── file_storage.py
        │   │   ├── pdf_service.py
        │   │   ├── document_repository.py
        │   │   └── embedding_service.py
        │   │   ├── search_service.py
        │   │   ├── chat_service.py
        │   │   └── conversation_service.py
        │   ├── storage/
        │   │   └── pdfs/
        │   ├── core/
        │   │   ├── errors.py
        │   │   └── embeddings.py
        │   ├── routers/
        │   │   ├── health.py
        │   │   ├── pdf_upload.py
        │   │   ├── pdf_extract.py
    +   │   │   ├── pdf_delete.py              <-- NEW
    +   │   │   ├── pdf_list.py                <-- NEW
        │   │   ├── qdrant_health.py
        │   │   ├── embeddings.py
        │   │   ├── search.py
        │   │   └── chat.py
        │   └── db/
        │       ├── mongodb.py
        │       └── qdrant.py
        ├── qdrant_data/
        │   └── ...
        ├── frontend/
        │   ├── node_modules/
        │   │   └── ...
        │   ├── public/
        │   │   └── ...
        │   ├── src/
        │   │   ├── App.tsx
        │   │   └── ...
        │   └── ...
        ├── .env
        ├── .gitignore
        ├── requirements.txt
        └── README.md
    ```
  </details>

</details>
-->

## Citations
