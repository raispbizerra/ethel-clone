import numpy as np
from ethel.utils.calculations import partial_ampleness


def test_partial_ampleness() -> None:
    assert partial_ampleness(np.arange(3)) == 2
