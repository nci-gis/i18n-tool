import argparse
import sys
from typing import Type

from i18n_tools import __version__
from i18n_tools.core.base import AppBase, AppInfo
from i18n_tools.utils import logger
from i18n_tools.utils.decorator import decorator_factory, simple_singleton

# @start> Initialization:
__VERSION__ = __version__
tool_choices = ["e2j", "j2e"]
# @end> Initialization.


@simple_singleton
class CLI(AppBase):
    def __init__(self):
        super().__init__(
            name="i18n_tools",
            description="The i18n-tools that supports to convert Excel to Json format and vice versa.",
        )
        self.arg_parser = argparse.ArgumentParser(
            prog=self.name,
            description=self.description,
            epilog="--end--",
        )
        self.tool_mapper = {}

    @decorator_factory()
    def register_as_tool(self, name: str = "tool", desc: str = "A sample tool") -> callable:
        """Decorator to register an app type as tool.
        Args:
            name (str): The name of the app.
            desc (str): A short description of the app.
        Returns:
            Callable: A decorator that registers the app type.
        """

        def decorator(klass: Type[AppBase]):
            if not issubclass(klass, AppBase):
                raise TypeError(f"Class {klass.__name__} must inherit from AppBase.")
            if name in self.tool_mapper:
                logger.warning(f"[WARN] App '{name}' is already registered. Overwrite it.")
            logger.debug(f"[INFO] Registering app: {name} - {desc}")
            # Register the app type:
            self.tool_mapper[name] = AppInfo(name=name, description=desc, klass=klass)
            return klass

        return decorator

    def parse_args(self, args=None) -> argparse.Namespace:
        """Parse command line arguments."""
        return self.arg_parser.parse_args(args)

    def add(self, *args, **kwargs) -> "CLI":
        """Add ArgumentParser argument.
        Ref: ArgumentParser.add_argument

        Returns:
            CLI: itself
        """
        self.arg_parser.add_argument(*args, **kwargs)
        return self

    def run(self, args: argparse.Namespace = None):
        """Run the CLI application."""
        logger.debug(f">> cmd arguments: {args}")

        # Run the tool:
        if args.tool in self.tool_mapper:
            tool_info: AppInfo = self.tool_mapper[args.tool]
            tool = tool_info.new_instance()
            logger.debug(f">> Running tool: {tool}")
            tool.run(args)
        else:
            logger.error("[ERR] unknown command.")
            self.arg_parser.print_help()
            sys.exit(1)


i18n_cli = (
    CLI()
    .add(
        "tool",
        nargs="?",
        choices=tool_choices,
        help="Specify which tool to use.",
    )
    .add(
        "--home-dir",
        help="Specify the `home` directory that the tool will look up for data input/output.",
    )
    .add("-v", "--version", action="version", version=f"[%(prog)s] : v{__VERSION__}")
)
