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
```
my_project/
├── app.py                        # Application entry point
├── pyproject.toml               # Project dependencies and build config
├── nova_core.json               # Framework configuration file
├── .env.base                    # Base environment variables
├── .env.dev                     # Development environment variables
├── .env.prod                    # Production environment variables
│
├── core/                        # Business logic layer (pure domain rules)
│   ├── config/                  # Core configuration (shared settings, constants)
│   ├── domain/                 # Domain layer (business concepts)
│   │   ├── models/             # Domain models (business objects)
│   │   ├── schemas/            # Data validation / DTOs
│   │   └── entities/           # Core entities (business rules objects)
│   └── use_cases/              # Application use cases (business actions / services)
│
├── infra/                       # Infrastructure layer (external systems)
│   ├── logger/                 # Logging system setup
│   ├── db/                     # Database implementations
│   │   ├── sqlalchemy/        # SQLAlchemy implementation
│   │   └── mongo/             # MongoDB implementation
│   └── config/                # Infrastructure-specific configuration
│
├── presentation/                # API / interface layer (FastAPI, controllers)
│   ├── app_factory.py          # Application factory (FastAPI app builder)
│   ├── routes/                 # API route definitions (endpoints)
│   ├── schemas/                # Request/response schemas (API layer DTOs)
│   ├── exception_handlers/     # Global API exception handling
│   └── utils/                  # Presentation helpers (response formatting, etc.)
│
└── tests/                       # Unit and integration tests
```
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
nova init my_project --db sqlalchemy
cd my_project
```
NOTE: --db sqlalchemy | mongodb, this command automatically generates and configures your database manager

# Generate CRUD
```
nova crud products
```
NOTE: nova crud {resource} generates a full CRUD for the {resource}, including use cases, routes, dependency injection (deps), schemas, and models ready for adding your personal fields.

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


## 📜 License

This project is licensed under a custom source-available license.

**Copyright (c) 2026 Gence Lucien dit Bemanjary**

---

### ✅ You are free to:
- Use this framework for personal, educational, and commercial purposes  
- Modify the source code  
- Distribute and fork the project  
- Use it inside commercial applications or services  

---

### ⚠️ Conditions:
- You must keep the original author attribution visible  
- You must clearly indicate any modifications made  
- You must include the license notice in all copies or derivatives  

---

### ❌ You are NOT allowed to:
- Sell this framework in its original or modified form  
- Repackage and sell it as a standalone product  
- Commercialize it as a competing framework  

---

### 💼 Commercial use:
You may use this framework inside commercial products or services as a dependency or component.

However, you are not allowed to sell the framework itself or any modified version of it.

---

### 📬 Permissions:
For commercial licensing or resale rights, please contact the author.
