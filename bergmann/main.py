import sys

from bergmann.ui.app import Bergmann


def main() -> None:
    debug = "--debug" in sys.argv
    app = Bergmann(debug=debug)
    app.run()


if __name__ == "__main__":
    main()
