"""
The transform module provides the necessary tools to transform a director to match a candidate.
"""

import abc
import ast
import os
import shutil
from pathlib import Path

from pyrep.candidate import Candidate, GeneticCandidate
from pyrep.genetic.operators import Mutator


class Transformer(abc.ABC):
    """
    Abstract class for transformation operators.
    """

    def transform_dir(self, candidate: Candidate, dst: os.PathLike):
        """
        Transform a directory to match a candidate.
        :param Candidate candidate: The candidate to match.
        :param os.PathLike dst: The destination directory to transform.
        """
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
            self.transform_file(candidate, Path(".."), dst)
        elif dst.is_dir():
            for directory, _, files in os.walk(dst):
                for file in files:
                    self.transform_file(candidate, dst, file)

    def transform_file(self, candidate: Candidate, dst: Path, file: os.PathLike):
        """
        Transform a file to match a candidate.
        :param Candidate candidate: The candidate to match.
        :param os.PathLike dst: The destination directory to transform.
        :param os.PathLike file: The file to transform.
        """
        if self.need_to_transform(candidate, file):
            self.transform(candidate, dst, file)

    def need_to_transform(self, candidate: Candidate, file: os.PathLike) -> bool:
        """
        Check if a file needs to be transformed.
        :param Candidate candidate: The candidate to match.
        :param os.PathLike file: The file to check.
        :return bool: True if the file needs to be transformed, False otherwise.
        """
        return False

    @abc.abstractmethod
    def transform(self, candidate: Candidate, dst: Path, file: os.PathLike):
        """
        Transform a file to match a candidate.
        :param Candidate candidate: The candidate to match.
        :param os.PathLike dst: The destination directory to transform.
        :param os.PathLike file: The file to transform.
        """
        pass

    @staticmethod
    def revert(candidate: Candidate, dst: os.PathLike, file: os.PathLike):
        """
        Revert a file to its original state.
        :param Candidate candidate: The candidate to revert.
        :param os.PathLike dst: The destination directory to revert.
        :param os.PathLike file: The file to revert.
        :return:
        """
        shutil.copy2(Path(candidate.src, file), Path(dst, file))


class CopyTransformer(Transformer):
    """
    Transformer that copies the source directory to the destination directory.
    """

    def transform_dir(self, candidate: Candidate, dst: os.PathLike):
        """
        Transform a directory to match a candidate by copying the source directory to the destination directory.
        :param Candidate candidate: The candidate to match.
        :param os.PathLike dst: The destination directory to transform.
        """
        src = Path(candidate.src)
        dst = Path(dst)
        if not dst.exists():
            if src.is_file():
                shutil.copy2(src, dst)
            elif src.is_dir():
                shutil.copytree(src, dst)
            else:
                raise IOError("Source must be a file or directory")

    def transform(self, candidate: Candidate, dst: Path, file: os.PathLike):
        pass


class MutationTransformer(Transformer):
    """
    Transformer that mutates the source directory to match a candidate.
    """

    def __init__(self):
        """
        Initialize the mutation transformer.
        """
        self.mutator = None
        self.files = set()

    def transform_dir(self, candidate: GeneticCandidate, dst: os.PathLike):
        """
        Transform a directory to match a candidate by mutating the source directory to the destination directory.
        :param GeneticCandidate candidate: The candidate to match.
        :param os.PathLike dst: The destination directory to transform.
        """
        if not isinstance(candidate, GeneticCandidate):
            raise TypeError("Candidate must be of type GeneticCandidate")
        self.mutator = Mutator(candidate.statements, candidate.mutations)
        last_files = self.files
        self.files = {candidate.files[i] for i in self.mutator.get_mutation_indices()}
        for file in last_files - self.files:
            self.revert(candidate, dst, file)
        super().transform_dir(candidate, dst)

    def need_to_transform(self, candidate: Candidate, file: os.PathLike) -> bool:
        """
        Check if a file needs to be transformed.
        :param Candidate candidate: The candidate to match.
        :param os.PathLike file: The file to check.
        :return bool: True if the file needs to be transformed, False otherwise.
        """
        return file in self.files

    def transform(self, candidate: Candidate, dst: Path, file: os.PathLike):
        """
        Transform a file to match a candidate by mutating the file.
        :param Candidate candidate: The candidate to match.
        :param os.PathLike dst: The destination directory to transform.
        :param os.PathLike file: The file to transform.
        """
        tree = self.mutator.mutate(candidate.trees[file])
        with open(dst / file, "w") as fp:
            fp.write(ast.unparse(tree))


__all__ = ["Transformer", "CopyTransformer", "MutationTransformer"]
