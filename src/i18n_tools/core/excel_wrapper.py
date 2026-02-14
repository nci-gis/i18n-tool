from collections.abc import Iterable
from pathlib import Path
from typing import Any, AnyStr, Dict, List, Union

import polars as pl
import xlsxwriter

from .base import DataReader, DataWriter, QueryBuilder


class ExcelReader(DataReader):
    def __init__(self, **kwargs):
        self.options = kwargs

    def read(self, fp: Path) -> Iterable["WorksheetWrapper"]:
        data = pl.read_excel(fp, sheet_id=0, **self.options)
        # remove all `commented-out` sheets:
        for key in data:
            if key.startswith("#"):
                del data[key]
        return [WorksheetWrapper(kv[0], kv[1]) for kv in data.items()]


class ExcelWriter(DataWriter):
    def __init__(self, **kwargs):
        self.options = kwargs

    def write(self, fp: Path, wb: "WorkbookWrapper", /, **kwargs):
        with xlsxwriter.Workbook(fp, options=self.options) as fs:
            for key in wb.sheets:
                ws: WorksheetWrapper = wb.sheets[key]
                df = ws.get_data()
                if df is not None:
                    df.write_excel(fs, worksheet=ws.name, **kwargs)


class WorksheetWrapper:
    def __init__(self, name: AnyStr, df: pl.DataFrame):
        self.name = name
        self.df = df

    def get_data(self) -> pl.DataFrame:
        return self.df

    def get_fields(self) -> List[str]:
        return self.df.columns()

    def query_by(
        self, queries: Union[QueryBuilder | Dict[str, QueryBuilder]]
    ) -> Union[pl.DataFrame | Dict[str, pl.DataFrame]]:
        if isinstance(queries, QueryBuilder):
            return self.df.sql(queries.build())
        else:
            ret: Dict[str, pl.DataFrame] = {}
            for key in queries:
                ret[key] = self.df.sql(queries[key].build())
            return ret


class WorkbookWrapper:
    def __init__(self, name: AnyStr):
        self.name = name
        self.sheets: Dict[str, WorksheetWrapper] = {}

    def load_data(self, fp: Path, reader: ExcelReader):
        sheets = reader.read(fp)
        for ws in sheets:
            self.add_sheet(ws)

    def add_sheet(self, ws: WorksheetWrapper) -> "WorkbookWrapper":
        self.sheets[ws.name] = ws
        return self

    def save_to(self, fp: Path, writer: ExcelWriter, /, **kwargs):
        writer.write(fp, self, **kwargs)

    def convert_to(self, converter: "ExcelConverter", /, **kwargs) -> Any:
        return converter.convert(self, **kwargs)


class ExcelConverter:
    def convert(self, wb: WorkbookWrapper, /, **kwargs) -> Any:
        raise NotImplementedError()
