import json
import os.path
import tempfile

from pydantic import Field
from pydantic.v1 import BaseSettings, root_validator

_DEFAULT_PATH = os.path.join(tempfile.gettempdir(), "web2vec")


class Config(BaseSettings):
    default_path: str = Field(env="WEB2VEC_DEFAULT_OUTPUT_PATH")
    crawler_output_path: str = Field(env="WEB2VEC_DEFAULT_CRAWLER_OUTPUT_PATH")
    remote_url_output_path: str = Field(env="WEB2VEC_DEFAULT_REMOTE_URL_PATH")
    open_page_rank_api_key: str = Field(env="WEB2VEC_OPEN_PAGERANK_API_KEY", default="")
    api_timeout: int = Field(env="WEB2VEC_API_TIMEOUT", default=60)

    @root_validator(pre=True)
    def set_default_path(cls, values):
        if not values.get("default_path"):
            values["default_path"] = _DEFAULT_PATH
        return values

    @root_validator(pre=True)
    def set_crawler_output_path(cls, values):
        if not values.get("crawler_output_path"):
            values["crawler_output_path"] = os.path.join(
                values.get("default_path"), "crawler"
            )
        return values

    @root_validator(pre=True)
    def set_remote_url_output_path(cls, values):
        if not values.get("remote_url_output_path"):
            values["remote_url_output_path"] = os.path.join(
                values.get("default_path"), "remote"
            )
        return values

    @classmethod
    def from_json(cls, filepath: str):
        with open(filepath, "r") as file:
            data = json.load(file)
        return cls(**data)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


config = Config(open_page_rank_api_key="", api_timeout=60)
