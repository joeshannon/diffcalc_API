from diffcalc_API.models.ub import (
    AddOrientationParams,
    AddReflectionParams,
    EditOrientationParams,
    EditReflectionParams,
    SetLatticeParams,
)

add_reflection: AddReflectionParams = AddReflectionParams(
    **{
        "hkl": [0, 0, 1],
        "position": [7.31, 0.0, 10.62, 0, 0.0, 0],
        "energy": 12.39842,
        "tag": "refl1",
    }
)

edit_reflection: EditReflectionParams = EditReflectionParams(
    **{"energy": 12.45, "tag_or_idx": "refl1"}
)

add_orientation: AddOrientationParams = AddOrientationParams(
    **{
        "hkl": [0, 1, 0],
        "xyz": [0, 1, 0],
        "tag": "plane",
    }
)

edit_orientation: EditOrientationParams = EditOrientationParams(
    **{
        "hkl": (0, 1, 0),
        "tag_or_idx": "plane",
    }
)

set_lattice: SetLatticeParams = SetLatticeParams(**{"a": 4.913, "c": 5.405})
