# AI-Support-Agent

## Progress updates 
<details><summary>Day 1 - 03/12/25</summary>
  
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

<details><summary>Day 2 - 04/12/25</summary>
  
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
  
* Switched from using ``fastapi dev main.py``[^6] (quick sandbox testing, accepts only relative importing, e.g. ``from .routers.health import router as health_router
``) to load the web API to ``uvicorn app.main:app --reload --host 127.0.0.1 --port 8000``[^6][^7][^8] (recommended production-standard approach, accepts absolute importing, e.g. ``from app.routers.health import router as health_router
``). The latter command didn't work initially (website hanged) but after running these commands in PowerShell (administrator mode):

  ```console
  netsh winsock reset
  netsh int ip reset
  ```

   and restarting my PC it worked.

[^6]: First Steps - FastAPI, https://fastapi.tiangolo.com/tutorial/first-steps/
[^10]: Deployment - Uvicorn, https://uvicorn.dev/deployment/
[^11]: Run a Server Manually - FastAPI, https://fastapi.tiangolo.com/deployment/manually/
[^12]: Debugging - FastAPI, https://fastapi.tiangolo.com/tutorial/debugging/
  
  
* Added a ``.env`` file:[^7]

  ```env
  # Deployment environment
  ENVIRONMENT=development
  
  # CORS allowed origins (comma-separated)
  CORS_ALLOWED_ORIGINS=["http://localhost:5173", "http://127.0.0.1:5173"]
  ```

  to hold secrets & environment-dependent values (not pushed to remote, added to ``.gitignore``).

[^7]: Settings and Environment Variables - FastAPI, https://fastapi.tiangolo.com/advanced/settings

* Added ``config.py``:[^7]

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

  ``.env`` stores sensitive info (e.g., secrets, API keys, origins), ``config.py`` loads them into Python using a ``Settings`` class (using Pydantic v2).[^7][^8] Production-quality FastAPI apps always use .env + a config module. And we used ``pydantic_settings`` over ``python-dotenv`` to load the environment variables as it is cleaner, safer, faster, validated, and the recommended modern approach for FastAPI applications (type validation, required values checked, integration with FastAPI/Pydantic, default values built-in, and automatic override with OS env vars).

[^8]: Read settings from .env - Settings and Environment Variables - FastAPI, https://fastapi.tiangolo.com/advanced/settings/?h=#read-settings-from-env
  
* Added logging middleware,[^9] that logs method, path, and timing in the console:

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

[^9]: Middleware - FastAPI, https://fastapi.tiangolo.com/tutorial/middleware/
  
* The current folder structure:

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

</details>

<details><summary> Day 3 - 05/12/25 </summary>

## Day 3 - 05/12/25
* <details><summary>Enable users to upload a PDF file to the backend</summary>
  
  * <details><summary>New folder structure</summary>

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
      │       └──pdf_upload.py    <-- NEW
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

  * <details><summary>New folder structure</summary>

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
      │       └──pdf_upload.py
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

* <details><summary> Update .gitignore </summary>

  Add this to ``.gitignore`` to prevent ``/__pycache__`` being pushed to remote:[^143]

  [^143]: Python Programming Course - Imperial College London COMP70053 Lesson 8 Chapter 5.3, https://python.pages.doc.ic.ac.uk/2022/lessons/core08/05-robot/03-ignore.html
  
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


<!--
<details><summary> Day N </summary>

## Day N - 05/12/25

* <details><summary> xxx </summary>

  ...

  </details>

</details>
-->

## Citations
