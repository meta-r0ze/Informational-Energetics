#!python3

import math
import argparse
import sys
from decimal import Decimal, getcontext

# ==========================================
# 0. EXTERNAL REFERENCE VALUES (Experimental Truth)
# ==========================================
# Sources: CODATA 2022 & PDG 2024
from dataclasses import dataclass
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
    
REFS = {
    # --- Fundamental Constants (CODATA 2022) ---
    "me": MeasuredVal(
        0.51099895000, 
        0.00000000015,
        11,
        "MeV", 
        "mohr_codata_2025",
    ),
    
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

    "rk": MeasuredVal(
        25812.80745,
        0.00001,
        5,
        "\\Omega",
        "mohr_codata_2025"
    ),

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

getcontext().prec = 5000
PI = math.pi

# ==========================================
# 1. HELPER FUNCTIONS
# ==========================================

def format_float_latex(num, precision=9):
    """
    Formats a float as a simple decimal string, avoiding scientific notation 
    for numbers within the standard range (0.001 < x < 1000).
    """
    return f"{num:.{precision}f}".rstrip('0').rstrip('.')

def to_latex_sci(num, precision=4, unit=""):
    """Converts a float to LaTeX scientific notation."""
    if num == 0: return "0"
    exponent = int(math.floor(math.log10(abs(num))))
    mantissa = num / (10**exponent)
    
    # Standard range: Just return the number as a string
    if -3 <= exponent < 6:
        # Avoid unnecessary decimals for integers
        if abs(num - round(num)) < 1e-9:
            return f"{int(num)}"
        return f"{num:.{precision}f}".rstrip('0').rstrip('.')
    if unit != "":
        return f"{mantissa:.{precision}f}e{exponent}"
    return f"{mantissa:.{precision}f} \\cdot 10^{{{exponent}}}"

def to_latex_sci_with_err(val, err, precision=4):
    """
    Handles scientific notation for Value +/- Error pairs.
    Ensures both share the same exponent for clean LaTeX: (1.2 +/- 0.1) x 10^19
    """
    if val == 0: return f"0 \\pm {err}"
    exponent = int(math.floor(math.log10(abs(val))))
    
    # Normalize both by the main exponent
    mantissa_val = val / (10**exponent)
    mantissa_err = err / (10**exponent)
    
    return f"({mantissa_val:.{precision}f} \\pm {mantissa_err:.{precision}f}) \\cdot 10^{{{exponent}}}"

def print_section(title, latex_mode=False):
    if latex_mode: return
    print(f"\n{'#'*70}")
    print(f"  {title}")
    print(f"{'#'*70}\n")

def print_latex_value(tag, valueToPrint, unit):
    if 0.001 < abs(valueToPrint) < 1000:
        valueToPrintStr = format_float_latex(valueToPrint) 
    else:
        valueToPrintStr = to_latex_sci(valueToPrint, 8, unit)

    if unit != "":
        valueToPrintStr = f"\\qty{{{valueToPrintStr}}}{{{unit}}}"
    print(f"%<*{tag}>{valueToPrintStr}%</{tag}>")

def print_derivation(name, tag, formula_sym, latex_sym, formula_num, result,
                     latex_mode=False, ref_key=None,context="observed value",
                     formula_step1=None,
                     formula_step2=None):

    # Auto-detect unit from REFS if not provided
    unit = None
    if ref_key is not None:
        unit = REFS[ref_key].units    
    else:
        unit = ""

    # --- LATEX OUTPUT MODE ---
    if latex_mode:
        # 1. Step Value Tag (Optional intermediate calculation)
        if formula_step1 is not None:
            print_latex_value(tag+"StepOneVal", formula_step1, unit)
        if formula_step2 is not None:
            print_latex_value(tag+"StepTwoVal", formula_step2, unit)

        # 2. Geometric Value Tag (THEORY PREDICTION)
        # We DO NOT add +/- 0 here. Theoretical values are presented as exact numbers.
        print_latex_value(tag+"Val", result, unit)

        # 3. Formula Tag
        print(f"%<*{tag}Eq>{latex_sym}%</{tag}Eq>")

        # 4. Experimental Comparison logic
        if ref_key and ref_key in REFS:
            ref_obj = REFS[ref_key]
            target = ref_obj.value
            err_val = ref_obj.uncertainty
            
            # Extract Citation
            cite_key = getattr(ref_obj, 'citation', None)
            cite_str = f"~\\cite{{{cite_key}}}" if cite_key else ""

            # Calculate Sigma
            diff = result - target
            sigma = 0.0
            if err_val > 0:
                sigma = diff / err_val

            # --- EXPERIMENTAL VALUE TAG GENERATION ---
            
            # Case A: Standard Float
            if 0.001 < abs(target) < 100000:
                 # Use the decimals field to rigidly enforce sig figs (preserves trailing zeros)
                 t_str = f"{target:.{ref_obj.decimals}f}"
                 e_str = f"{err_val:.{ref_obj.decimals}f}"
                 out_str = f"\\qty{{{t_str} \\pm {e_str}}}{{{unit}}}{cite_str}"
                 print(f"%<*{tag}ExperimentalValue>{out_str}%</{tag}ExperimentalValue>")
            # Case B: Scientific Notation
            else:
                 # Pass ref_obj.decimals to format the mantissa correctly
                 exp_str = to_latex_sci_with_err(target, err_val, ref_obj.decimals)
                 if unit:
                     out_str = f"${exp_str}$ \\unit{{{unit}}}{cite_str}"
                 else:
                     out_str = f"${exp_str}${cite_str}"
                 print(f"%<*{tag}ExperimentalValue>{out_str}%</{tag}ExperimentalValue>")

            # Accuracy Sentence Logic
            abs_sigma = abs(sigma)
            if abs_sigma < 1.0:
                acc_text = f"The geometric derivation matches the experimental value to within ${abs_sigma:.2f}\\sigma$."
            elif abs_sigma < 3.0:
                acc_text = f"The geometric prediction lies within ${abs_sigma:.2f}\\sigma$ of the {context}."
            else:
                acc_text = f"The geometric prediction deviates by ${abs_sigma:.2f}\\sigma$ from the {context}, suggesting higher-order corrections may be required."
            
            print(f"%<*{tag}AccText>{acc_text}%</{tag}AccText>")
            print(f"%<*{tag}Diff>{to_latex_sci(diff, 3)}%</{tag}Diff>")
            print(f"%<*{tag}Sigma>{sigma:.2f}%</{tag}Sigma>")

        print("") # Spacer in tex file
        return

    # --- HUMAN READABLE MODE ---
    print(f"--- {name} ---")
    print(f"Formula:  {formula_sym}")
    print(f"Filled:   {formula_num}")
    print(f"Calculated: {result:.12g} {unit}")

    # LaTeX Snippet hint
    latex_str = to_latex_sci(result, 5) if abs(result) < 0.001 or abs(result) > 1000 else f"{result:.5f}"
    # print(f"LaTeX Copy: \\mathbf{{{latex_str}}} {unit}")

    if ref_key and ref_key in REFS:
        target = REFS[ref_key].value
        err_val = REFS[ref_key].uncertainty
        diff = result - target
        
        print(f"Target:     {target:.12g} +/- {err_val:.2g} {unit}")
        
        if err_val > 0:
            sigma = diff / err_val
            sigma_str = f"{sigma:+.2f}σ"
            
            # Range check for console output
            if abs(sigma) > 3.0:
                print(f"Deviation:  {sigma_str}  [WARNING: >3σ deviation]")
            else:
                print(f"Deviation:  {sigma_str}  [OK]")
        else:
            pct_err = (diff / target) * 100
            print(f"Error:      {pct_err:.6f}% (No Sigma avail)")

    print("")

def run_global_audit(results_dict, refs, latex_mode=False):
    # --- TIER 1: BOSONIC STRUCTURE ---
    tier1_checklist = [
        ("AlphaInv",    "alpha_inv", "Alpha^-1"),
        ("FermiConst",  "gf",        "G_Fermi"),
        ("WBosonMass",  "mw",        "Mass W"),
        ("AlphaS",      "alpha_s",   "Alpha Strong"),
        ("HiggsMass",   "mh",        "Mass Higgs"),
    ]

    # --- TIER 2: SPECTRUM & FLAVOR ---
    tier2_checklist = [
        ("WeakAngle",    "sin2_w",   "Sin^2 ThetaW"),
        ("CabibboAngle", "vus",      "Cabibbo Vus"),
        ("Jarlskog",     "jarlskog", "Jarlskog J"),
        ("PlanckMass",   "Mp",       "Planck Mass"),
        ("VonKlitzing",  "rk",       "Von Klitzing Const")
    ]

    run_global_audit_tier(results_dict, refs, tier1_checklist, latex_mode, "bosonic")
    run_global_audit_tier(results_dict, refs, tier2_checklist, latex_mode, "spectrum")
    run_global_audit_tier(results_dict, refs, tier1_checklist + tier2_checklist, latex_mode, "combined")


def run_global_audit_tier(results_dict, refs, checklist, latex_mode, name=""):
    """
    Performs Chi-Squared Audit using MeasuredVal objects.
    Outputs in a vertical, human-readable list format for precise digit comparison.
    """
    if not latex_mode:
        print("\n" + "="*60)
        print(f"{'GLOBAL GEOMETRIC AUDIT':^60}")
        print("="*60)

    total_chi2 = 0.0
    dof = 0
    
    for calc_key, ref_key, display in checklist:
        if calc_key in results_dict and ref_key in refs:
            # 1. Get the data objects
            calc_val = results_dict[calc_key]
            ref = refs[ref_key] 
            
            # 2. Calculate Stats
            diff = calc_val - ref.value
            sigma = diff / ref.uncertainty
            chi2 = sigma ** 2
            
            # 3. Determine Format based on magnitude
            # Use scientific for very small/large numbers, fixed for human scales
            # ensuring we show enough digits to see the difference.
            if abs(ref.value) < 1e-2 or abs(ref.value) > 1e4:
                fmt = ".9e"
                err_fmt = ".1e"
            else:
                fmt = ".9f"
                err_fmt = ".8f"
            
            if not latex_mode:
                # 4. Print Block
                print(f"[{display}]")
                print(f"  Experimental: {ref.value:{fmt}} +/- {ref.uncertainty:{err_fmt}}")
                print(f"  Geometric:    {calc_val:{fmt}}")
                # Source and Unit line
                src_str = f"({ref.citation})"
                print(f"  Citation:     {ref.units:<6} {src_str}")
                print(f"  Deviation:    {sigma:+.2f} sigma")
                print(f"  Chi^2:        {chi2:.4f}")
                print("-" * 60)
            
            total_chi2 += chi2
            dof += 1

    if not latex_mode:            
        print("=" * 60)
        print(f"TOTAL CHI^2:   {total_chi2:.4f}")
        print(f"DOF:           {dof}")
        print(f"REDUCED CHI^2: {total_chi2/dof:.4f}")
    
        if total_chi2 < 25.0:
            print(">>> STATUS: VALIDATED (Theory matches Experiment)")
        else:
            print(">>> STATUS: TENSION DETECTED")
        print("="*60 + "\n")
    else:
        tag=name+"totalchi"
        print(f"%<*{tag}Val>{total_chi2:.4f}%</{tag}Val>")
        tag=name+"reducedchi"
        print(f"%<*{tag}Val>{total_chi2/dof:.4f}%</{tag}Val>")

def main():
    parser = argparse.ArgumentParser(description="Calculate E8 Persistence Constants")
    parser.add_argument('--latex', action='store_true', help='Output in catchfilebetweentags format')
    args = parser.parse_args()

    LATEX_MODE = args.latex
    
    # ==========================================
    # 2. Experimental
    # ==========================================
    if LATEX_MODE:
        # Output basic experimental values as tags too if needed
        me = REFS['me'].value
        print(f"%<*MeMeV>{me}%</MeMeVPrint>")
        print(f"%<*MeMeVPrint>{me}%</MeMeVPrint>")
        print("")

    # ==========================================
    # 2. SYSTEM I: INVARIANTS
    # ==========================================
    print_section("SYSTEM I: THE INVARIANT SUBSTRATE", LATEX_MODE)

    D     = 4
    DELTA = 43
    SIGMA = 5
    NU    = 16
    CHI   = 2

    if not LATEX_MODE:
        print(f"Invariants: S = {{ D={D}, Delta={DELTA}, Sigma={SIGMA}, Nu={NU}, Chi={CHI} }}")

    # Derived Loads
    L_INTRINSIC = NU + SIGMA + CHI
    L_EMBED = L_INTRINSIC + (2 * D)
    L_SUBSTRATE = (DELTA * D) + NU
    N = 2 * NU
    R_M = D * DELTA

    # --- Universal Manifold Friction ---
    # Any integer capacity (N) projected onto the spacetime manifold (D*Delta)
    # experiences a texture loss/friction defined by the inverse volume.
    COORDINATE_OVERHEAD = 1.0 - (1.0 / (D * DELTA)) # ~0.99

    if LATEX_MODE:
        # Output basic invariants as tags
        print(f"%<*InvLIntrinsic>{L_INTRINSIC}%</InvLIntrinsic>")
        print(f"%<*InvLEmbed>{L_EMBED}%</InvLEmbed>")
        print(f"%<*InvLSubstrate>{L_SUBSTRATE}%</InvLSubstrate>")
        print(f"%<*InvN>{N}%</InvN>")
        print(f"%<*InvRM>{R_M}%</InvRM>")
        print(f"%<*InvCoordinateOverhead>{COORDINATE_OVERHEAD}%</InvCoordinateOverhead>")
    elif not LATEX_MODE:
        print(f"Capacities: L_INTRINSIC={L_INTRINSIC}, L_EMBED={L_EMBED}, N={N}, RM={R_M}")

    # ==========================================
    # 3. SYSTEM II: THE VACUUM IMPEDANCE
    # ==========================================
    print_section("SYSTEM II: THE GEOMETRIC IMPEDANCE (Table II Audit)", LATEX_MODE)

    comp_CAP = PI * DELTA
    comp_MAP = CHI
    comp_PRO = -1 / ((D * DELTA) - SIGMA)
    comp_GOV = -(CHI / DELTA)
    comp_TOL = (CHI * (R_M - SIGMA)) / (pow(N, 3) * SIGMA * R_M)
    comp_MAR = 1 / (L_EMBED * (SIGMA + 1) * pow(DELTA, 2))
    # Summation
    ALPHA_INV_GEO = comp_CAP + comp_MAP + comp_PRO + comp_GOV + comp_TOL + comp_MAR
    ALPHA_GEO = 1.0 / ALPHA_INV_GEO

    # Table breakdown for human mode
    if not LATEX_MODE:
        print(f"{'COMPONENT':<25} | {'FORMULA':<25} | {'VALUE':<15}")
        print("-" * 70)
        print(f"{'Capacity':<25} | {'π * Δ':<25} | {comp_CAP:+.8f}")
        print(f"{'Map':<25} | {'χ':<25} | {comp_MAP:+.8f}")
        print(f"{'Protocol':<25} | {'-1/(DΔ - σ)':<25} | {comp_PRO:+.8f}")
        print(f"{'Governor':<25} | {'-χ/Δ':<25} | {comp_GOV:+.8f}")
        print(f"{'Toll':<25} | {'Eq 16a':<25} | {comp_TOL:+.8e}")
        print(f"{'Margin':<25} | {'Eq 16b':<25} | {comp_MAR:+.8e}")
        print("-" * 70)
        print(f"{'TOTAL IMPEDANCE':<25} | {'SUM':<25} | {ALPHA_INV_GEO:.9f}")
        print("-" * 70)
        print("")
    else:
        # Export components for Table II generation
        print(f"%<*CompCAP>{comp_CAP:.5f}%</CompCAP>")
        print(f"%<*CompMAP>{comp_MAP:.5f}%</CompMAP>")
        print(f"%<*CompPRO>{comp_PRO:.5f}%</CompPRO>")
        print(f"%<*CompGOV>{comp_GOV:.5f}%</CompGOV>")
        print(f"%<*CompTOL>{to_latex_sci(comp_TOL)}%</CompTOL>")
        print(f"%<*CompMAR>{to_latex_sci(comp_MAR)}%</CompMAR>")
        print("")

    print_derivation(
        name="Fine Structure Constant Inverse",
        tag="AlphaInv",
        formula_sym="Sum(Components)",
        latex_sym=r"\pi\Delta + \chi - \frac{1}{D\Delta - \sigma} - \frac{\chi}{\Delta} + T + PM",
        formula_num="See Table",
        result=ALPHA_INV_GEO,
        latex_mode=LATEX_MODE,
        ref_key="alpha_inv"
    )
    print_derivation(
        name="Fine Structure Constant Inverse (morel)",
        tag="AlphaInvMorel",
        formula_sym="Sum(Components)",
        latex_sym=r"\pi\Delta + \chi - \frac{1}{D\Delta - \sigma} - \frac{\chi}{\Delta} + T + PM",
        formula_num="See Table",
        result=ALPHA_INV_GEO,
        latex_mode=LATEX_MODE,
        ref_key="alpha_inv_morel"
    )
    print_derivation(
        name="Fine Structure Constant Inverse (parker)",
        tag="AlphaInvParker",
        formula_sym="Sum(Components)",
        latex_sym=r"\pi\Delta + \chi - \frac{1}{D\Delta - \sigma} - \frac{\chi}{\Delta} + T + PM",
        formula_num="See Table",
        result=ALPHA_INV_GEO,
        latex_mode=LATEX_MODE,
        ref_key="alpha_inv_parker"
    )

    print_derivation(
        name="Fine Structure Constant Inverse (fan)",
        tag="AlphaInvFan",
        formula_sym="Sum(Components)",
        latex_sym=r"\pi\Delta + \chi - \frac{1}{D\Delta - \sigma} - \frac{\chi}{\Delta} + T + PM",
        formula_num="See Table",
        result=ALPHA_INV_GEO,
        latex_mode=LATEX_MODE,
        ref_key="alpha_inv_fan"
    )

    # --- Von Klitzing Constant (Quantum Resistance) ---
    Z0_SI = 4 * PI * (10**-7) * 299792458
    RK_GEO = Z0_SI / (2 * ALPHA_GEO)
    
    print_derivation(
        name="Von Klitzing Constant (R_K)",
        tag="VonKlitzing",
        formula_sym="Z_0 / 2α",
        latex_sym=r"\frac{Z_0}{2\alpha}",
        formula_num=f"{Z0_SI:.4f} / (2 * {ALPHA_GEO:.4e})",
        result=RK_GEO,
        latex_mode=LATEX_MODE,
        ref_key="rk",
        context="Quantum Hall resistance"
    )

    # --- Planck Charge Ratio & Vacuum Breakdown ---
    CHARGE_RATIO = 1.0 / math.sqrt(ALPHA_INV_GEO)  # e / q_P
    CHARGE_ATTENUATION = math.sqrt(ALPHA_INV_GEO)  # q_P / e
    CHARGE_RATIO_PCT = CHARGE_RATIO * 100.0

    print_derivation(
        name="Planck Charge Ratio (e/q_P)",
        tag="PlanckChargeRatio",
        formula_sym="1 / sqrt(Z_geo)",
        latex_sym=r"\frac{1}{\sqrt{Z_{geo}}}",
        formula_num=f"1 / sqrt({ALPHA_INV_GEO:.4f})",
        result=CHARGE_RATIO,
        latex_mode=LATEX_MODE
    )
    if LATEX_MODE:
        # Output tags specifically for the text formulation
        print(f"%<*ChargeAtten>{CHARGE_ATTENUATION:.1f}%</ChargeAtten>")
        print(f"%<*ChargeRatioPct>{CHARGE_RATIO_PCT:.1f}\\%%</ChargeRatioPct>")

    # ==========================================
    # 4. SYSTEM IV: THE GEOMETRIC CONTROL ARCHITECTURE
    # ==========================================
    print_section("SYSTEM IV: THE GEOMETRIC CONTROL ARCHITECTURE", LATEX_MODE)



    # --- Strong Coupling ---
    numerator_s = (NU*COORDINATE_OVERHEAD) + (1.0 / D)
    ALPHA_S_GEO = numerator_s / ALPHA_INV_GEO

    print_derivation(
        name="Strong Coupling (alpha_s) at M_Z",
        tag="AlphaS",
        formula_sym="(nu*eta + 1/D) / alpha_inv",
        latex_sym=r"\frac{\nu \cdot \eta + 1/D}{\alpha^{-1}}",
        formula_num=f"({NU} * {COORDINATE_OVERHEAD:.4f} + 0.25) / {ALPHA_INV_GEO:.4f}",
        result=ALPHA_S_GEO,
        latex_mode=LATEX_MODE,
        ref_key="alpha_s",
    )

    # --- QCD Running (Test 2: Evolution to Tau) ---
    BETA_0_QCD = 11.0 - (2.0/3.0)*3.0 # = 9.0
    M_TAU_REF = 1.77686
    M_Z_REF = REFS['mz'].value

    # 1. Linear 1-Loop Prediction (The Continuum Assumption)
    log_term = math.log(M_TAU_REF / M_Z_REF)
    denom_running = 1.0 + (BETA_0_QCD / (2.0 * PI)) * ALPHA_S_GEO * log_term
    ALPHA_S_TAU_LINEAR = ALPHA_S_GEO / denom_running

    # 2. Saturation Correction (The Finite Capacity Reality)
    # At strong coupling, channel saturation imposes a (N-1)/N efficiency limit.
    # N = Nu = 16. Factor = 15/16 = 0.9375.
    SATURATION_FACTOR = (NU - 1.0) / NU
    ALPHA_S_TAU_CORRECTED = ALPHA_S_TAU_LINEAR * SATURATION_FACTOR

    # Output Tags
    print_derivation(
        name="Alpha_s at Tau (Linear 1-Loop)",
        tag="AlphaSTauLinear",
        formula_sym="1-Loop Geometric",
        latex_sym=r"\alpha_s^{\text{(1-loop)}}",
        formula_num=f"{ALPHA_S_TAU_LINEAR:.4f}",
        result=ALPHA_S_TAU_LINEAR,
        latex_mode=LATEX_MODE
    )

    print_derivation(
        name="Alpha_s at Tau (Corrected)",
        tag="AlphaSTauCorrected",
        formula_sym="Linear * (nu-1)/nu",
        latex_sym=r"\alpha_s^{\text{(eff)}}",
        formula_num=f"{ALPHA_S_TAU_LINEAR:.4f} * 15/16",
        result=ALPHA_S_TAU_CORRECTED,
        latex_mode=LATEX_MODE,
        ref_key="alpha_s_tau"
    )

    # --- QED Running (Test 3: Z-Pole Resonance) ---
    # 1. Screening Fog
    # The standard fermionic contribution to vacuum polarization approx 8.1
    # This leaves the integer '1' as the structural resonance.
    QFT_POLARIZATION = REFS['delta_alpha_mz'].value
    SCREENING_FOG = ALPHA_INV_GEO * QFT_POLARIZATION
    
    # 2. Resonant Transition (With Manifold Friction)
    # The Z-boson couples to the Scalar Ground State (Delta^0 = 1).
    # However, this unit channel is projected onto the D=4 manifold.
    # It is subject to the same Manifold Friction (eta) as the Chiral Capacity.
    # Effective Step = 1.0 * eta
    RESONANCE_DROP = 1.0 * COORDINATE_OVERHEAD
    
    ALPHA_INV_MZ_CALC = ALPHA_INV_GEO - SCREENING_FOG - RESONANCE_DROP

    print_derivation(
        name="Alpha Inv at Z-Pole (Corrected)",
        tag="AlphaRunning",
        formula_sym="alpha_inv - Fog - eta",
        latex_sym=r"\alpha^{-1}_{geo} - \Sigma Q^2 - \eta",
        formula_num=f"{ALPHA_INV_GEO:.4f} - {SCREENING_FOG} - {COORDINATE_OVERHEAD:.4f}",
        result=ALPHA_INV_MZ_CALC,
        latex_mode=LATEX_MODE,
        ref_key="alpha_inv_mz",
    )

    # --- Weak Mixing Angle ---
    denom_weak = (D * DELTA) + (NU*COORDINATE_OVERHEAD) + SIGMA
    SIN2_THETA_W_GEO = DELTA / denom_weak

    print_derivation(
        name="Weak Mixing Angle (sin^2 theta_W)",
        tag="WeakAngle",
        formula_sym="Delta / (D*Delta + (ν * COORDINATE_OVERHEAD) + σ)",
        latex_sym=r"\frac{\Delta}{D\Delta + \nu + \sigma}",
        formula_num=f"{DELTA} / {denom_weak:.4f}",
        result=SIN2_THETA_W_GEO,
        latex_mode=LATEX_MODE,
        ref_key="sin2_w",
        context="On-Shell definition",
        formula_step1=denom_weak
    )

    print_derivation(
        name="Weak Mixing Angle (sin^2 theta_W)",
        tag="WeakAngleGlobal",
        formula_sym="Delta / (D*Delta + (ν * COORDINATE_OVERHEAD) + σ)",
        latex_sym=r"\frac{\Delta}{D\Delta + \nu + \sigma}",
        formula_num=f"{DELTA} / {denom_weak:.4f}",
        result=SIN2_THETA_W_GEO,
        latex_mode=LATEX_MODE,
        ref_key="sin2_w_global",
        context="On-Shell definition",
        formula_step1=denom_weak
    )

    # TCheck
    TCHECK = (1/ALPHA_INV_GEO)**2 * SIN2_THETA_W_GEO

    print_derivation(
        name="Weak Mixing Angle (sin^2 theta_W)",
        tag="WeakAngleTCheck",
        formula_sym="Delta / (D*Delta + (ν * COORDINATE_OVERHEAD) + σ)",
        latex_sym=r"\frac{\Delta}{D\Delta + \nu + \sigma}",
        formula_num=f"{DELTA} / {denom_weak:.4f}",
        result=TCHECK,
        latex_mode=LATEX_MODE,
        ref_key="sin2_w",
        context="On-Shell definition",
        formula_step1=denom_weak
    )

    # --- Higgs VEV ---
    # 1. Tree Level (Bare Geometric Floor)
    V_MEV_BARE = ((CHI * pow(DELTA, 2)) - L_SUBSTRATE) * ALPHA_INV_GEO * REFS["me"].value

    # 2. Radiative Correction (Topological Screening)
    # The field is screened by the Effective Dimension D_eff = D + Chi/4pi.
    D_EFF = D + (CHI / (4.0 * math.pi))
    POLARIZATION = 1.0 + (ALPHA_GEO / D_EFF)
    V_MEV_TOP = V_MEV_BARE * POLARIZATION

    # 3. Thermodynamic Noise Correction (Generation Partitioning)
    # The Persistence Margin (PM) is partitioned across the 3 generation channels.
    N_GEN = SIGMA - CHI
    NOISE_CORRECTION = 1.0 - (comp_MAR / N_GEN)
    V_MEV_PHYS = V_MEV_TOP * NOISE_CORRECTION
    
    # Final Physical VEV
    V_GEV_PHYS = V_MEV_PHYS

    # in GeV
    V_MEV_BARE /= 1000.0
    V_MEV_TOP /= 1000.0
    V_GEV_PHYS /= 1000.0 

    print_derivation(
        name="Higgs VEV (v)",
        tag="HiggsVEV",
        # Updated formula showing the 3-step derivation clearly
        formula_sym="v_tree * (1 + α/D_eff) * (1 - PM/3)",
        latex_sym=r"v_{geo} \left( 1 + \frac{\alpha}{D + \chi/4\pi} \right) \left( 1 - \frac{PM}{3} \right)",
        formula_num=f"{V_MEV_BARE:.3f} * {POLARIZATION:.6f} * {NOISE_CORRECTION:.8f}",
        result=V_GEV_PHYS,
        latex_mode=LATEX_MODE,
        ref_key="vev",
        context="electroweak scale",
        formula_step1=V_MEV_BARE,
        formula_step2=V_MEV_TOP
    )

    # --- Fermi Constant ---
    GF_GEO = 1.0 / (math.sqrt(CHI) * pow(V_GEV_PHYS, 2))

    print_derivation(
        name="Fermi Constant (G_F)",
        tag="FermiConst",
        formula_sym="1 / (√χ * v_phys²)",
        latex_sym=r"\frac{1}{\sqrt{\chi} v_{phys}^2}",
        formula_num=f"1 / (√{CHI} * {V_GEV_PHYS:.2f}²)",
        result=GF_GEO,
        latex_mode=LATEX_MODE,
        ref_key="gf",
    )

    # --- Higgs Parameters ---
    # Resonant Tax (Dynamics): 
    # The lattice oscillates at frequency Delta. We must subtract 1 unit of bandwidth (1/Delta)
    LAMBDA_NET=((SIGMA - CHI) - (1.0 / DELTA))
    LAMBDA_GEO = LAMBDA_NET / L_INTRINSIC
    MH_GEO = math.sqrt(2 * LAMBDA_GEO) * V_GEV_PHYS

    print_derivation(
        name="Higgs Self-Coupling (λ)",
        tag="HiggsLambda",
        formula_sym="((σ - χ) - 1/Δ) / H_{intrinsic}",
        latex_sym=r"\frac{(\sigma - \chi) - \frac{1}{\Delta}}{H_{sys}}",
        formula_num=f"({SIGMA} - {CHI} - 1/{DELTA}) / {L_INTRINSIC}",
        result=LAMBDA_GEO,
        latex_mode=LATEX_MODE,
        ref_key="lambda",
        formula_step1=LAMBDA_NET
    )

    print_derivation(
        name="Higgs Mass (m_H)",
        tag="HiggsMass",
        formula_sym="√(2λ) * v",
        latex_sym=r"\sqrt{2\lambda} v",
        formula_num=f"√(2 * {LAMBDA_GEO:.4f}) * {V_GEV_PHYS:.2f}",
        result=MH_GEO,
        latex_mode=LATEX_MODE,
        ref_key="mh",
    )

    # --- Electron Yukawa (y_e) ---
    YE_BARE = comp_MAR
    PROJECTION_COEFF = SIGMA / D  # 1.25
    SELF_ENERGY_CORRECTION = 1.0 + (PROJECTION_COEFF * ALPHA_GEO)
    YE_CORRECTED = YE_BARE * SELF_ENERGY_CORRECTION
    
    print_derivation(
        name="Electron Yukawa (y_e) [Geometric]",
        tag="ElectronYukawa",
        formula_sym="PM * (1 + (σ/D)α)",
        latex_sym=r"PM_{geo} \left(1 + \frac{\sigma}{D}\alpha \right)",
        formula_num=f"{YE_BARE:.4e} * (1 + 1.25*{ALPHA_GEO:.4f})",
        result=YE_CORRECTED,
        latex_mode=LATEX_MODE,
        ref_key="ye_sm",
        context="Includes geometric charge projection (Sigma/D)",
        formula_step1=YE_BARE
    )

    # --- Jarlskog Invariant (Time Asymmetry) ---
    PHI = (1 + math.sqrt(5)) / 2
    J_GEO = pow(PHI, 2) * comp_TOL * COORDINATE_OVERHEAD

    print_derivation(
        name="Jarlskog Invariant (J)",
        tag="Jarlskog",
        formula_sym="phi^2 * T_geo",
        latex_sym=r"\phi^2 \cdot T_{geo}",
        formula_num=f"{PHI:.4f}^2 * {comp_TOL:.4e}",
        result=J_GEO,
        latex_mode=LATEX_MODE,
        ref_key="jarlskog",
        context="CP violation parameter"
    )

    # --- W Boson Mass (Validation) ---
    MZ_EXP = REFS['mz'].value
    MW_GEO = MZ_EXP * math.sqrt(1.0 - SIN2_THETA_W_GEO)
    
    print_derivation(
        name="W Boson Mass (M_W)",
        tag="WBosonMass",
        formula_sym="M_Z * sqrt(1 - sin2_theta_w)",
        latex_sym=r"M_Z \sqrt{1 - \sin^2\theta_W}",
        formula_num=f"{MZ_EXP} * sqrt(1 - {SIN2_THETA_W_GEO:.4f})",
        result=MW_GEO,
        latex_mode=LATEX_MODE,
        ref_key="mw",
        context="CDF/ATLAS Tension Mediator"
    )

    # --- Cabibbo Angle (Flavor Aperture) ---
    # Leakage = Interface / Flavor Width
    SIN_THETA_C_GEO = PI / (NU - CHI)
    
    print_derivation(
        name="Cabibbo Angle (|V_us|)",
        tag="CabibboAngle",
        formula_sym="pi / (nu - chi)",
        latex_sym=r"\frac{\pi}{\nu - \chi}",
        formula_num=f"{PI:.4f} / ({NU} - {CHI})",
        result=SIN_THETA_C_GEO,
        latex_mode=LATEX_MODE,
        ref_key="vus",
        context="Flavor Aperture"
    )

    # ==========================================
    # 5. GRAVITY & PLANCK MASS
    # ==========================================
    print_section("GRAVITY & HIERARCHY", LATEX_MODE)

    # --- Residual Capacity Components ---
    BOUNDARY_STORAGE = CHI / (SIGMA - CHI)
    GAUGE_LOAD = ALPHA_GEO
    B_RES = NU - BOUNDARY_STORAGE - GAUGE_LOAD

    print_derivation(
        name="Residual Capacity (B_res)",
        tag="ResidualCap",
        formula_sym="ν - χ/(σ-χ) - α",
        latex_sym=r"\nu - \frac{\chi}{\sigma-\chi} - \alpha",
        formula_num=f"{NU} - {BOUNDARY_STORAGE:.4f} - {GAUGE_LOAD:.4e}",
        result=B_RES,
        latex_mode=LATEX_MODE
    )

    # --- Bandwidth Conservation (Synthesis) ---
    TOTAL_BANDWIDTH = B_RES + BOUNDARY_STORAGE + GAUGE_LOAD

    print_derivation(
        name="Boundary Storage",
        tag="BoundaryStorage",
        formula_sym="χ/(σ-χ)",
        latex_sym=r"\frac{\chi}{\sigma-\chi}",
        formula_num=f"{CHI}/({SIGMA}-{CHI})",
        result=BOUNDARY_STORAGE,
        latex_mode=LATEX_MODE
    )

    print_derivation(
        name="Gauge Load",
        tag="GaugeLoad",
        formula_sym="α",
        latex_sym=r"\alpha",
        formula_num=f"{GAUGE_LOAD:.6f}",
        result=GAUGE_LOAD,
        latex_mode=LATEX_MODE
    )

    print_derivation(
        name="Total Bandwidth Sum",
        tag="TotalBandwidth",
        formula_sym="B_res + Boundary + Gauge",
        latex_sym=r"B_{res} + \frac{\chi}{\sigma-\chi} + \alpha",
        formula_num=f"{B_RES:.4f} + {BOUNDARY_STORAGE:.4f} + {GAUGE_LOAD:.4f}",
        result=TOTAL_BANDWIDTH,
        latex_mode=LATEX_MODE
    )

    # --- Gravitational Coupling ---
    EXP_G = DELTA / 2.0
    ALPHA_G_GEO = B_RES * pow(ALPHA_GEO, EXP_G)

    print_derivation(
        name="Gravitational Coupling (α_G)",
        tag="GravCoupling",
        formula_sym="B_res * α^(Δ/2)",
        latex_sym=r"B_{res} \alpha^{\Delta/2}",
        formula_num=f"{B_RES:.4f} * α^{EXP_G}",
        result=ALPHA_G_GEO,
        latex_mode=LATEX_MODE,
        ref_key="G_coupling",
        context="dimensionless coupling"
    )

    # --- Planck Mass ---
    MP_MEV_GEO = REFS["me"].value / math.sqrt(ALPHA_G_GEO)
    MP_GEV_GEO = MP_MEV_GEO / 1000.0

    print_derivation(
        name="Planck Mass (M_P)",
        tag="PlanckMass",
        formula_sym="m_e / √α_G",
        latex_sym=r"\frac{m_e}{\sqrt{\alpha_G}}",
        formula_num=f"m_e / √{ALPHA_G_GEO:.4e}",
        result=MP_GEV_GEO,
        latex_mode=LATEX_MODE,
        ref_key="Mp",
        context="hierarchy scale"
    )

    # --- Higgs Impedance (Validation) ---
    # 1. Weak Aperture Target (with Manifold Friction)
    # The ideal aperture is (Sigma + 1) = 6.
    # The projection onto the manifold (D*Delta) introduces a friction term 1/(D*Delta).
    APERTURE_IDEAL = SIGMA + 1.0
    APERTURE_PROJECTED = APERTURE_IDEAL * COORDINATE_OVERHEAD
    
    # 2. Higgs Impedance Calculation
    # Z_H = (1/lambda) * exp(-2*lambda)
    Z_HIGGS = (1.0 / LAMBDA_GEO) * math.exp(-2.0 * LAMBDA_GEO)
    
    print_derivation(
        name="Higgs Impedance (Z_H)",
        tag="HiggsImpedance",
        formula_sym="(1/λ) * e^(-2λ)",
        latex_sym=r"\frac{1}{\lambda}e^{-2\lambda}",
        formula_num=f"(1/{LAMBDA_GEO:.4f}) * exp(-{2*LAMBDA_GEO:.4f})",
        result=Z_HIGGS,
        latex_mode=LATEX_MODE
    )
    
    print_derivation(
        name="Weak Aperture (Projected)",
        tag="WeakApertureProj",
        formula_sym="6 * (1 - 1/DΔ)",
        latex_sym=r"(\sigma+1)(1 - \frac{1}{D\Delta})",
        formula_num=f"6 * (1 - 1/{D*DELTA})",
        result=APERTURE_PROJECTED,
        latex_mode=LATEX_MODE
    )

    # ==========================================
    # 6. VACUUM ENERGY (THE 10^120 SOLUTION)
    # ==========================================
    
    # Derivation C: The Thermal Resolution Limit
    # M_min = m_e * (Thermal Coupling / Mode Density)
    #       = m_e * (pi * alpha) / (nu * Delta^3)
    
    # 1. Thermal Coupling (Admittance * Geometry)
    THERMAL_COUPLING = PI * ALPHA_GEO
    
    # 2. Mode Density (Capacity * Volume)
    MODE_DENSITY = NU * pow(DELTA, 3)
    
    # 3. Minimum Geometric Resolution (The Noise Floor)
    # Units: MeV (inherited from m_e)
    # This represents the minimum energy scale, not frequency in Hz.
    M_GEO_MIN = REFS['me'].value * (THERMAL_COUPLING / MODE_DENSITY)
    
    # 4. Vacuum Density (rho_vac)
    # The entropic noise of the ground state, gated by admittance (alpha).
    # rho = (alpha/2) * M_min^4 (Natural Units)
    RHO_VAC_MEV4 = (ALPHA_GEO / 2.0) * pow(M_GEO_MIN, 4)
    
    # 5. Hierarchy Ratio (rho_vac / M_P^4)
    # Comparing the Vacuum Floor to the Planck Ceiling.
    # Uses MP_MEV_GEO derived in the Gravity section.
    VACUUM_HIERARCHY = RHO_VAC_MEV4 / pow(MP_MEV_GEO, 4)

    print_derivation(
        name="Vacuum Energy Scaling (rho_vac / M_P^4)",
        tag="VacuumEnergyScale",
        formula_sym="(alpha/2) * (M_min / M_P)^4",
        latex_sym=r"\frac{\alpha}{2} \left( \frac{M_{min}}{M_P} \right)^4",
        formula_num=f"({ALPHA_GEO:.4f}/2) * ({M_GEO_MIN:.4e}/{MP_MEV_GEO:.4e})^4",
        result=VACUUM_HIERARCHY,
        latex_mode=LATEX_MODE,
        ref_key="vacuum_ratio"
    )
    
    # ==========================================
    # 7. VACUUM ENERGY (THE 10^120 SOLUTION)
    # ==========================================


    # 1. QCD Axial Anomaly (Nc = 3)
    Nc_geo = SIGMA - CHI
    print_derivation(
        name = "Color Charge (Nc)",
        tag= "Nc",
        formula_sym="sigma - chi",
        latex_sym=r"\sigma - \chi",
        formula_num=r"5 - 2",
        result= Nc_geo,
        latex_mode=args.latex,
        ref_key="nc_color"
    )
    # 2. Weinberg Angle at Unification (GUT Scale)
    # At symmetric phase: D4 (+) D4 both active -> 8 total dimensions
    # Color sector (sigma-chi=3) over total lattice (2D=8)
    sin2_gut = (SIGMA - CHI) / (D + D) 
    print_derivation(
        name="Weinberg Angle (GUT)",
        tag="WeinbergGUT",
        formula_sym=r"\frac{N_c}{2D}",
        latex_sym=r"\frac{N_c}{2D}",
        formula_num="3/8",
        result=sin2_gut,
        latex_mode=args.latex,
        ref_key=None
    )


    # Optional: Print the physical wavelength for debugging/sanity check
    # h_bar * c approx 197.327 MeV*fm
    # lambda = (2 * pi * h_bar * c) / M_min
    if not LATEX_MODE:
        HBAR_C_MICRON = 0.197327 # MeV * micrometer
        LAMBDA_MICRON = (2 * PI * HBAR_C_MICRON) / M_GEO_MIN
        print(f"  Physical Wavelength (lambda_min): {LAMBDA_MICRON:.2f} micrometers")
        print("-" * 60 + "\n")

    RESULTS = {}
    RESULTS["AlphaInv"] = ALPHA_INV_GEO
    RESULTS["FermiConst"] = GF_GEO
#    RESULTS["WBosonMass"] = MW_GEO
    RESULTS["AlphaS"] = ALPHA_S_GEO
    RESULTS["HiggsMass"] = MH_GEO

    RESULTS["VonKlitzing"] = RK_GEO
    RESULTS["WeakAngle"] = SIN2_THETA_W_GEO
    RESULTS["CabibboAngle"] = SIN_THETA_C_GEO
    RESULTS["Jarlskog"] = J_GEO
    RESULTS["PlanckMass"] = MP_GEV_GEO
    run_global_audit(RESULTS, REFS, LATEX_MODE)

if __name__ == "__main__":
    main()
