import os
from pathlib import Path
from queue import Queue, Empty
from threading import Thread
from typing import List

from pyrep.candidate import GeneticCandidate
from pyrep.constants import DEFAULT_WORK_DIR
from pyrep.fitness.metric import Fitness
from pyrep.transform import MutationTransformer


class Worker:
    def __init__(self, identifier: str, out: os.PathLike = None):
        self.identifier = identifier
        self.out = Path(out or DEFAULT_WORK_DIR)
        self.cwd = self.out / identifier
        self.transformer = MutationTransformer()

    def evaluate(self, candidate: GeneticCandidate, fitness: Fitness):
        self.transformer.transform_dir(candidate, self.cwd)
        candidate.fitness = fitness.fitness(self.cwd)

    def run(self, candidates: Queue, fitness: Fitness):
        try:
            while True:
                self.evaluate(candidates.get_nowait(), fitness)
        except Empty:
            pass


class Engine:
    def __init__(
        self,
        fitness: Fitness,
        workers: int = 1,
        out: os.PathLike = None,
    ):
        self.fitness = fitness
        self.out = Path(out or DEFAULT_WORK_DIR)
        self.workers = [Worker(f"rep_{i}", self.out) for i in range(workers)]

    def evaluate(self, candidates=List[GeneticCandidate]):
        threads = []
        data = Queue()
        for candidate in candidates:
            data.put(candidate)
        for worker in self.workers:
            thread = Thread(target=worker.run, args=(data, self.fitness))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
