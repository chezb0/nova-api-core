# 🚀 Nova API Core

**A clean, modular, and production-ready backend framework built on top of FastAPI.**

Nova is designed for developers who want **full control, strong architecture, and zero magic** — without sacrificing productivity.

---

## ✨ Why Nova ?

Most frameworks either hide complexity or enforce rigid patterns. Nova takes a different approach:

- 🧠 Explicit over magic — no hidden behavior  
- 🧱 Clean Architecture first — strict separation of concerns  
- 🔌 Fully modular — plug your own components (DB, logger, providers)  
- ⚙️ Config-driven system — environment + multi-provider ready  
- 📦 CLI included — bootstrap real projects instantly  
- 🛡️ Structured error system — consistent and extensible  
- 📊 JSON logging — production-ready observability  

---

## 🏗️ Project Structure

core/ → business logic, config system, abstractions  
infra/ → external implementations (logger, db, providers)  
presentation/ → API layer (routes, handlers)  
tests/ → unit & integration tests  

No hidden layers. No implicit wiring.

---

## ⚡ Quick Start

# Create virtual environment
python -m venv venv  
source venv/bin/activate  # Linux / Mac  
venv\Scripts\activate     # Windows  

# Install Nova
pip install git+https://github.com/chezb0/nova-api-core.git

# Create project
nova init my_project  
cd my_project  

# Run API
uvicorn app:app --host localhost --port 8001

---

## 🔧 Configuration System

Nova uses a typed configuration system based on dataclasses.

### Bootstrap (.env.base)
APP_NAME=MyApp  
APP_VERSION=0.1.0  
ENV=dev  
LOG_LEVEL=DEBUG  
LOG_OUTPUT=CONSOLE  

### Environment (.env.dev)
DEBUG=true  
PORT=8000  

### AppConfig
from dataclasses import dataclass  
@dataclass  
class AppConfig:  
&nbsp;&nbsp;&nbsp;&nbsp;PORT: int  
&nbsp;&nbsp;&nbsp;&nbsp;DEBUG: bool  

### Loading
bootstrap_provider = EnvProvider(".env.base")  
bootstrap = ConfigLoader.load_bootstrap(bootstrap_provider)  

env_provider = EnvProvider(f".env.{bootstrap.ENV}")  

config = ConfigLoader.load_app_config(  
&nbsp;&nbsp;&nbsp;&nbsp;AppConfig,  
&nbsp;&nbsp;&nbsp;&nbsp;providers=[env_provider],  
)  

---

## 📜 Logging (JSON Structured)

logger = JsonLogger(  
&nbsp;&nbsp;&nbsp;&nbsp;app_name=bootstrap.APP_NAME,  
&nbsp;&nbsp;&nbsp;&nbsp;environment=bootstrap.ENV,  
&nbsp;&nbsp;&nbsp;&nbsp;# log_level=bootstrap.LOG_LEVEL  
&nbsp;&nbsp;&nbsp;&nbsp;# log_output=bootstrap.LOG_OUTPUT  
&nbsp;&nbsp;&nbsp;&nbsp;# log_file_path=bootstrap.LOG_FILE_PATH  
)  

Example:
{"timestamp":"2026-01-01T12:00:00Z","level":"INFO","message":"Starting Nova API","environment":"dev","app_name":"MyApp"}  

---

## 🛑 Error Handling

ERROR_HANDLERS = [  
&nbsp;&nbsp;&nbsp;&nbsp;AppExceptionHandler(),  
&nbsp;&nbsp;&nbsp;&nbsp;GenericExceptionHandler(),  
]  

- Centralized exception handling  
- Clean API responses  
- Structured logging for debugging  

---

## 🌐 Routing

ROUTES = [health_router]  

@router.get("/health")  
def health():  
&nbsp;&nbsp;&nbsp;&nbsp;return {"status": "ok"}  

---

## 🧠 App Factory

app = create_app(  
&nbsp;&nbsp;&nbsp;&nbsp;config=config,  
&nbsp;&nbsp;&nbsp;&nbsp;bootstrap=bootstrap,  
&nbsp;&nbsp;&nbsp;&nbsp;logger=logger,  
&nbsp;&nbsp;&nbsp;&nbsp;routes=ROUTES,  
&nbsp;&nbsp;&nbsp;&nbsp;error_handlers=ERROR_HANDLERS,  
)  

Everything is explicit. No hidden wiring.

---

## 🎯 Philosophy

Nova is built with one goal: give developers power and clarity, not magic and hidden complexity.

You control:
- configuration flow  
- architecture decisions  
- system evolution  

---

## 🚧 Status

Early-stage but actively evolving.

Planned:
- Vault provider integration  
- Module system (like NestJS)  
- CLI generators (routes, modules, providers)  
- Observability extensions  

---

## 🤝 Contributing

Contributions, ideas, and feedback are welcome.

---

## 👨‍💻 Author

Maintained by `Gence Lucien dit Bemanjary` — feel free to contribute or reuse the base structure.

---

## ⭐ Support

If you like the project, give it a star and follow its evolution.
