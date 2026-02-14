import json
from pathlib import Path
from typing import Dict, Type

from recursivenamespace import RecursiveNamespace

from i18n_tools.utils import logger

from .base import DataReader, DataWriter, LocaleData
from .enums import LocaleStyle
from .errors import InvalidJsonStructure, InvalidLocaleStyle


class JsonReader(DataReader):
    def __init__(self, **kwargs):
        self.options = kwargs

    def read(self, fp: Path, /, **kwargs) -> Dict:
        """_summary_

        Args:
            fp (Path): File path
            kwargs (Dict): json.load params, e.g.:
                object_pairs_hook=OrderedDict

        Returns:
            Dict: json data
        """
        with open(str(fp), **self.options) as fs:
            return json.load(fs, **kwargs)


class JsonWriter(DataWriter):
    def __init__(self, **kwargs):
        self.options = kwargs

    def write(self, fp: Path, data: Dict, /, **kwargs):
        """Write JSON data to a file.

        Args:
            fp (Path): the file path to write to.
            data (Dict): the JSON data to write.
            kwargs (Dict):
                - create_parents=True: create parent directories if not exist.
                - and json.dumps params, e.g.: indent=4, ensure_ascii=False
        """
        create_parents = kwargs.pop("create_parents", False)
        if create_parents:
            fp.parent.mkdir(parents=True, exist_ok=True)
        # Write to file:
        with open(str(fp), mode="w", **self.options) as fs:
            out = json.dumps(data, **kwargs)
            fs.write(out)

    def write_rns(self, fp: Path, data: RecursiveNamespace, /, **kwargs):
        self.write(fp, data.to_dict(), **kwargs)


class JsonLocale:
    def __init__(self, reader: JsonReader = None, writer: JsonWriter = None):
        self.reader = reader
        self.writer = writer

    # @start> protected methods:
    def _load_data(self, locale_file: Path, /, **kwargs) -> dict:
        """Load locale data from a JSON file."""
        if self.reader is None:
            raise ValueError("JsonReader is not initialized.")
        return self.reader.read(locale_file, **kwargs)

    def _save_data(self, locale_file: Path, locale_data: LocaleData, /, **kwargs):
        """Save locale data to a JSON file."""
        if self.writer is None:
            raise ValueError("JsonWriter is not initialized.")
        self.writer.write_rns(locale_file, locale_data.data, **kwargs)

    # @end> protected methods.

    def load_locale(self, locale_file: Path, /, **kwargs) -> LocaleData:
        raise NotImplementedError()

    def save_locale(self, save_to: Path, locale_data: LocaleData, /, **kwargs):
        raise NotImplementedError()

    @staticmethod
    def create_instance(
        locale_style: LocaleStyle, reader: JsonReader = None, writer: JsonWriter = None
    ) -> Type["JsonLocale"]:
        if locale_style == LocaleStyle.PER_NAMESPACE:
            return LocalePerNamespace(reader, writer)
        elif locale_style == LocaleStyle.PER_LOCALE:
            return LocalePerLanguage(reader, writer)
        else:
            raise InvalidLocaleStyle(locale_style.value)


class LocalePerNamespace(JsonLocale):
    """JSON locale wrapper class for per-namespace style."""

    def __init__(self, reader: JsonReader, writer: JsonWriter):
        super().__init__(reader, writer)

    def load_locale(self, locale_file: Path, /, **kwargs) -> LocaleData:
        """Load locale data from a JSON file structured as per-namespace style."""
        if len(locale_file.parts) < 3:
            raise InvalidJsonStructure(
                "Invalid JSON structure of PerNamespace style, e.g.: project/namespace/<lang>.json"
            )
        namespace = locale_file.parent.name
        lang = locale_file.stem
        logger.debug(f">> load locale data from file : {locale_file}")
        data = self._load_data(locale_file, **kwargs)
        return LocaleData(namespace, lang, data)

    def save_locale(self, save_to: Path, locale_data: LocaleData, /, **kwargs):
        """Save locale data to a JSON file structured as per-namespace style."""
        # if not save_to.exists():
        #     save_to.mkdir(parents=True)
        locale_file = save_to / locale_data.namespace / f"{locale_data.lang}.json"
        logger.debug(f">> write locale data to file : {locale_file}")
        self._save_data(locale_file, locale_data, **kwargs)


class LocalePerLanguage(JsonLocale):
    """JSON locale wrapper class for per-language (locale) style."""

    def __init__(self, reader: JsonReader, writer: JsonWriter):
        super().__init__(reader, writer)

    def load_locale(self, locale_file: Path, /, **kwargs) -> LocaleData:
        """Load locale data from a JSON file structured as per-language (locale) style."""
        if len(locale_file.parts) < 3:
            raise InvalidJsonStructure("Invalid JSON structure of PerLocale style, e.g.: project/lang/<namespace>.json")
        namespace = locale_file.stem
        lang = locale_file.parent.name
        logger.debug(f">> load locale data from file : {locale_file}")
        data = self._load_data(locale_file, **kwargs)
        return LocaleData(namespace, lang, data)

    def save_locale(self, save_to: Path, locale_data: LocaleData, /, **kwargs):
        """Save locale data to a JSON file structured as per-language (locale) style."""
        # if not save_to.exists():
        #     save_to.mkdir(parents=True)
        locale_file = save_to / locale_data.lang / f"{locale_data.namespace}.json"
        logger.debug(f">> write locale data to file : {locale_file}")
        self._save_data(locale_file, locale_data, **kwargs)
