# Copyright 2026 FlagOS Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
import torch

import flaggems_vllm

from . import accuracy_utils as utils


@pytest.mark.mul
@pytest.mark.parametrize("shape", utils.POINTWISE_SHAPES)
@pytest.mark.parametrize("dtype", utils.FLOAT_DTYPES)
def test_mul_tensor_tensor(shape, dtype):
    inp1 = torch.randn(shape, dtype=dtype, device=flaggems_vllm.device)
    inp2 = torch.randn(shape, dtype=dtype, device=flaggems_vllm.device)
    ref_inp1 = utils.to_reference(inp1, True)
    ref_inp2 = utils.to_reference(inp2, True)

    ref_out = torch.mul(ref_inp1, ref_inp2)
    with flaggems_vllm.use_gems():
        res_out = torch.mul(inp1, inp2)

    utils.gems_assert_close(res_out, ref_out, dtype)


@pytest.mark.mul
@pytest.mark.parametrize("shape", utils.POINTWISE_SHAPES)
@pytest.mark.parametrize("scalar", utils.SCALARS)
@pytest.mark.parametrize("dtype", utils.FLOAT_DTYPES)
def test_mul_tensor_scalar(shape, scalar, dtype):
    inp = torch.randn(shape, dtype=dtype, device=flaggems_vllm.device)
    ref_inp = utils.to_reference(inp, True)

    ref_out = torch.mul(ref_inp, scalar)
    with flaggems_vllm.use_gems():
        res_out = torch.mul(inp, scalar)

    utils.gems_assert_close(res_out, ref_out, dtype)


@pytest.mark.mul
@pytest.mark.parametrize("shape", utils.POINTWISE_SHAPES)
@pytest.mark.parametrize("scalar", utils.SCALARS)
@pytest.mark.parametrize("dtype", utils.FLOAT_DTYPES)
def test_mul_scalar_tensor(shape, scalar, dtype):
    inp = torch.randn(shape, dtype=dtype, device=flaggems_vllm.device)
    ref_inp = utils.to_reference(inp, True)

    ref_out = torch.mul(scalar, ref_inp)
    with flaggems_vllm.use_gems():
        res_out = torch.mul(scalar, inp)

    utils.gems_assert_close(res_out, ref_out, dtype)


@pytest.mark.mul
@pytest.mark.parametrize(
    "shape_a, shape_b",
    [
        ((10, 1), (1, 5)),
        ((3, 1, 5), (1, 4, 1)),
        ((0, 1), (1, 5)),
    ],
)
@pytest.mark.parametrize("dtype", utils.FLOAT_DTYPES)
def test_mul_broadcast(shape_a, shape_b, dtype):
    inp1 = torch.randn(shape_a, dtype=dtype, device=flaggems_vllm.device)
    inp2 = torch.randn(shape_b, dtype=dtype, device=flaggems_vllm.device)
    ref_inp1 = utils.to_reference(inp1, True)
    ref_inp2 = utils.to_reference(inp2, True)

    ref_out = torch.mul(ref_inp1, ref_inp2)
    with flaggems_vllm.use_gems():
        res_out = torch.mul(inp1, inp2)

    assert res_out.shape == ref_out.shape
    utils.gems_assert_close(res_out, ref_out, dtype)


@pytest.mark.mul
@pytest.mark.parametrize("shape", utils.POINTWISE_SHAPES)
@pytest.mark.parametrize("dtype", utils.FLOAT_DTYPES)
def test_mul_tensor_tensor_inplace(shape, dtype):
    inp1 = torch.randn(shape, dtype=dtype, device=flaggems_vllm.device)
    inp2 = torch.randn(shape, dtype=dtype, device=flaggems_vllm.device)
    ref_inp1 = utils.to_reference(inp1.clone(), True)
    ref_inp2 = utils.to_reference(inp2, True)

    ref_out = ref_inp1.mul_(ref_inp2)
    with flaggems_vllm.use_gems():
        res_out = inp1.mul_(inp2)

    assert res_out.data_ptr() == inp1.data_ptr()
    utils.gems_assert_close(res_out, ref_out, dtype)


@pytest.mark.mul
@pytest.mark.parametrize("shape", utils.POINTWISE_SHAPES)
@pytest.mark.parametrize("scalar", utils.SCALARS)
@pytest.mark.parametrize("dtype", utils.FLOAT_DTYPES)
def test_mul_tensor_scalar_inplace(shape, scalar, dtype):
    inp = torch.randn(shape, dtype=dtype, device=flaggems_vllm.device)
    ref_inp = utils.to_reference(inp.clone(), True)

    ref_out = ref_inp.mul_(scalar)
    with flaggems_vllm.use_gems():
        res_out = inp.mul_(scalar)

    assert res_out.data_ptr() == inp.data_ptr()
    utils.gems_assert_close(res_out, ref_out, dtype)


@pytest.mark.mul
@pytest.mark.parametrize("shape", utils.POINTWISE_SHAPES)
def test_mul_complex(shape):
    inp1 = torch.randn(shape, dtype=torch.complex64, device=flaggems_vllm.device)
    inp2 = torch.randn(shape, dtype=torch.complex64, device=flaggems_vllm.device)
    ref_inp1 = utils.to_reference(inp1, True)
    ref_inp2 = utils.to_reference(inp2, True)

    ref_out = torch.mul(ref_inp1, ref_inp2)
    with flaggems_vllm.use_gems():
        res_out = torch.mul(inp1, inp2)

    utils.gems_assert_close(res_out, ref_out, torch.complex64)
