"""
    this is the ``multiclipboard`` module.
    this module defines one class, Clipboard.
"""

import json
import pathlib

# pip install pyperclip
import pyperclip


class Clipboard:
    """
    The Clipboard class defines a Clipboard object, its attributes and methods
    """

    def __init__(self, filename: str) -> None:
        """
        __init__ is the Clipboard object constructor

        Args:
            filename (str): path to file simulating the computer's persistent clipboard cache (cut-copy-paste)
        """

        self.filename = filename

    def __str__(self) -> str:
        """
        __str__ returns an informal string representation of the clipboard

        Returns:
            str: the clipboard file's absolute file path
        """

        return f"Clipboard location: {pathlib.Path(self.filename).absolute()}"

    def _save_data_to_clipboard(self, data: dict) -> None:
        """
        _save_data_to_clipboard saves data to the clipboard file cache as a dictionary
        If the file does not exist, it will create the file; if it exists, it overwrites file contents

        Args:
            data (dict): actual clipboard cache as a dictionary
        """

        with open(file=self.filename, mode="w") as c_board:
            json.dump(data, c_board)

    def _load_data_from_clipboard(self, key: str = None) -> dict:
        """
        _load_data_from_clipboard loads data from the clipboard file cache as a dictionary

        Args:
            key (str, optional): a label representing particular saved data. Defaults to None.

        Returns:
            dict: saved data retrieved upon request
        """

        try:
            with open(file=self.filename, mode="r") as c_board:
                data: dict = json.load(c_board)
        except FileNotFoundError:
            return None
        else:
            return data if key is None else data.get(key)

    def _save_data(self, current_clipboard: dict) -> None:
        """
        _save_data handles saving logic - takes in user input and directs it to file cache

        Args:
            current_clipboard (dict): current state of the clipboard cache
        """

        if not current_clipboard:
            current_clipboard = {}

        key: str = input("Enter a label for copied data: ")
        current_clipboard[key] = pyperclip.paste()
        self._save_data_to_clipboard(data=current_clipboard)
        print("data saved!")

    def _load_data(self, current_clipboard, label: str = None) -> dict:
        """
        _load_data handles the data retrieval logic - takes in user input and searches cache for matches

        Args:
            current_clipboard (dict): current state of the clipboard cache
            label (str, optional): string given to represent particular saved data. Defaults to None.

        Returns:
            dict|str: dictionary representing full clipboard cache or string representing particular retrieved data
        """

        if not current_clipboard:
            print("clipboard is empty.")
        elif label:
            try:
                retrieved_data: str = current_clipboard[label]
            except KeyError:
                print(
                    "label does not exist. use <list> command to see current clipboard contents."
                )
            else:
                pyperclip.copy(retrieved_data)
                print("data copied to clipboard!")
        else:
            print(current_clipboard)

    def _delete_clipboard(self):
        """
        _delete_clipboard deletes the generated clipboard cache
        """

        clipboard_path = pathlib.Path(self.filename)
        clipboard_path.unlink(missing_ok=True)

    def clipboard(self, command: str):
        """
        clipboard is the main clipboard - handles all clipboard logic and directs control flow accordingly

        Args:
            command (str): user's input command that prompts a given action
        """

        current_clipboard: dict = self._load_data_from_clipboard()

        match command:
            case "save":
                self._save_data(current_clipboard)

            case "load":
                key: str = input("Enter label to retrieve data: ")
                self._(current_clipboard, label=key)

            case "list":
                self._(current_clipboard)

            case "clear" | "delete":
                self._delete_clipboard()

            case _:
                print("Unknown command.")
