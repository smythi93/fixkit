import difflib
import os
from pathlib import Path
from typing import List, Optional

from pyrep.candidate import GeneticCandidate
from pyrep.constants import DEFAULT_WORK_DIR
from pyrep.transform import MutationTransformer


def get_patches(candidates: List[GeneticCandidate], out: Optional[os.PathLike] = None):
    tmp = Path(out or DEFAULT_WORK_DIR, "patch")
    patches = Path(out or DEFAULT_WORK_DIR, "patches")
    transformer = MutationTransformer()
    file_format = f"{{:0{len(str(len(candidates)))}d}}.patch"
    for i, candidate in enumerate(candidates, start=1):
        patch = ""
        transformer.transform_dir(candidate, tmp)
        for file in transformer.files:
            with (candidate.src / file).open("r") as src_file, (tmp / file).open(
                "r"
            ) as diff_file:
                src = src_file.readlines()
                dst = diff_file.readlines()
            diff = difflib.unified_diff(src, dst, fromfile=file, tofile=file)
            patch += "".join(diff) + "\n"
        with (patches / file_format.format(i)).open("w") as patch_file:
            patch_file.write(patch)
