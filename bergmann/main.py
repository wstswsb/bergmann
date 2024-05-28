import sys

from bergmann.ui.app import Bergmann


def global_exception_handler(exception_type, exception, traceback):
    print(f"an exception occurred: {exception_type}")


def main() -> None:
    debug = "--debug" in sys.argv
    app = Bergmann(debug=debug)
    app.run()


if __name__ == "__main__":
    sys.excepthook = global_exception_handler
    main()
