import os
import pickle
import pandas as pd
from pathlib import Path
from functools import wraps
from typeguard import typechecked


@typechecked()
def cached(cache_dir_path: Path):
    """
    If given path does not exist, run function (argument) and dump data into cache, else read from file.
    
    NOTE: Fixing the protocol or changing the datatype might improve compatibility and thus reusability of
          the data across different python versions - would also be interesting for run tests

    :param cache_dir_path: Path, Path to cache file
    :return: Whatever your function (executed by wrapper) is supposed to do
    """
    # handle file name and extension
    file_path_and_name, extension = os.path.splitext(cache_dir_path)

    # assert correct file extension given, to avoid issues (.pickle seems to be best practvie for python3)
    assert extension in [".pickle", ".pkl"], \
        f"Got unexpected file extension {extension} for 'cache_dir_path' {cache_dir_path}"

    def inner_cached(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not cache_dir_path.exists():
                ret = func(*args, **kwargs)

                cache_dir_path.parent.mkdir(parents=True, exist_ok=True)
                with cache_dir_path.open("wb") as f:
                    pickle.dump(ret, f, protocol=4)

            else:
                with cache_dir_path.open("rb") as f:
                    ret = pickle.load(f)

            return ret

        return wrapper
    return inner_cached
