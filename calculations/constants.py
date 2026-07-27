#!python3

import math
import argparse
from decimal import getcontext
from sympy import symbols, Rational, N, latex, simplify, pretty, UnevaluatedExpr, pi, sqrt

from experimental_values import PAPER1_REFS, PAPER3_REFS
REFS = {**PAPER1_REFS, **PAPER3_REFS}
from output_helpers import (
    PI, print_section, print_derivation, run_global_audit_tier, to_latex_sci
)

getcontext().prec = 5000

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

def wrap_latex_tag(val, units):
    if units == None or units == "":
        return val
    return f"\\qty{{{val}}}{{{units}}}"

def format_latex_tag(val, precision=12):
    """
    Formats a numeric/SymPy value dynamically:
    - Integers: 4
    - Small floats (< 0.001): 1.23456789e-05
    - Real floats: 137.03599908
    """
    if hasattr(val, 'is_integer') and val.is_integer:
        return f"{int(val)}"

    float_val = float(val)

    # Check if value is integer or within floating-point epsilon of an integer
    if float_val.is_integer() or abs(float_val - round(float_val)) < 1e-12:
        return f"{int(round(float_val))}"

    # Tiny values needing scientific notation
    if 0 < abs(float_val) < 1e-3 or abs(float_val) >= 1e8:
        return f"{float_val:.{precision}e}"

    # Standard decimal representation: format to precision then strip trailing zeroes
    return f"{float_val:.{precision}f}".rstrip('0').rstrip('.')

def outputgroup(group_list, listname, subs, LATEX_MODE=False):
    if not LATEX_MODE:
        print(f"{listname}:")
        print("-" * 70)
    for item in group_list:
        sym, formula = item[0], item[1]
        experimentalValues = item[2] if len(item) > 2 else []
        if sym not in subs:
            uneval_subs = {
                k: UnevaluatedExpr(v) if not isinstance(v, UnevaluatedExpr) else v
                for k, v in subs.items()
            }
            subs[sym] = formula.subs(uneval_subs)

        tag_name = "".join(sym.name.split("_"))
        tag_name = tag_name[:1].upper() + tag_name[1:]
        if (tag_name == "Alpha^-1"):
            tag_name = "AlphaInv"
        latex_formula = latex(formula)
        unicode_formula = pretty(formula, use_unicode=True)

        uneval_subs = {k: UnevaluatedExpr(v) for k, v in subs.items()}
        formula_sub = formula.subs(uneval_subs)
        latex_substituted = latex(formula_sub)

        num_val = N(formula.subs(subs).doit())
        precision = REFS[experimentalValues[0]].decimals if len(experimentalValues) > 0 else 12
        units = REFS[experimentalValues[0]].units if len(experimentalValues) > 0 else None
        formatted_val = format_latex_tag(num_val, precision)

        if LATEX_MODE:
            print(f"%<*{tag_name}Eq>{latex_formula}%</{tag_name}Eq>")
            print(f"%<*{tag_name}Val>{wrap_latex_tag(formatted_val, units)}%</{tag_name}Val>")
        else:
            print(f"{sym}")
            print(f"  formula = ({latex_formula})")
            print(f"  formula = ({latex_substituted})")
            print(f"  value = {formatted_val} {units if units != None else ""}")

        for idx, exp_key in enumerate(experimentalValues):
            experiment = REFS[exp_key]
            diff = num_val - experiment.value
            sigma = diff / experiment.uncertainty if experiment.uncertainty != 0 else 0.0

            tag_suffix = exp_key.split("_")[-1].capitalize()
            if not LATEX_MODE:
                print(f"  [Exp {exp_key}] Citation     : {experiment.citation}")
                print(f"  [Exp {exp_key}] Value        : {experiment.value:.{experiment.decimals}f} ± {experiment.uncertainty:.{experiment.decimals}f} {experiment.units}")
                print(f"  [Exp {exp_key}] Difference   : {diff:+.6e}")
                print(f"  [Exp {exp_key}] Discrepancy  : {sigma:+.2f} σ\n")
            else:
                out_str = experiment.format_latex()

                print(f"%<*{tag_name}{tag_suffix}ExperimentalVal>{out_str}%</{tag_name}{tag_suffix}ExperimentalVal>")
                print(f"%<*{tag_name}{tag_suffix}Diff>{to_latex_sci(diff, 3)}%</{tag_name}{tag_suffix}Diff>")
                print(f"%<*{tag_name}{tag_suffix}Sigma>{sigma:+.2f}%</{tag_name}{tag_suffix}Sigma>")

    if not LATEX_MODE:
        print("-" * 70)
    print(f"")

## TODO convert all equations into objects with symbols and then printing them out
def paper1(LATEX_MODE = False):
    PI_SYM = symbols('pi', positive=True)

    # ==========================================
    # SYSTEM 1: CHARACTERISTIC_INTEGERS
    # ==========================================
    DELTA_SYM, NU_SYM, SIGMA_SYM, CHI_SYM, D_SYM = symbols('Delta nu sigma chi D', integer=True, positive=True)
    CHARACTERISTIC_INTEGERS = [
        (DELTA_SYM, DELTA_SYM),
        (NU_SYM, NU_SYM),
        (SIGMA_SYM, SIGMA_SYM),
        (CHI_SYM, CHI_SYM),
        (D_SYM, D_SYM),
    ]
    e8_subs = {
        D_SYM: 4,
        DELTA_SYM: 43,
        SIGMA_SYM: 5,
        CHI_SYM: 2,
        NU_SYM: 16
    }

    L_INTRINSIC_SYM, L_EMBED_SYM, L_SUBSTRATE_SYM, N_SYM, RM_SYM = symbols('L_intrinsic L_embed L_substrate N RM', integer=True, positive=True)
    DERIVED_LOADS = [
        (L_INTRINSIC_SYM, NU_SYM + SIGMA_SYM + CHI_SYM),
        (L_EMBED_SYM,     NU_SYM + SIGMA_SYM + CHI_SYM + (2 * D_SYM)),
        (L_SUBSTRATE_SYM, (DELTA_SYM * D_SYM) + NU_SYM),
        (N_SYM,           2 * NU_SYM),
        (RM_SYM,         D_SYM * DELTA_SYM),
    ]

    print_section("SYSTEM 1: THE INVARIANT SUBSTRATE", LATEX_MODE)
    outputgroup(CHARACTERISTIC_INTEGERS, "Characteristic Integers", e8_subs, LATEX_MODE)
    outputgroup(DERIVED_LOADS, "Derived loads", e8_subs, LATEX_MODE)

    # ==========================================
    # SYSTEM 2: IMPEDANCE
    # ==========================================
    ALPHA_INV_CAP_SYM = symbols('AlphaInvCAP')
    ALPHA_INV_MAP_SYM = symbols('AlphaInvMAP')
    ALPHA_INV_PRO_SYM = symbols('AlphaInvPRO')
    ALPHA_INV_GOV_SYM = symbols('AlphaInvGOV')
    ALPHA_INV_TOL_SYM = symbols('AlphaInvTOL')
    ALPHA_INV_MAR_SYM = symbols('AlphaInvMAR')

    IMPEDANCE_COMPONENTS = [
        (ALPHA_INV_CAP_SYM, pi * DELTA_SYM),
        (ALPHA_INV_MAP_SYM, CHI_SYM),
        (ALPHA_INV_PRO_SYM, -Rational(1, 1) / (RM_SYM - SIGMA_SYM)),
        (ALPHA_INV_GOV_SYM, -Rational(1, 1) * CHI_SYM / DELTA_SYM),
        (ALPHA_INV_TOL_SYM, (Rational(1, 1) * CHI_SYM * (RM_SYM - SIGMA_SYM)) / (N_SYM**3 * SIGMA_SYM * RM_SYM)),
        (ALPHA_INV_MAR_SYM, Rational(1, 1) / (L_EMBED_SYM * (SIGMA_SYM + 1) * DELTA_SYM**2)),
    ]

    ALPHA_INV_SYM = symbols('alpha^-1')
    ALPHA_SYM = symbols('alpha')
    IMPEDANCE = [
        (ALPHA_INV_SYM, ALPHA_INV_CAP_SYM + ALPHA_INV_MAP_SYM + ALPHA_INV_PRO_SYM + ALPHA_INV_GOV_SYM + ALPHA_INV_TOL_SYM + ALPHA_INV_MAR_SYM, ["alpha_inv_codata",
        "alpha_inv_morel",
        "alpha_inv_parker",
        "alpha_inv_fan"]),
        (ALPHA_SYM, Rational(1, 1) / ALPHA_INV_SYM),
    ]

    print_section("SYSTEM 2: GEOMETRIC IMPEDANCE", LATEX_MODE)
    outputgroup(IMPEDANCE_COMPONENTS, "Alpha^-1 components", e8_subs, LATEX_MODE)
    outputgroup(IMPEDANCE, "alpha^-1", e8_subs, LATEX_MODE)

    # --- Von Klitzing Constant (Quantum Resistance) ---
    SOL_SYM = symbols('SpeedOfLight')
    RK_SYM = symbols('VonKlitzing')
    VONKLITZING = [
        (SOL_SYM, UnevaluatedExpr((10**-7) * 299792458)),
        (RK_SYM, (4 * pi * SOL_SYM)/ (2 * ALPHA_SYM), ["rk"])
    ]
    outputgroup(VONKLITZING, "Von Klitzing Constant", e8_subs, LATEX_MODE)

    # --- Planck Charge Ratio & Vacuum Breakdown ---
    CHARGE_RATIO_SYM = symbols('PlanckChargeRatio')
    CHARGE_RATIO_PCT_SYM = symbols('PlanckChargeRatioPercentage')
    CHARGE_ATTENUATION_SYM = symbols('PlanckChargeAttenuation')    
    PLANCKCHARGE = [
        (CHARGE_RATIO_SYM, 1 / sqrt(ALPHA_INV_SYM)),
        (CHARGE_RATIO_PCT_SYM, CHARGE_RATIO_SYM * 100),
        (CHARGE_ATTENUATION_SYM, sqrt(ALPHA_INV_SYM))
    ]
    outputgroup(PLANCKCHARGE, "Planck Charge Ratio", e8_subs, LATEX_MODE)

def main():
    parser = argparse.ArgumentParser(description="Calculate E8 Persistence Constants")
    parser.add_argument('--latex', action='store_true', help='Output in catchfilebetweentags format')
    parser.add_argument('--paper', type=int, default=-1, choices=[1, 3], help='Select paper variant (e.g., 1 or 3 or -1 for all)')
    args = parser.parse_args()

    LATEX_MODE = args.latex
    PAPER_NUM = args.paper
    
    paper1(LATEX_MODE)

    if LATEX_MODE:
        me = REFS['me'].value
        print(f"%<*MeMeV>{me}%</MeMeVPrint>")
        print("")

    D     = 4
    DELTA = 43
    SIGMA = 5
    NU    = 16
    CHI   = 2
    L_INTRINSIC = NU + SIGMA + CHI
    L_EMBED = L_INTRINSIC + (2 * D)
    L_SUBSTRATE = (DELTA * D) + NU
    N = 2 * NU
    R_M = D * DELTA

    AlphaInv_CAP = PI * DELTA
    AlphaInv_MAP = CHI
    AlphaInv_PRO = -(1.0 / (R_M - SIGMA))
    AlphaInv_GOV = -(CHI / DELTA)
    AlphaInv_TOL = (1.0 * CHI * (R_M - SIGMA)) / (N**3 * SIGMA * R_M)
    AlphaInv_MAR = 1.0 / (L_EMBED * (SIGMA + 1) * DELTA**2)
    ALPHA_INV_GEO = AlphaInv_CAP + AlphaInv_MAP + AlphaInv_PRO + AlphaInv_GOV + AlphaInv_TOL + AlphaInv_MAR
    ALPHA_GEO = 1.0 / ALPHA_INV_GEO

    if PAPER_NUM == 1:
        return


    # ==========================================
    # 4. SYSTEM IV: THE GEOMETRIC CONTROL ARCHITECTURE
    # ==========================================
    print_section("SYSTEM IV: THE GEOMETRIC CONTROL ARCHITECTURE", LATEX_MODE)

    COORDINATE_OVERHEAD = 1.0 - (1.0 / (D * DELTA))
    if LATEX_MODE:
        print(f"%<*InvCoordinateOverhead>{COORDINATE_OVERHEAD}%</InvCoordinateOverhead>")

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
        latex_sym=r"\frac{\Delta}{D\Delta + \nu\left(1 - \frac{1}{D\Delta}\right) + \sigma}",
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
    NOISE_CORRECTION = 1.0 - (AlphaInv_MAR / N_GEN)
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
        formula_sym="((σ - χ) - 1/Δ) / L_{intrinsic}",
        latex_sym=r"\frac{(\sigma - \chi) - \frac{1}{\Delta}}{L_{intrinsic}}",
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
    YE_BARE = AlphaInv_MAR
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
    J_GEO = pow(PHI, 2) * AlphaInv_TOL * COORDINATE_OVERHEAD

    print_derivation(
        name="Jarlskog Invariant (J)",
        tag="Jarlskog",
        formula_sym="phi^2 * T_geo * eta",
        latex_sym=r"\phi^2 \cdot T_{geo} \cdot \eta",
        formula_num=f"{PHI:.4f}^2 * {AlphaInv_TOL:.4e}",
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
        formula_sym="(sigma + 1) * (1 - 1/(D*Delta))",
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
