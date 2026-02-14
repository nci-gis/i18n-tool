import os

# @start> Initialization:
TRUTHY_VALUES = ["yes", "true", "1"]  # for boolean conversion.
# @end> Initialization.


class EnvVar:
    """Helper class to get environment variables."""

    ## EnvVar names:
    # General:
    APP_NAME = "APP_NAME"
    LOG_COLOR_MODE = "LOG_COLOR_MODE"

    # For App:
    HOME_DIR = "HOME_DIR"
    CONFIG_FILE = "CONFIG_FILE"
    INPUT_DIR = "INPUT_DIR"
    OUTPUT_DIR = "OUTPUT_DIR"
    JSON_DIR = "JSON_DIR"
    EXCEL_DIR = "EXCEL_DIR"

    @staticmethod
    def get(key: str, default=None):
        return os.getenv(key, default)

    @staticmethod
    def get_str(key: str, default=""):
        return str(os.getenv(key, default))

    @staticmethod
    def get_boolean(key) -> bool:
        """Get a boolean config, if the value represent by:
            "true" or "yes" or "1".

        Args:
            key (str): EnvVar name

        Returns:
            bool: True | False
        """
        value = EnvVar.get_str(key).lower()
        return value in TRUTHY_VALUES

    @staticmethod
    def get_int(key, default=0) -> int:
        try:
            value = os.getenv(key)
            if value is not None:
                return int(value)
        except Exception:
            pass  # @skip error.
        return default

    @staticmethod
    def get_float(key, default=0.0) -> float:
        try:
            value = os.getenv(key)
            if value is not None:
                return float(value)
        except Exception:
            pass  # @skip error.
        return default

    @staticmethod
    def get_list(key, sep=",") -> list:
        """Get value of a EnvVar as a list.
            Return an empty list if not found.

        Args:
            key (str): EnvVar name
        """
        value = EnvVar.get_str(key)
        return value.split(sep)
