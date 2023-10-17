import json
import typing
from typing import Optional

import polars as pl
from dagster import (
    ConfigurableIOManagerFactory,
    InitResourceContext,
    InputContext,
    OutputContext,
    UPathIOManager,
)
from dagster import _check as check
from dagster._core.storage.io_manager import IOManager
from pydantic import BaseModel
from upath import UPath


class PolarsArrowFileSystemIOManager(UPathIOManager):
    extension: str = ".arrow"

    def __init__(self, base_dir=None, **kwargs):
        from upath import UPath

        self.base_dir = check.opt_str_param(base_dir, "base_dir")
        super().__init__(base_path=UPath(base_dir, **kwargs))

    def dump_to_path(self, context: OutputContext, obj: pl.DataFrame, path: UPath):
        obj.write_ipc(path, compression="zstd")

    def load_from_path(self, context: InputContext, path: UPath) -> pl.DataFrame:
        return pl.read_ipc(path)


class ConfigurablePolarsArrowFileSystemIOManager(ConfigurableIOManagerFactory):
    base_dir: Optional[str]

    def create_io_manager(self, context: InitResourceContext) -> IOManager:
        base_dir = self.base_dir or check.not_none(context.instance).storage_directory()
        return PolarsArrowFileSystemIOManager(base_dir)


class JSONFileSystemIOManager(UPathIOManager):
    extension: str = ".json"

    def __init__(self, base_dir=None, **kwargs):
        from upath import UPath

        self.base_dir = check.opt_str_param(base_dir, "base_dir")
        super().__init__(base_path=UPath(base_dir, **kwargs))

    def dump_to_path(self, context: OutputContext, obj: dict, path: UPath):
        with open(path, "w") as file:
            json.dump(obj, file)

    def load_from_path(self, context: InputContext, path: UPath) -> pl.DataFrame:
        with open(path, "r") as file:
            obj = json.load(file)
        return obj


class ConfigurableJSONFileSystemIOManager(ConfigurableIOManagerFactory):
    base_dir: Optional[str]

    def create_io_manager(self, context: InitResourceContext) -> IOManager:
        base_dir = self.base_dir or check.not_none(context.instance).storage_directory()
        return JSONFileSystemIOManager(base_dir)


class PydanticFileSystemIOManager(UPathIOManager):
    extension: str = ".json"

    def __init__(self, base_dir=None, **kwargs):
        from upath import UPath

        self.base_dir = check.opt_str_param(base_dir, "base_dir")
        super().__init__(base_path=UPath(base_dir, **kwargs))

    def dump_to_path(self, context: OutputContext, obj: BaseModel | list[BaseModel], path: UPath):
        context.log.info({"input_type": context.dagster_type.__dict__})
        serialized = [element.dict() for element in obj] if isinstance(obj, list) else obj.dict()
        with open(path, "w") as file:
            json.dump(serialized, file)

    def load_from_path(self, context: InputContext, path: UPath):
        # Load JSON from file
        with open(path, "r") as file:
            deserialized = json.load(file)

        # Extract type from Input Asset
        type_class = context.dagster_type.typing_type
        if isinstance(type_class, typing._GenericAlias) and type_class.__origin__ == list:
            # Extract type of inner Pydantic model
            model_class = context.dagster_type.typing_type.__args__[0]
            assert issubclass(model_class, BaseModel)
            # Construct Pydantic model from dicts
            return [model_class(**data) for data in deserialized]
        else:
            return type_class(**deserialized)


class ConfigurablePydanticFileSystemIOManager(ConfigurableIOManagerFactory):
    base_dir: Optional[str]

    def create_io_manager(self, context: InitResourceContext) -> IOManager:
        base_dir = self.base_dir or check.not_none(context.instance).storage_directory()
        return PydanticFileSystemIOManager(base_dir)
