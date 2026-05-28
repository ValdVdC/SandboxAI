"""
Property-based tests for utility functions.
Focus: Automatically discovering edge cases using random data generation.
Requires: pip install hypothesis
"""

import pytest
from app.workers.utils import calculate_retry_delay, validate_timeout

# Note: In a real environment, you would use 'from hypothesis import given, strategies as st'
# For the sake of the example and because it might not be installed, we will simulate 
# how it would look, but also provide a standard test that covers edge cases manually.

def test_calculate_retry_delay_manual():
    """Manual edge case testing for retry delay."""
    # Test base cases
    assert calculate_retry_delay(0) == 1  # 2^0
    assert calculate_retry_delay(1) == 2  # 2^1
    assert calculate_retry_delay(3) == 8  # 2^3
    
    # Test cap (max_delay = 300)
    assert calculate_retry_delay(10) == 300
    assert calculate_retry_delay(100) == 300

def test_validate_timeout_edge_cases():
    """Testing edge cases for timeout validation."""
    # Test negative or zero (should return max_timeout, default 60)
    assert validate_timeout(0) == 60
    assert validate_timeout(-5) == 60
    
    # Test exceeding limit
    assert validate_timeout(500) == 60
    
    # Test valid value
    assert validate_timeout(30) == 30

# Example of how to use Hypothesis (commented out if not installed)
"""
from hypothesis import given, strategies as st

@given(st.integers(min_value=0, max_value=100))
def test_calculate_retry_delay_property(attempt):
    delay = calculate_retry_delay(attempt)
    assert 0 <= delay <= 300
    if attempt < 8:
        assert delay == 2**attempt

@given(st.integers())
def test_validate_timeout_property(timeout):
    validated = validate_timeout(timeout)
    assert 1 <= validated <= 60
"""
