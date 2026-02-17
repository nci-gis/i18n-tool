import argparse
import dataclasses
import logging
import sys
from functools import lru_cache
from pathlib import Path
from typing import AnyStr, Optional, Union

import yaml
from recursivenamespace import RecursiveNamespace, rns

from i18n_tools.core.base import AppBase, Schema
from i18n_tools.utils import EnvVar, logger, simple_singleton

PKG_DIR = Path(__file__).parent.resolve()
# internal resources:
RESOURCES_DIR = PKG_DIR / "resources"
DEFAULT_CFG_FILE = RESOURCES_DIR / "default.yaml"


@lru_cache
@rns.rns()
def load_config(fp: Path = None):
    """Load app config from .env, default config, custom config (if provided).
    With precedence:

        .env < default config < custom config (if provided)
    """
    logger.debug(f"Loading app config from: {fp if fp else 'default only'}")

    cnf = {}
    # load from `.env`:
    env = cnf[Const.ENV] = {}
    env[EnvVar.INPUT_DIR.lower()] = EnvVar.get_str(EnvVar.INPUT_DIR, Const.INPUT)
    env[EnvVar.OUTPUT_DIR.lower()] = EnvVar.get_str(EnvVar.OUTPUT_DIR, Const.OUTPUT)
    env[EnvVar.JSON_DIR.lower()] = EnvVar.get_str(EnvVar.JSON_DIR, Const.JSON)
    env[EnvVar.EXCEL_DIR.lower()] = EnvVar.get_str(EnvVar.EXCEL_DIR, Const.EXCEL)

    # load from default `config.yaml`:
    with open(DEFAULT_CFG_FILE) as fs:
        data = yaml.safe_load(fs)
        cnf.update(**data)

    # load user custom config:
    if fp is not None:
        with open(fp) as fs:
            data = yaml.safe_load(fs)
            cnf.update(**data)

    # return final result:
    return cnf


class Const:
    EMPTY = ""
    COMMA = ","
    EN = "en"  # language.
    INPUT = "input"
    OUTPUT = "output"
    EXCEL = "excel"
    EXCEL_EXT = ".xlsx"  # excel extension.
    JSON = "json"
    JSON_EXT = ".json"  # json extension.
    ENV = "env"  # environment.


class Fields:
    APP_NAME = "app.name"
    LOCALE_STYLE = "app.locale_style"
    LOG_LEVEL = "log.level"
    J2E_INPUTS = "json2excel.inputs"
    E2J_INPUTS = "i18n.inputs"
    E2J_INDENT = "i18n.indent"


@simple_singleton
class AppConfig:
    """Application configuration manager. Singleton class."""

    def __init__(self, home_dir: Path = None):
        self._home_dir: Path = self.__resolve_home_dir(home_dir)
        self.custom_config = self.__resolve_custom_config()
        self.cfg: RecursiveNamespace = self.__load_config(self.custom_config)
        # additional paths:
        self.app_name = self.cfg.get_or_else(Fields.APP_NAME, "i18n-tools")

    # @private:
    @staticmethod
    def __resolve_home_dir(home_dir: Path = None) -> Path:
        """Resolve home_dir path. Default to ~/i18n-tools if not set."""
        if home_dir:
            return home_dir.expanduser().resolve()
        # check EnvVar first:
        home_dir_str = EnvVar.get_str(EnvVar.HOME_DIR, "")
        p = Path(home_dir_str) if home_dir_str else Path.home() / "i18n-tools"
        # create if not exist:
        if not p.exists():
            p.mkdir(parents=True)
        return p.expanduser().resolve()

    # @ private:
    def __resolve_custom_config(self) -> Optional[Path]:
        """Resolve custom config file path if provided."""
        config_file = EnvVar.get_str(EnvVar.CONFIG_FILE, "")
        if config_file:
            p = Path(config_file)
            if not p.is_absolute():
                p = self._home_dir / p
            if p.exists() and p.is_file():
                return p.resolve()
        return None

    # @private:
    @staticmethod
    def __load_config(fp: Path = None) -> RecursiveNamespace:
        """Load config from file path, return as RecursiveNamespace."""
        cfg = load_config(fp)
        return cfg

    def get(self, key: str, default=None, show_log=False):
        """Get config value by key with optional default."""
        return self.cfg.get_or_else(key, or_else=default, show_log=show_log)

    def home_dir(self) -> Path:
        """Get home directory path."""
        return self._home_dir

    def input_dir(self) -> Path:
        """Get input directory path."""
        p = Path(self.cfg.env.input_dir or Const.INPUT)
        if not p.is_absolute():
            p = self.home_dir() / p
        if not p.exists():
            raise FileNotFoundError(f"Input directory not found: {p}")
        return p.resolve()

    def output_dir(self) -> Path:
        """Get output directory path."""
        p = Path(self.cfg.env.output_dir or Const.OUTPUT)
        if not p.is_absolute():
            p = self.home_dir() / p
        if not p.exists():
            p.mkdir(parents=True)
        return p.resolve()

    def json_in_dir(self) -> Path:
        """Get JSON directory path."""
        p = Path(self.cfg.env.json_dir or Const.JSON)
        if not p.is_absolute():
            p = self.input_dir() / p
        if not p.exists():
            raise FileNotFoundError(f"JSON directory not found: {p}")
        return p.resolve()

    def json_out_dir(self) -> Path:
        """Get JSON directory path."""
        p = Path(self.cfg.env.json_dir or Const.JSON)
        if not p.is_absolute():
            p = self.output_dir() / p
        return p.resolve()

    def excel_in_dir(self) -> Path:
        """Get Excel directory path."""
        p = Path(self.cfg.env.excel_dir or Const.EXCEL)
        if not p.is_absolute():
            p = self.input_dir() / p
        if not p.exists():
            raise FileNotFoundError(f"Excel directory not found: {p}")
        return p.resolve()

    def excel_out_dir(self) -> Path:
        """Get Excel directory path."""
        p = Path(self.cfg.env.excel_dir or Const.EXCEL)
        if not p.is_absolute():
            p = self.output_dir() / p
        return p.resolve()


@dataclasses.dataclass
class DirectoryItem:
    name: str
    path: str
    pattern: Optional[str] = None
    include: Optional[Union[str | list]] = None
    exclude: Optional[Union[str | list]] = None

    def get_files(self, pattern="*.*", home_dir: Path = None) -> list[Path]:
        p = Path(self.path)
        # make the path relative to `home_dir` if provided and `path` is not absolute:
        if not p.is_absolute() and home_dir is not None:
            p = home_dir / p
        # list all files match `pattern`:
        _pattern = self.pattern or pattern
        files = p.rglob(_pattern)
        if self.include is not None:
            arr = self.include if isinstance(self.include, list) else [str(self.include)]
            ret = [f for f in files if f.name in arr]
            return ret
        elif self.exclude is not None:
            arr = self.exclude if isinstance(self.exclude, list) else [str(self.exclude)]
            ret = [f for f in files if f.name not in arr]
            return ret
        else:
            return list(files)


@dataclasses.dataclass
class EN_I18nSchema(Schema):  # NOSONAR
    root: AnyStr = "Root"
    key: AnyStr = "Key"
    en: AnyStr = Const.EN


def main_func(app: AppBase, args: argparse.Namespace = None):
    """Main entry point for the i18n-tools application."""
    try:
        # Get app_config:
        home_dir = None
        if args is not None and args.home_dir is not None:
            home_dir = Path(args.home_dir)
        app_cfg = AppConfig(home_dir)

        # Update log level with app config:
        logger.setLevel(app_cfg.get(Fields.LOG_LEVEL, logging.INFO))

        # Run the tool:
        logger.info("..::START::..")
        app.run(args)
        logger.info("..::END::..")
    except Exception:
        logger.error("Exception occurred in `app.run(...)` :", exc_info=True)
        sys.exit(1)
