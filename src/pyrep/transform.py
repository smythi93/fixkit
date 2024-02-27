import abc
import ast
import os
import shutil
from pathlib import Path

from pyrep.candidate import Candidate, GeneticCandidate
from pyrep.genetic.operators import Mutator


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
            self.transform_file(candidate, dst)
        elif dst.is_dir():
            for directory, _, files in os.walk(dst):
                for file in files:
                    self.transform_file(candidate, dst / file)

    def transform_file(self, candidate: Candidate, file: os.PathLike):
        if self.need_to_transform(candidate, file):
            self.transform(candidate, file)

    def need_to_transform(self, candidate: Candidate, file: os.PathLike) -> bool:
        return False

    @abc.abstractmethod
    def transform(self, candidate: Candidate, file: os.PathLike):
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

    def transform(self, candidate: Candidate, file: os.PathLike):
        pass


class MutationTransformer(Transformer):
    def __init__(self):
        self.mutator = None
        self.files = set()

    def transform_dir(self, candidate: Candidate, dst: os.PathLike):
        if not isinstance(candidate, GeneticCandidate):
            raise TypeError("Candidate must be of type GeneticCandidate")
        self.mutator = Mutator(candidate.statements, candidate.mutations)
        self.files = {candidate.files[i] for i in self.mutator.get_mutation_indices()}
        super().transform_dir(candidate, dst)

    def need_to_transform(self, candidate: Candidate, file: os.PathLike) -> bool:
        return file in self.files

    def transform(self, candidate: Candidate, file: os.PathLike):
        tree = self.mutator.mutate(candidate.trees[file])
        with open(file, "w") as fp:
            fp.write(ast.unparse(tree))
