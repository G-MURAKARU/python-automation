import sys

from multiclipboard import Clipboard

SAVED_DATA = "clipboard.json"


def main():
    if len(sys.argv) > 2:
        print("Please pass exactly one command.")
        return

    my_clipboard = Clipboard(SAVED_DATA)

    if len(sys.argv) == 1:
        print(my_clipboard)
    else:
        command: str = sys.argv[1]
        my_clipboard.clipboard(command)


if __name__ == "__main__":
    main()
