[English|[中文版](./README_cn.md)]

## Introduction

FlagGems-vllm is part of [FlagOS](https://flagos.io/).
FlagGems-vllm is a high-performance operator library designed for multiple hardware backends. It provides optimized implementations of common vLLM operators and supports high-performance inference and deployment for a variety of widely used models.

FlagGems-vllm is a high-performance deep learning operator library implemented using the [Triton programming language](https://github.com/openai/triton) launched by OpenAI.

## Features

- Operators have undergone deep performance tuning
- Triton kernel call optimization
- Flexible multi-backend support mechanism
- Support for common vllm operators (moe_align_block_size, etc.)

## Quick Installation
### Install Dependencies
```shell
pip install -U scikit-build-core>=0.11 pybind11 ninja cmake
```
### Install FlagGems-vllm
```shell
git clone https://github.com/flagos-ai/FlagGems-vllm.git
cd FlagGems-vllm
pip install  .
```

## Usage Example

```python
import torch
import flaggems_vllm

# Create a tensor
x = torch.randn(1024, device='cuda')

# Apply ReLU activation
y = flaggems_vllm.ops.relu(x)
```

## Tests and Benchmark Quick Start

The following commands are verified in this repository and can be used for quick validation after installation.

### Run tests

```shell
cd /workspace/FlagGems-vllm
pytest -q tests --collect-only
pytest -q tests/test_outer.py --quick
```

### Run benchmark

```shell
cd /workspace/FlagGems-vllm
pytest -q benchmark --collect-only
pytest -q benchmark/test_outer.py::test_outer --level core --iter 1 --warmup 1
```

### Notes

- Most tests/benchmarks require a CUDA-capable GPU runtime.
- `--collect-only` is recommended first to quickly check import and discovery.

This project is licensed under the [Apache (version 2.0) License](./LICENSE).
