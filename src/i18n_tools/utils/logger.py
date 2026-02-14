import logging
import sys

from dotenv import load_dotenv

from .env_helper import EnvVar

load_dotenv()  # take environment variables from .env.

try:
    from colorama import Fore, Style, init

    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False


class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        msg = super().format(record)
        if COLORAMA_AVAILABLE:
            color = self.COLORS.get(record.levelno, "")
            msg = f"{color}{msg}{Style.RESET_ALL}"
        return msg


def get_logger(name: str = "i18n-tools", level: int = None, color_mode: bool = True) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        handler = logging.StreamHandler(sys.stdout)
        with_color = color_mode and COLORAMA_AVAILABLE
        formatter_cls = ColorFormatter if with_color else logging.Formatter
        formatter = formatter_cls("[%(asctime)s] %(levelname)s <%(name)s>: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    # Prevent log messages from being propagated to the root logger
    logger.propagate = False
    if level is None:
        level = logging.INFO
    logger.setLevel(level)
    return logger


# Initialize a default logger instance with the log level set to INFO (changeable):
logger = get_logger(
    name=EnvVar.get_str(EnvVar.APP_NAME, "i18n-tools"),
    level=logging.INFO,
    color_mode=EnvVar.get_boolean(EnvVar.LOG_COLOR_MODE),
)
