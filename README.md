# FixKit

[![Python Version](https://img.shields.io/pypi/pyversions/fixkit)](https://pypi.org/project/fixkit/)
[![GitHub release](https://img.shields.io/github/v/release/smythi93/fixkit)](https://img.shields.io/github/v/release/smythi93/fixkit)
[![PyPI](https://img.shields.io/pypi/v/fixkit)](https://pypi.org/project/fixkit/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/smythi93/fixkit/test-fixkit.yml?branch=main)](https://img.shields.io/github/actions/workflow/status/smythi93/fixkit/test-fixkit.yml?branch=main)
[![Coverage Status](https://coveralls.io/repos/github/smythi93/fixkit/badge.svg?branch=main)](https://coveralls.io/github/smythi93/fixkit?branch=main)
[![Licence](https://img.shields.io/github/license/smythi93/fixkit)](https://img.shields.io/github/license/smythi93/fixkit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

FixKit is a collection of various automated program repair approaches and techniques. 
It is designed to be a flexible and extensible framework for experimenting with different repair strategies. 
The framework is written in Python for Python and is designed to be easy to use and extend.

## Installation

To install FixKit, simply get the package from PyPI:

```bash
pip install fixkit
```

To install the latest version from the repository, use:

```bash
pip install git+https://github.com/smythi93/fixkit.git
```

## Usage

FixKit is a library and can be used directly in your Python code.

```python
from fixkit.repair.pygenprog import PyGenProg
from fixkit.localization.coverage import CoverageLocalization

repair = PyGenProg.from_source(
  src= "subjects/middle",
  excludes=["tests.py"],
  localization=CoverageLocalization(
    "subjects/middle",
    cov="middle",
    metric="Ochiai",
    tests=["tests.py"],
  ),
  population_size=40,
  max_generations=10,
)
patches = repair.repair()
```

## Components

Individual components can be swapped out and replaced with custom implementations.
The following components are currently available:

- **Fault Localization**: Determines the location of the fault in the source code.
- **Repair Approach**: Generates patches to fix the fault in the source code.
- **Search Strategy**: Searches for patches in the search space.
- **Fitness Function**: Evaluates the fitness of patches based on a given metric.
- **Selection Strategy**: Selects patches for the next generation based on their fitness.
- **Crossover Strategy**: Combines patches to create new patches.
- **Mutation Operators**: Mutates patches to create new patches.
- **Minimization Strategy**: Minimizes patches to reduce their size.

