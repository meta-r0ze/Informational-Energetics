#!python3
from dataclasses import dataclass
from decimal import getcontext

getcontext().prec = 5000

@dataclass
class MeasuredVal:
    value: float
    uncertainty: float
    decimals: int    # Exact number of decimal places to print (Sig Figs)
    units: str
    citation: str

    @property
    def rel_precision(self):
        """Returns relative precision (e.g. 1e-5)"""
        if self.value == 0: return 0.0
        return abs(self.uncertainty / self.value)

PAPER1_REFS = {
    # paper 1
    "alpha_inv": MeasuredVal(
        137.035999177,
        0.000000021,
        9,
        "",
        "mohr_codata_2025"
    ),
    "alpha_inv_morel": MeasuredVal(
        137.035999206,
        0.000000011,
        9,
        "",
        "morel_determination_2020"
    ),

    "alpha_inv_parker": MeasuredVal(
        137.035999046,
        0.000000027,
        9,
        "",
        "parker_measurement_2018"
    ),

    "alpha_inv_fan": MeasuredVal(
        137.035999166,
        0.000000015,
        9,
        "",
        "fan_measurement_2023"
    ),
    "me": MeasuredVal(
        0.51099895000,
        0.00000000015,
        11,
        "MeV",
        "mohr_codata_2025",
    ),
    "rk": MeasuredVal(
        25812.80745,
        0.00001,
        5,
        "\\Omega",
        "mohr_codata_2025"
    ),
}

PAPER3_REFS = {
    # Paper 3
    "Mp": MeasuredVal(
        1.22091e19,
        0.00001e19,
        5,
        "GeV",
        "mohr_codata_2025"
    ),

    # --- Electroweak & Higgs (PDG 2024) ---
    "gf": MeasuredVal(
        1.1663788e-5,
        0.0000006e-5,
        7,
        "GeV^-2",
        "navas_review_2024"
    ),

    "mz": MeasuredVal(
        91.1876,
        0.0021,
        4,
        "GeV",
        "navas_review_2024"
    ),

    "mw": MeasuredVal(
        80.377,
        0.012,
        3,
        "GeV",
        "navas_review_2024"  # Global Fit
    ),

    # Specific W-Mass measurements for tension analysis
    "mw_cdf": MeasuredVal(
        80.4335,
        0.0094,
        4,
        "GeV",
        "cdf_collaboration_high-precision_2022"
    ),

    "mw_atlas": MeasuredVal(
        80.360,
        0.016,
        3,
        "GeV",
        "aaboud_improved_2023"
    ),

    "sin2_w": MeasuredVal(
        0.22291,
        0.00011,
        5,
        "",
        "navas_review_2024"
    ),

    "sin2_w_global": MeasuredVal(
        0.22354,
        0.00006,
        5,
        "",
        "navas_review_2024",
    ),

    "mh": MeasuredVal(
        125.20,
        0.11,
        2,
        "GeV",
        "navas_review_2024"
    ),

    # --- Strong Coupling (QCD) ---
    "alpha_s": MeasuredVal(
        0.1179,
        0.0009,
        4,
        "",
        "denterria_strong_2024"
    ),

    # --- Tau Scale Strong Coupling ---
    "alpha_s_tau": MeasuredVal(
        0.330,
        0.014,
        3,
        "",
        "navas_review_2024",
    ),

    # --- Flavor Physics (CKM) ---
    "vus": MeasuredVal(
        0.22500,
        0.00067,
        5,
        "",
        "navas_review_2024"
    ),

    "jarlskog": MeasuredVal(
        3.08e-5,
        0.15e-5,
        2,
        "",
        "navas_review_2024"
    ),

    # --- Running Constants & Background ---
    "alpha_inv_mz": MeasuredVal(
        127.955,
        0.010,
        3,
        "",
        "navas_review_2024"
    ),

    "delta_alpha_mz": MeasuredVal(
        0.0590,
        0.0001,
        4,
        "",
        "navas_review_2024"
    ),

    # --- Gravity ---
    "G_coupling": MeasuredVal(
        1.752e-45,
        0.001e-45,
        3,
        "",
        "mohr_codata_2025"
    ),

    # --- Derived Comparisons ---
    "vev": MeasuredVal(
        246.21965,
        0.00006,
        5,
        "GeV",
        "navas_review_2024"
    ),

    "lambda": MeasuredVal(
        0.129,
        0.005,
        3,
        "",
        "navas_review_2024"
    ),

    "ye_sm": MeasuredVal(
        2.935e-6,
        0.001e-6,
        3,
        "",
        "navas_review_2024"
    ),

    "vacuum_ratio": MeasuredVal(
        1.38e-123,
        0.20e-123, # Expanded to encompass the H0 / \Omega_\Lambda systematic tensions
        2,
        "",
        "navas_review_2024", # Use PDG/Cosmology review rather than just Planck
    ),

    "nc_color": MeasuredVal(
        3.0,
        0.0,
        0,
        "",
        "standard_model"
    ),
}
