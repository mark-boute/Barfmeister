import os
from pathlib import Path


def get_boi_file_bath(user_id: int, year: int):

    # Make sure the /bois dir exists.
    if not os.path.exists("./bois"):
        os.mkdir("./bois")

    # Make sure the /bois/'year' folder exists.
    if not os.path.exists(f"./bois/{str(year)}"):
        os.mkdir(f"./bois/{str(year)}")

    # Make sure the /bois/'year'/'user_id'.csv exists
    if not os.path.exists(f"./bois/{str(year)}/{str(user_id)}.csv"):
        Path(f"./bois/{str(year)}/{str(user_id)}.csv").touch()

    return f"./bois/{str(year)}/{str(user_id)}.csv"


get_boi_file_bath(1234, 2021)
