import abc
import os
import shutil
from pathlib import Path

from pyrep.candidate import Candidate


class Transformer(abc.ABC):
    def transform_dir(self, candidate: Candidate, dst: os.PathLike):
        src = Path(candidate.src)
        dst = Path(dst)
        if not dst.exists():
            if src.is_file():
                shutil.copy2(src, dst)
            elif src.is_dir():
                shutil.copytree(src, dst)
            else:
                raise IOError("Source must be a file or directory")
        if dst.is_file():
            self.transform_file(dst)
        elif dst.is_dir():
            for directory, _, files in os.walk(dst):
                for file in files:
                    self.transform_file(dst / file)

    def transform_file(self, file: os.PathLike):
        pass


class CopyTransformer(Transformer):
    def transform_dir(self, candidate: Candidate, dst: os.PathLike):
        src = Path(candidate.src)
        dst = Path(dst)
        if not dst.exists():
            if src.is_file():
                shutil.copy2(src, dst)
            elif src.is_dir():
                shutil.copytree(src, dst)
            else:
                raise IOError("Source must be a file or directory")
