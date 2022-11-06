from typing import Any

from numpy.typing import NDArray


def partial_ampleness(axis_of_rotation: NDArray[Any]) -> Any:
    """Calculate the ampleness of a given axis of rotation."""
    return axis_of_rotation.max() - axis_of_rotation.min()
