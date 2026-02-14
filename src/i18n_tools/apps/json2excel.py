import argparse
from collections import OrderedDict
from pathlib import Path
from typing import AnyStr, Dict, List

import polars as pl

# @ import numpy as np
from recursivenamespace import utils

import i18n_tools.shared as shared
from i18n_tools.adapters.cli.app import i18n_cli as cli
from i18n_tools.core.base import LocaleData
from i18n_tools.core.enums import LocaleStyle
from i18n_tools.core.excel_wrapper import ExcelWriter, WorkbookWrapper, WorksheetWrapper
from i18n_tools.core.json_wrapper import JsonLocale, JsonReader
from i18n_tools.shared import Const, DirectoryItem, EN_I18nSchema, Fields
from i18n_tools.utils import logger

# @start> Initialization:
en_i18n = EN_I18nSchema()
full_key = "FullKey"
# @end> Initialization.


def make_key(str_val: AnyStr):
    root, *keys = utils.split_key(str_val)
    if len(keys) == 0:
        return (None, root)
    return (root, utils.join_key(keys))


# @ def make_keys(vals: Any):
#     roots = []
#     keys = []
#     rk_map = map(make_key, vals)
#     for r, k in rk_map:
#         roots.append(r)
#         keys.append(k)
#     return roots, keys


class DataFrameWrapper:
    def __init__(self, name: str):
        self.name: str = name
        self.content: Dict[str, Dict] = {}

    def add_content(self, lang: str, data: Dict):
        self.content[lang] = data

    def __add_lang(self, df: pl.DataFrame, keys, lang_name: str, lang_dic: Dict) -> pl.DataFrame:
        arr = [lang_dic.get(key) for key in keys]
        df = df.with_columns(pl.lit(pl.Series(lang_name, arr)))
        return df

    def to_df(self) -> pl.DataFrame:
        # convert "en"
        en: List = utils.flatten_as_list(self.content[en_i18n.en], flat_list_type=utils.FlatListType.WITH_SMART_INDEX)
        # convert json to dataframe:
        full_keys = []
        en_data = []
        for en_item in en:
            fk = en_item[0]
            root, key = make_key(fk)
            val = en_item[1]
            full_keys.append(fk)
            en_data.append((fk, root, key, val))
        en_schema = [full_key] + en_i18n.values()
        df = pl.DataFrame(en_data, schema=en_schema, orient="row")
        # print(df)

        # convert the rest:
        langs = list(self.content.keys())
        langs.remove(en_i18n.en)
        for lang in langs:
            other = utils.flatten_as_dict(self.content[lang])
            df = self.__add_lang(df, full_keys, lang, other)
        # remove col: full_key
        df = df.drop(full_key)
        # print(df)
        return df


class JsonWrapper:
    def __init__(self):
        self.df_wrappers: Dict[str, DataFrameWrapper] = {}

    def add_content(self, locale: LocaleData):
        if locale.namespace not in self.df_wrappers:
            self.df_wrappers[locale.namespace] = DataFrameWrapper(locale.namespace)
        df_w = self.df_wrappers[locale.namespace]
        df_w.add_content(locale.lang, locale.data)

    def save_as_excel(self, out_dir: Path, name: str):
        out_file = out_dir / f"{name}{Const.EXCEL_EXT}"
        writer = ExcelWriter()
        wb = WorkbookWrapper(name)
        for df_w in self.df_wrappers.values():
            ws = WorksheetWrapper(df_w.name, df_w.to_df())
            wb.add_sheet(ws)
        # save to file:
        logger.info(f">> write to file : {out_file}")
        wb.save_to(out_file, writer)


class I18nJsonDataLoader:
    def __init__(self, locale_style: LocaleStyle, dir_items: List[DirectoryItem]):
        self.locale_style = locale_style
        self.dir_items = dir_items
        self.json_wrappers: Dict[str, JsonWrapper] = {}

    def load_data(self, options: Dict = None):
        options = options or {}
        app_cfg = shared.AppConfig()
        json_reader = JsonReader(**options)
        json_wrappers = self.json_wrappers
        json_locale = JsonLocale.create_instance(self.locale_style, reader=json_reader)
        for d in self.dir_items:
            if d.name not in json_wrappers:
                json_wrappers[d.name] = JsonWrapper()
            jw: JsonWrapper = json_wrappers[d.name]
            files = d.get_files(f"*{Const.JSON_EXT}", home_dir=app_cfg.home_dir())
            # print(files)
            for fp in files:
                locale = json_locale.load_locale(fp, object_pairs_hook=OrderedDict)
                jw.add_content(locale)
        # print(self.json_wrappers)

    def __export_json_wrapper(self, out_dir: Path, name: str, jw: JsonWrapper):
        jw.save_as_excel(out_dir, name)

    def export_to_excel(self, out_dir: Path):
        for name, jw in self.json_wrappers.items():
            self.__export_json_wrapper(out_dir, name, jw)


def get_input_dirs() -> List[DirectoryItem]:
    app_cfg = shared.AppConfig()
    inputs = app_cfg.get(Fields.J2E_INPUTS)
    if isinstance(inputs, list):
        dirs = [DirectoryItem(**pj.to_dict()) for pj in inputs]
    else:
        p = app_cfg.json_in_dir()
        if not p.exists():
            return []
        in_dirs = [x for x in p.iterdir() if x.is_dir()]
        # if no sub-directory, use the input directory itself:
        if len(in_dirs) == 0:
            in_dirs = [p]
        dirs = [DirectoryItem(in_dir.name, in_dir) for in_dir in in_dirs]
    # @ret:
    return dirs


@cli.register_as_tool(name="j2e", desc="Convert i18n json files to excel files.")
class Json2ExcelApp(shared.AppBase):
    def __init__(self, name: str, description: str):
        super().__init__(name, description)

    def run(self, args: argparse.Namespace = None):
        logger.debug(f"CMD > j2e > arguments: {args}")

        # Get app_config:
        app_cfg = shared.AppConfig()

        # Initialize:
        out_dir = app_cfg.excel_out_dir()
        if not out_dir.exists():
            out_dir.mkdir(parents=True)
        dir_items = get_input_dirs()
        locale_style = app_cfg.get(Fields.LOCALE_STYLE, LocaleStyle.PER_NAMESPACE.value)
        i18n = I18nJsonDataLoader(LocaleStyle.of(locale_style), dir_items)

        # load all json files:
        i18n.load_data({"encoding": "utf8", "errors": "ignore"})

        # export to excel files:
        i18n.export_to_excel(out_dir)


# Main (debugging / testing) purpose:
if __name__ == "__main__":
    args = argparse.Namespace(home_dir=None)
    shared.main_func(Json2ExcelApp("", ""), args)
