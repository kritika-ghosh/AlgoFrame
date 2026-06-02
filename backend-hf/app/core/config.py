# app/core/config.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GROQ_API_KEY: str = ""
    SPACE_HOST_URL: str = "http://127.0.0.1:7860"
    MANIM_QUALITY_FLAG: str = "-ql" 
    GEMINI_API_KEY: str

    # Tells Pydantic to look for a .env file in the root execution context path
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # Prevents crashes if extra variables exist in the env file
    )

settings = Settings()