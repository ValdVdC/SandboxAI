"""Tests for celery tasks and semantic evaluation."""

import numpy as np
import pytest

from app.workers.tasks import cosine_similarity


class TestSemanticValidation:
    """Test semantic validation logic."""

    def test_cosine_similarity_identical(self):
        """Test cosine similarity with identical vectors."""
        vec1 = np.array([1.0, 2.0, 3.0])
        vec2 = np.array([1.0, 2.0, 3.0])
        score = cosine_similarity(vec1, vec2)
        assert score == pytest.approx(1.0)

    def test_cosine_similarity_orthogonal(self):
        """Test cosine similarity with orthogonal vectors."""
        vec1 = np.array([1.0, 0.0])
        vec2 = np.array([0.0, 1.0])
        score = cosine_similarity(vec1, vec2)
        assert score == pytest.approx(0.0)

    def test_cosine_similarity_opposite(self):
        """Test cosine similarity with opposite vectors."""
        vec1 = np.array([1.0, 2.0])
        vec2 = np.array([-1.0, -2.0])
        score = cosine_similarity(vec1, vec2)
        assert score == pytest.approx(-1.0)

    def test_cosine_similarity_zero_vector(self):
        """Test cosine similarity when one vector is zero."""
        vec1 = np.array([0.0, 0.0])
        vec2 = np.array([1.0, 1.0])
        score = cosine_similarity(vec1, vec2)
        assert score == 0.0

    def test_cosine_similarity_partial(self):
        """Test cosine similarity with partial match."""
        vec1 = np.array([1.0, 1.0, 0.0])
        vec2 = np.array([1.0, 1.0, 1.0])
        score = cosine_similarity(vec1, vec2)
        assert 0.0 < score < 1.0
