import math

import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.data_structures.probabalistic.at_bloom_filter import (
    ATBloomFilter,
    ATScalableBloomFilter,
)


@st.composite
def bloom_filter_arguments(draw):
    input_data = draw(st.lists(st.integers(min_value=1), min_size=5, max_size=100))
    m = draw(st.integers(min_value=1, max_value=1_000))
    k = draw(st.integers(min_value=1, max_value=m))
    check_data = draw(st.lists(st.integers(min_value=1), min_size=5, max_size=100))
    return (input_data, m, k, check_data)


@given(bloom_filter_arguments())
def test_input_data(args):
    # Given
    input_data, m, k, check_data = args

    bf = ATBloomFilter(m=m, k=k)
    for x in input_data:
        bf.add(x)

    # When
    for x in input_data:
        result = bf.prob_contains(x)

        # Then
        assert result


@given(bloom_filter_arguments())
def test_check_data_true(args):
    # Given
    input_data, m, k, check_data = args

    bf = ATBloomFilter(m=m, k=k)
    for x in input_data:
        bf.add(x)

    # When
    for x in check_data:
        if x in input_data:
            result = bf.prob_contains(x)

            # Then
            assert result


@given(bloom_filter_arguments())
def test_p_calculation(args):
    # Given
    input_data, m, k, check_data = args

    bf = ATBloomFilter(m=m, k=k)
    for x in input_data:
        bf.add(x)

    # When

    # Then
    if bf.n >= m:
        assert bf.p == 1
    else:
        assert bf.p == math.e ** (
            -(bf.m / (bf.n if bf.n > 0 else 1)) * (math.log(2) ** 2)
        )


@given(bloom_filter_arguments())
def test_n_calculation(args):
    # Given
    input_data, m, k, check_data = args

    bf = ATBloomFilter(m=m, k=k)
    for x in input_data:
        bf.add(x)

    # When

    # Then
    assert bf.n == len(input_data)


def test_invalid_input_k_m():
    # Given
    m = None
    k = None

    # When

    # Then
    with pytest.raises(ValueError):
        _ = ATBloomFilter(m=m, k=k)


@given(bloom_filter_arguments())
def test_scalable_bf(args):
    # Given
    input_data, m, k, check_data = args

    bf = ATScalableBloomFilter(m=m, k=k, desired_p=0.001)
    for x in input_data:
        bf.add(x)

    # When
    for x in input_data:
        result = bf.prob_contains(x)

        # Then
        assert result
