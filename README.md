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
```
python -m venv venv  
source venv/bin/activate  # Linux / Mac  
venv\Scripts\activate     # Windows 
```

# Install Nova
```
pip install git+https://github.com/chezb0/nova-api-core.git
```

# Create project
```
nova init my_project (optional: --db sqlalchemy | mongodb, this command automatically generates and configures your database manager)
cd my_project
```

# Run API
```
uvicorn app:app --host localhost --port 8001
```

---

## 🔧 Configuration System

Nova uses a typed configuration system based on dataclasses.

### Bootstrap (.env.base)
```
APP_NAME=MyApp  
APP_VERSION=0.1.0  
ENV=dev  
LOG_LEVEL=DEBUG  
LOG_OUTPUT=CONSOLE
``` 

### Environment (.env.dev)
```
DEBUG=true  
PORT=8000
```

### AppConfig
```
from dataclasses import dataclass  
@dataclass  
class AppConfig:  
    PORT: int  
    DEBUG: bool 
```

### Loading
```
bootstrap_provider = EnvProvider(".env.base")  
bootstrap = ConfigLoader.load_bootstrap(bootstrap_provider)  

env_provider = EnvProvider(f".env.{bootstrap.ENV}")  

config = ConfigLoader.load_app_config(  
    AppConfig,  
    providers=[env_provider],  
) 
```

---

## 📜 Logging (JSON Structured)
```
logger = JsonLogger(  
    app_name=bootstrap.APP_NAME,  
    environment=bootstrap.ENV,  
    # log_level=bootstrap.LOG_LEVEL  
    # log_output=bootstrap.LOG_OUTPUT  
    # log_file_path=bootstrap.LOG_FILE_PATH  
) 
```

Example:
```
{"timestamp":"2026-01-01T12:00:00Z","level":"INFO","message":"Starting Nova API","environment":"dev","app_name":"MyApp"}  
```

---

## 🛑 Error Handling
```

ERROR_HANDLERS = [  
    AppExceptionHandler(),  
    GenericExceptionHandler(),  
] 
```

- Centralized exception handling  
- Clean API responses  
- Structured logging for debugging  

---

## 🌐 Routing
```
ROUTES = [health_router]  

@router.get("/health")  
def health():  
    return {"status": "ok"}  
```
---

## 🧠 App Factory
```
app = create_app(  
    config=config,  
    bootstrap=bootstrap,  
    logger=logger,  
    routes=ROUTES,  
    error_handlers=ERROR_HANDLERS,  
) 
```

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
