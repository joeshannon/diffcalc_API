"""API examples used in diffcalc_api.routes.ub."""


from diffcalc_api.models.ub import (
    AddOrientationParams,
    AddReflectionParams,
    EditOrientationParams,
    EditReflectionParams,
    HklModel,
    PositionModel,
    SetLatticeParams,
    XyzModel,
)

add_reflection: AddReflectionParams = AddReflectionParams(
    **{
        "hkl": HklModel(h=0, k=0, l=1),
        "position": PositionModel(mu=7.31, delta=0.0, nu=10.62, eta=0, chi=0.0, phi=0),
        "energy": 12.39842,
    }
)

edit_reflection: EditReflectionParams = EditReflectionParams(
    **{"energy": 12.45, "set_tag": "refl2"}
)

add_orientation: AddOrientationParams = AddOrientationParams(
    **{
        "hkl": HklModel(h=0, k=1, l=0),
        "xyz": XyzModel(x=0, y=1, z=0),
    }
)

edit_orientation: EditOrientationParams = EditOrientationParams(
    **{
        "hkl": HklModel(h=0, k=1, l=0),
    }
)

set_lattice: SetLatticeParams = SetLatticeParams(**{"a": 4.913, "c": 5.405})
