import argparse
import dataclasses
from typing import Any, AnyStr, Dict, List, Optional, Type


class AppBase(object):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.name}, description={self.description})"

    def run(self, args: argparse.Namespace = None):
        raise NotImplementedError("Subclasses should implement this method.")


@dataclasses.dataclass
class AppInfo:
    name: str
    description: str
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = dataclasses.field(default_factory=dict)
    klass: Type[AppBase] = Optional[Type[AppBase]]  # The class type of the app.

    def new_instance(self) -> AppBase:
        """Create a new instance of the app."""
        return self.klass(self.name, self.description, *self.args, **self.kwargs)


@dataclasses.dataclass
class Schema:
    @classmethod
    def fields(cls) -> List[str]:
        ret = []
        for f in dataclasses.fields(cls):
            ret.append(f.name)
        return ret

    def values(self, *args: List[str]) -> List[Any]:
        if not args:
            args = self.fields()
        return [getattr(self, field) for field in args]

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


class DataReader:
    def read(self, *args, **kwargs) -> Any:
        raise NotImplementedError()


class DataWriter:
    def write(self, *args, **kwargs):
        raise NotImplementedError()


@dataclasses.dataclass
class QueryBuilder:
    sql: str = ""

    def append(self, query: str) -> "QueryBuilder":
        self.sql = f"{self.sql} {query}"
        return self

    def select(self, columns: List[AnyStr]) -> "QueryBuilder":
        sep = ","
        if columns:
            self.sql = f"select {sep.join(columns)} from self"
        else:
            self.sql = "select * from self"
        return self

    def build(self) -> str:
        return self.sql


@dataclasses.dataclass
class LocaleData:
    namespace: str
    lang: str
    data: Dict
