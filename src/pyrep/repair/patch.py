"""
The patch module provides the necessary tools to generate patches from candidates.
"""

import difflib
import os
from pathlib import Path
from typing import List, Optional

from pyrep.candidate import GeneticCandidate
from pyrep.constants import DEFAULT_WORK_DIR
from pyrep.genetic.transform import MutationTransformer


def write_patches(
    candidates: List[GeneticCandidate], out: Optional[os.PathLike] = None
):
    """
    Generate patch files from a list of candidates.
    :param List[GeneticCandidate] candidates: The candidates to generate patches from.
    :param Optional[os.PathLike] out: The output directory for the patches.
    """
    patches = Path(out or DEFAULT_WORK_DIR, "patches")
    patches.mkdir(parents=True, exist_ok=True)
    file_format = f"{{:0{len(str(len(candidates)))}d}}.patch"
    # Iterate over the candidates and generate patches
    for i, candidate in enumerate(candidates, start=1):
        patch = get_patch(candidate, out=out)
        # Write the patch to a file
        with (patches / file_format.format(i)).open("w") as patch_file:
            patch_file.write(patch)


def get_patch(candidate: GeneticCandidate, out: Optional[os.PathLike] = None) -> str:
    """
    Generate a patch from a candidate.
    :param GeneticCandidate candidate: The candidate to generate a patch from.
    :param Optional[os.PathLike] out: The output directory for the patch.
    :return str: The patch generated from the candidate.
    """
    transformer = MutationTransformer()
    tmp = Path(out or DEFAULT_WORK_DIR, "patch")
    transformer.transform(candidate, tmp)
    patch = ""
    # Iterate over the files and generate a unified diff
    for file in transformer.files:
        with (candidate.src / file).open("r") as src_file, (tmp / file).open(
            "r"
        ) as diff_file:
            src = src_file.readlines()
            dst = diff_file.readlines()
        # Generate the diff and add it to the patch
        diff = difflib.unified_diff(src, dst, fromfile=file, tofile=file)
        patch += "".join(diff) + "\n"
    return patch
