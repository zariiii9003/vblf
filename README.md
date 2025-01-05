# Binary Logging Format Library for Python

[![PyPI - Version](https://img.shields.io/pypi/v/blf.svg)](https://pypi.org/project/blf)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/blf.svg)](https://pypi.org/project/blf)

## Introduction

A Python library for reading and writing BLF files, a proprietary binary logging format of Vector Informatik GmbH. BLF files are commonly used in automotive logging and testing scenarios.

## Installation

```bash
pip install blf
```

## Usage

### Reading BLF Files

```python
from blf.can import CanMessage, CanMessage2
from blf.reader import BlfReader

# Open a BLF file
with BlfReader("example.blf") as reader:
    # Iterate through all objects in the file
    for obj in reader:
        print(f"Type: {obj.header.base.object_type.name}")
        print(f"Timestamp: {obj.header.object_time_stamp}")

        # Handle CAN messages
        if isinstance(obj, (CanMessage, CanMessage2))
            print(f"CAN ID: {obj.id}")
            print(f"Data: {obj.data.hex()}")
```

### Writing BLF Files

```python
from blf.can import CanMessage
from blf.writer import BlfWriter

# Create a new BLF file
with BlfWriter("output.blf") as writer:
    # Create a CAN message
    msg = CanMessage(...)

    # Write the message to the file
    writer.write(msg)
```

## License

This project is licensed under the MIT License.

## Acknowledgments

- Vector Informatik GmbH for the BLF file format
- Tobias Lorenz for his C++ library [vector_blf](https://bitbucket.org/tobylorenz/vector_blf/src/master/)
