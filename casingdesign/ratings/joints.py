"""API connection joint strength per API TR 5C3 §5 (ISO 10400 §10).

Round thread (STC/LTC): minimum of fracture and jump-out strength.
    Ajp = pi/4 [(D - 0.1425)^2 - d^2]       area under the last perfect thread
    P_fracture = 0.95 Ajp Up
    P_jumpout  = 0.95 Ajp L [ 0.74 D^-0.59 Up / (0.5 L + 0.14 D) + Yp / (L + 0.14 D) ]
    L = engaged thread length (in), from API 5B thread dimensions.

Buttress (BTC): minimum of pipe-thread strength and coupling strength.
    P_pipe     = 0.95 Ap Up [1.008 - 0.0396 (1.083 - Yp/Up) D]
    P_coupling = 0.95 Ac Uc   (coupling area x coupling tensile; same grade assumed)

Units: in, psi, lbf. Up = minimum ultimate tensile strength, Yp = minimum yield.
"""
from __future__ import annotations

import math

from .api5c3 import PipeGeometry

# API Spec 5CT Table E.28 regular buttress coupling OD W (in). Special-clearance
# couplings (smaller OD, lower strength) are not modelled; pass coupling_od explicitly.
BTC_COUPLING_OD = {
    4.5: 5.250, 5.0: 5.800, 5.5: 6.300, 6.625: 7.390, 7.0: 7.875, 7.625: 8.500,
    8.625: 9.625, 9.625: 10.625, 10.75: 11.750, 11.75: 12.750, 13.375: 14.375,
    16.0: 17.000, 18.625: 20.000, 20.0: 21.000,
}


def round_thread_joint_strength(geom: PipeGeometry, yp: float, up: float,
                                engaged_length: float) -> float:
    d_nom = geom.od
    ajp = math.pi / 4.0 * ((d_nom - 0.1425) ** 2 - geom.id**2)
    fracture = 0.95 * ajp * up
    L = engaged_length
    jumpout = 0.95 * ajp * L * (
        0.74 * d_nom**-0.59 * up / (0.5 * L + 0.14 * d_nom) + yp / (L + 0.14 * d_nom)
    )
    return min(fracture, jumpout)


def buttress_joint_strength(geom: PipeGeometry, yp: float, up: float,
                            coupling_od: float | None = None,
                            coupling_yp: float | None = None,
                            coupling_up: float | None = None) -> float:
    pipe = 0.95 * geom.area * up * (1.008 - 0.0396 * (1.083 - yp / up) * geom.od)
    if coupling_od is None:
        coupling_od = BTC_COUPLING_OD.get(geom.od)
    if coupling_od is None:
        return pipe
    # Coupling bore equals pipe OD at the thread; area of the coupling wall.
    ac = math.pi / 4.0 * (coupling_od**2 - geom.od**2)
    coupling = 0.95 * ac * (coupling_up or up)
    return min(pipe, coupling)
