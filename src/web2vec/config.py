import os.path
import tempfile

from pydantic import field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_PATH = os.path.join(tempfile.gettempdir(), "web2vec")


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="WEB2VEC_", env_file="../../.env", env_file_encoding="utf-8"
    )

    default_output_path: str = _DEFAULT_PATH
    remote_url_output_path: str = ""
    open_page_rank_api_key: str = ""
    api_timeout: int = 60
    crawler_output_path: str = ""
    crawler_spider_depth_limit: int = 5

    @field_validator("remote_url_output_path", "crawler_output_path", mode="before")
    @classmethod
    def set_correct_path(cls, value: str, info: ValidationInfo):
        data = info.data
        field_name = info.field_name

        if not value:
            if field_name == "remote_url_output_path":
                return os.path.join(data["default_output_path"], "remote")
            if field_name == "crawler_output_path":
                return os.path.join(data["default_output_path"], "crawler")
        return value


config = Config()
