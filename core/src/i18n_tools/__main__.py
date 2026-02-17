"""main entry point"""

from i18n_tools import i18n_cli as cli
from i18n_tools import main_func


def main():
    # @ main_func(cli, cli.parse_args(["j2e"]))
    main_func(cli, cli.parse_args())


if __name__ == "__main__":
    main()
