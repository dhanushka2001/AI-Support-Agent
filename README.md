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
    </details>

    using UUID to create unique file IDs.[^2]

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


<!--
<details><summary> Day N </summary>

## Day N - 05/12/25

* <details><summary> xxx </summary>

  ...

  </details>

</details>
-->

## Citations
