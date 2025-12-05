# AI-Support-Agent

## Progress updates 
<details><summary>Day 1 - 03/12/25</summary>
  
## Day 1 - 03/12/25
* Created main application entry point in ``app/main.py``.
* Expose a simple endpoint to confirm server availability, GET /health returns a basic JSON response with meaningful info: API version and timestamp[^1]:

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

* Using https://fastapi.tiangolo.com/tutorial/first-steps/ as a guide.
* Using ``fastapi dev main.py`` to load the web API. Accessible via ``http://127.0.0.1:8000/``, ``http://127.0.0.1:8000/health/``, and  ``http://127.0.0.1:8000/docs#/`` (which uses Swagger UI).
</details>

<details><summary>Day 2 - 04/12/25</summary>
  
## Day 2 - 04/12/25
* Configured CORS to support future frontend interactions and manage app settings cleanly[^2].
* Moved the health function defintion to a separate file, inside ``app/routers/health.py``. ``main.py`` can access it by doing ``from app.routers.health import router as health_router`` and ``app.include_router(health_router)``.

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

* Added a ``.gitignore``:

  ```txt
  app/__pycache__/
  ```
  
* Added ``requirements.txt``:

  ```txt
  fastapi
  uvicorn[standard]
  python-dotenv
  ```

  running ``pip install -r requirements.txt`` installs all dependencies easily.

  [^2]: CORS (Cross-Origin Resource Sharing) - FastAPI, https://fastapi.tiangolo.com/tutorial/cors/?h=cors
* Switched from using ``fastapi dev main.py`` (quick sandbox testing, accepts only relative importing, e.g. ``from .routers.health import router as health_router
``) to load the web API to ``uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`` (recommended production-standard approach, accepts absolute importing, e.g. ``from app.routers.health import router as health_router
``). The latter command didn't work initially (website hanged) but after running these commands in PowerShell (administrator mode):

  ```console
  netsh winsock reset
  netsh int ip reset
  ```

   and restarting my PC it worked.
  
* Added a ``.env`` file:

  ```env
  # Deployment environment
  ENVIRONMENT=development
  
  # CORS allowed origins (comma-separated)
  CORS_ALLOWED_ORIGINS=["http://localhost:5173", "http://127.0.0.1:5173"]
  ```

  to hold secrets & environment-dependent values (not pushed to remote, added to ``.gitignore``).

* Added ``config.py``:

  ```python
  from pydantic_settings import BaseSettings
  from functools import lru_cache
  
  class Settings(BaseSettings):
      ENVIRONMENT: str = "development"
      CORS_ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
  
      # Later you can add:
      # OPENAI_API_KEY: str
      # DB_URL: str
  
      class Config:
          env_file = ".env"
          env_file_encoding = "utf-8"
  
  @lru_cache()
  def get_settings():
      return Settings()
  
  settings = get_settings()
  ```

  ``.env`` stores sensitive info (e.g., secrets, API keys, origins), ``config.py`` loads them into Python using a ``Settings`` class. Production-quality FastAPI apps always use .env + a config module. And we used ``pydantic_settings`` over ``python-dotenv`` to load the environment variables as it is cleaner, safer, faster, validated, and the recommended modern approach for FastAPI applications (type validation, required values checked, integration with FastAPI/Pydantic, default values built-in, and automatic override with OS env vars).
  
* Added logging middleware, that logs method, path, and timing in the console:

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
  
* The current file structure:

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
  

    
