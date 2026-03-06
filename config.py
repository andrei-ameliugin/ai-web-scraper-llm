from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_api_url: str = "https://api.openai.com/v1/responses"
    openai_model: str = "gpt-4.1-mini"
    request_timeout: int = 10

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
