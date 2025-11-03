from src.config import settings

def check_settings():
    # Verify that .env variables loaded successfully without printing secrets
    print("Configuration loaded.")
    print(f"Requests per minute limit: {settings.MAX_REQ_PER_MIN}")
    print(f"Tokens per day limit: {settings.MAX_TOKENS_PER_DAY}")
    print(f"Default model: {settings.DEFAULT_MODEL}")
    print(f"Output directory: {settings.OUTPUT_DIR}")

    # Check if API key  exists
    if settings.OPENAI_API_KEY:
        print("API key detected (not displayed).")
    else:
        print("o API key found in .env.")

if __name__ == "__main__":
    check_settings()