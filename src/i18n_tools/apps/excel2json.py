import argparse
from collections.abc import Generator
from pathlib import Path
from typing import Any, Dict, List, NamedTuple

import polars as pl
from recursivenamespace import RecursiveNamespace, rns, utils

import i18n_tools.shared as shared
from i18n_tools.adapters.cli.app import i18n_cli as cli
from i18n_tools.core.base import AppBase, LocaleData
from i18n_tools.core.enums import LocaleStyle
from i18n_tools.core.errors import InvalidExcelStructure
from i18n_tools.core.excel_wrapper import (
    ExcelConverter,
    ExcelReader,
    WorkbookWrapper,
    WorksheetWrapper,
)
from i18n_tools.core.json_wrapper import JsonLocale, JsonWriter
from i18n_tools.shared import Const, DirectoryItem, EN_I18nSchema, Fields
from i18n_tools.utils import logger

# @start> Initialization:
en_i18n = EN_I18nSchema()
full_key = "FullKey"
# @end> Initialization.


class DF2RNS:
    def __init__(self, ws: WorksheetWrapper):
        self.ws = ws

    def __add_full_key(self, df: pl.DataFrame) -> pl.DataFrame:
        new_df = df.with_columns(
            pl.when(pl.col(en_i18n.root).is_null() & pl.col(en_i18n.key).is_null())
            .then(pl.col(en_i18n.en))
            .when(pl.col(en_i18n.root).is_null())
            .then(pl.col(en_i18n.key))
            .when(pl.col(en_i18n.key).is_null())
            .then(pl.col(en_i18n.root))
            .otherwise(
                pl.concat_str(
                    pl.col(en_i18n.root),
                    pl.col(en_i18n.key),
                    separator=utils.KEY_SEP_CHAR,
                )
            )
            .alias(full_key)
        )
        return new_df

    @rns.rns(use_raw_key=True, use_chain_key=True)
    def to_rns(self, df: pl.DataFrame, lang: str) -> RecursiveNamespace:
        ret: List[utils.KV_Pair] = []
        for i in range(len(df)):
            key = df[full_key][i]
            value = df[lang][i]
            if value is not None and value != "":
                ret.append(utils.KV_Pair(key, value))
        # @return:
        return ret

    def save_as_json(self, save_to: Path, locale_style: LocaleStyle, indent: int = 2):
        df: pl.DataFrame = self.ws.df
        # excludes column: Root and Key
        languages = df.columns[2:]
        # add column: FullKey = Root + Key
        df = self.__add_full_key(df)
        #! create json locale based on locale style:
        writer = JsonWriter(encoding="utf8")
        json_locale = JsonLocale.create_instance(locale_style, writer=writer)
        for lang in languages:
            # extract each language to RNS object
            data = self.to_rns(df, lang)
            locale_data = LocaleData(self.ws.name, lang, data)
            # save the language to json file:
            logger.info(f"Saving locale: '{locale_data.namespace} of {locale_data.lang}' to '{save_to}'")
            json_locale.save_locale(
                save_to,
                locale_data,
                create_parents=True,
                indent=indent,
                ensure_ascii=False,
            )


class ConverterMap(NamedTuple):
    name: str
    conv: DF2RNS


class RNS_Converter(ExcelConverter):  # NOSONAR
    def convert(self, wb):
        for ws in wb.sheets.values():
            yield ConverterMap(wb.name, DF2RNS(ws))


class I18nExcelDataLoader:
    def __init__(self, locale_style: LocaleStyle, dir_items: List[DirectoryItem]):
        self.json_indent = shared.AppConfig().get(Fields.E2J_INDENT, 2)
        self.locale_style = locale_style
        self.dir_items = dir_items
        self.workbooks: Dict[str, WorkbookWrapper] = {}

    def load_data(self, options: Dict = None):
        app_cfg = shared.AppConfig()
        workbooks = self.workbooks
        for d in self.dir_items:
            if d.name not in workbooks:
                workbooks[d.name] = WorkbookWrapper(name=d.name)
            wb: WorkbookWrapper = workbooks[d.name]
            files = d.get_files(f"*{Const.EXCEL_EXT}", home_dir=app_cfg.home_dir())
            # print(files)
            options = options or {}
            reader = ExcelReader(**options)
            for fp in files:
                if len(fp.parts) < 2:
                    raise InvalidExcelStructure()
                wb.load_data(fp, reader)
        # print(self.workbooks)

    def __export_workbook(self, out_dir: Path, wb: WorkbookWrapper):
        conv_map: Generator[ConverterMap, Any, None] = wb.convert_to(RNS_Converter())
        for cm in conv_map:
            # store json file to: <out_dir>/<workbook_name/project_name>
            fp: Path = out_dir / cm.name
            # save to json file:
            cm.conv.save_as_json(fp, self.locale_style, self.json_indent)

    def export_to_json(self, out_dir: Path):
        for wb in self.workbooks.values():
            self.__export_workbook(out_dir, wb)


def get_input_dirs() -> List[DirectoryItem]:
    app_cfg = shared.AppConfig()
    inputs = app_cfg.get(Fields.E2J_INPUTS)
    if isinstance(inputs, list):
        dirs = [DirectoryItem(**pj.to_dict()) for pj in inputs]
    else:
        p = app_cfg.excel_in_dir()
        if not p.exists():
            return []
        in_dirs = [x for x in p.iterdir() if x.is_dir()]
        # if no sub-directory, use the input directory itself:
        if len(in_dirs) == 0:
            in_dirs = [p]
        dirs = [DirectoryItem(in_dir.name, in_dir) for in_dir in in_dirs]
    # @ret:
    return dirs


@cli.register_as_tool(name="e2j", desc="Convert i18n excel files to json files.")
class Excel2JsonApp(AppBase):
    def __init__(self, name: str, description: str):
        super().__init__(name, description)

    def run(self, args: argparse.Namespace = None):
        logger.debug(f"CMD > e2j > arguments: {args}")

        # Get app_config:
        app_cfg = shared.AppConfig()

        # Initialize:
        out_dir = app_cfg.json_out_dir()
        if not out_dir.exists():
            out_dir.mkdir(parents=True)
        dir_items = get_input_dirs()
        locale_style = app_cfg.get(Fields.LOCALE_STYLE, LocaleStyle.PER_NAMESPACE.value)
        i18n = I18nExcelDataLoader(LocaleStyle.of(locale_style), dir_items)

        # load all excel files:
        i18n.load_data()

        # export to json files:
        i18n.export_to_json(out_dir)


# Main (debugging / testing) purpose:
if __name__ == "__main__":
    args = argparse.Namespace(home_dir=None)
    shared.main_func(Excel2JsonApp("", ""), args)
