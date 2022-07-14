from diffcalc_API.models.UBCalculation import (
    addOrientationParams,
    addReflectionParams,
    editOrientationParams,
    editReflectionParams,
    setLatticeParams,
)

addReflection: addReflectionParams = addReflectionParams(
    **{
        "hkl": [0, 0, 1],
        "position": [7.31, 0.0, 10.62, 0, 0.0, 0],
        "energy": 12.39842,
        "tag": "refl1",
    }
)

editReflection: editReflectionParams = editReflectionParams(
    **{"energy": 12.45, "tagOrIdx": "refl1"}
)

addOrientation: addOrientationParams = addOrientationParams(
    **{
        "hkl": [0, 1, 0],
        "xyz": [0, 1, 0],
        "tag": "plane",
    }
)

editOrientation: editOrientationParams = editOrientationParams(
    **{
        "hkl": (0, 1, 0),
        "tagOrIdx": "plane",
    }
)

setLattice: setLatticeParams = setLatticeParams(**{"a": 4.913, "c": 5.405})
