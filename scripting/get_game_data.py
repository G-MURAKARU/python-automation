import gc
import json
import os
import pathlib
import re
import shutil
import sys
from subprocess import PIPE, run

DIR_PATTERN = "*[g|G][a|A][m|M][e|E]*"
FILE_EXTENSION = "*.go"
COMPILE_COMMAND = ["go", "build"]


def get_absolute_path(dir_file: str) -> pathlib.Path:
    """
    get_absolute_path gets the absolute path of a file or directory

    Args:
        dir_file (str): file/directory relative path

    Returns:
        pathlib.Path: absolute path
    """

    return pathlib.Path(dir_file).resolve(dir_file)


def find_all_game_paths(source_dir: pathlib.Path) -> list[pathlib.Path]:
    """
    find_all_game_paths finds all absolute paths of directories containing substring "game" - case-insensitive

    Args:
        source_dir (pathlib.Path): directory to traverse

    Returns:
        list[pathlib.Path]: list of found game directories
    """

    # os.walk() - recursive
    # if statement ensures return of only directories containing 'game', not files
    return [
        item
        for item in source_dir.glob(DIR_PATTERN)
        # .rglob() for recursive search
        if item.is_dir()
    ]


def setup_target_dir(dirname: str) -> pathlib.Path:
    """
    setup_target_dir sets up a target directory to store found game data (if it does not exist)

    Args:
        dirname (str): name of target directory

    Returns:
        pathlib.Path: absolute path to target directory
    """

    # os.path.exists(), os.path.mkdir()
    pathlib.Path(dirname).mkdir(exist_ok=True)
    return get_absolute_path(dirname)


def get_names_from_paths(
    paths: list[pathlib.Path], to_strip: str
) -> list[str]:
    """
    get_names_from_paths renames found directories, removing given substring

    Args:
        paths (list[pathlib.Path]): list of directories to rename (absolute paths)
        to_strip (str): substring to remove from directory names

    Returns:
        list[str]: list of new directory names
    """

    new_names = []
    for path in paths:
        # os.path.split()
        dirname: str = path.name
        # using regex to find case-insensitive matches of the to_strip string
        # (assumes there is only one match per string)
        new_dirname = dirname.replace(
            re.findall(to_strip, dirname, flags=re.IGNORECASE)[0], ""
        )
        new_names.append(new_dirname)

    return new_names


def copy_and_overwrite(source: pathlib.Path, dest: str) -> None:
    """
    copy_and_overwrite recursively copies old directories into a new location,
    with overwrite if they already exist

    Args:
        source (pathlib.Path): directory to recursively copy
        dest (str): new directory location
    """

    _ = shutil.copytree(src=source, dst=dest, dirs_exist_ok=True)


def create_new_dirs(
    old_dirs: list[pathlib.Path],
    new_dirpath: pathlib.Path,
    new_dirs: list[str],
) -> None:
    """
    create_new_dirs creates new (directory absolute paths) to use as destination directories

    Args:
        old_dirs (list[pathlib.Path]): list of (absolute paths of) old directories to copy
        new_dirpath (pathlib.Path): copy destination (parent dir of new dirs)
        new_dirs (list[str]): new directory names
    """

    for src_path, new_dir in zip(old_dirs, new_dirs):
        # os.path.join()
        dest_path = pathlib.Path.joinpath(new_dirpath, new_dir)
        copy_and_overwrite(source=src_path, dest=dest_path)


def make_json_metadata_file(path: pathlib.Path, dirs: list[str]) -> None:
    """
    make_json_metadata_file contains some metadata for copied data

    Args:
        path (pathlib.Path): absolute path for file storing metadata
        dirs (list[str]): some metadata
    """

    data = {"game_names": dirs, "number_of_games": len(dirs)}
    json_path = path.joinpath("metadata.json")

    # pathlib.Path().open() works like builtin open() function
    with json_path.open(mode="w") as metadata_file:
        json.dump(data, metadata_file)


def compile_code_files(path: pathlib.Path):
    """
    compile_code_file compiles given files with a given bash command

    Args:
        path (pathlib.Path): directory containing files to compile
    """

    for file in path.rglob(FILE_EXTENSION):
        cwd = pathlib.Path().absolute()
        os.chdir(file.parent)
        command = COMPILE_COMMAND + [file.name]
        gc.collect()
        run(command, stdin=PIPE, stdout=PIPE, universal_newlines=True)
        os.chdir(cwd)


def main(args: list):
    """
    main directs everything

    Args:
        args (list): list of command-line arguments
    """

    source, target = args
    # os.getcwd() + os.path.join()
    source_path = get_absolute_path(source)
    game_dirs = find_all_game_paths(source_path)
    new_game_dirs = get_names_from_paths(game_dirs, "game")
    target_path = setup_target_dir(target)

    create_new_dirs(
        old_dirs=game_dirs, new_dirpath=target_path, new_dirs=new_game_dirs
    )
    make_json_metadata_file(target_path, new_game_dirs)
    compile_code_files(target_path)


# sourcery skip: raise-specific-error
if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise Exception("You must pass a source and target directory - only.")

    main(args=sys.argv[1:])
