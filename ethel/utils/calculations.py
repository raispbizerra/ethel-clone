from typing import Any, TypeVar
from numpy.typing import NDArray


def partial_ampleness(axis_of_rotation: NDArray[Any]) -> Any:
    return axis_of_rotation.max() - axis_of_rotation.min()
