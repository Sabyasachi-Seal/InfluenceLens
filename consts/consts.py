class AppError:
    APP_START_FAIL = "Application not initialized"

class ModelConfig:
    EMBEDDING_MODEL = "models/embedding-001"
    LLM_MODEL = "gemini-2.5-flash"

class CorsConfig:
    CORSMIDDLEWARE_ALLOW_ORIGINS = ["*"]
    CORSMIDDLEWARE_ALLOW_CREDENTIALS = True
    CORSMIDDLEWARE_ALLOW_METHODS = ["*"]
    CORSMIDDLEWARE_ALLOW_HEADERS = ["*"]