#!python3

import math
import argparse
from decimal import getcontext
from sympy import symbols, Rational, latex, simplify, UnevaluatedExpr

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

## TODO convert the various equations into objects with symbols and then printing them out is cleaner
def test():
    DELTA_SYM, NU_SYM, SIGMA_SYM, CHI_SYM, D_SYM = symbols('Delta nu sigma chi D', integer=True, positive=True)
    N_sym = 2*NU_SYM
    R_M_sym = D_SYM*DELTA_SYM

    # Build with explicit 1
    Z_TOL = (1 * D_SYM * (R_M_sym - SIGMA_SYM)) / (N_sym**3 * SIGMA_SYM * R_M_sym)

    print("LaTeX (symbolic):", latex(Z_TOL))
    Z_TOL_num = Z_TOL.subs({DELTA_SYM: 43, NU_SYM: 16, SIGMA_SYM: 5, CHI_SYM: 2, D_SYM: 4})
    print("LaTeX (numeric): ", latex(Z_TOL_num))
    print("Evaluated:       ", float(Z_TOL_num))


def main():
    parser = argparse.ArgumentParser(description="Calculate E8 Persistence Constants")
    parser.add_argument('--latex', action='store_true', help='Output in catchfilebetweentags format')
    parser.add_argument('--paper', type=int, default=-1, choices=[1, 3], help='Select paper variant (e.g., 1 or 3 or -1 for all)')
    args = parser.parse_args()

    LATEX_MODE = args.latex
    PAPER_NUM = args.paper
    
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
    COORDINATE_OVERHEAD = 1.0 - (1.0 / (D * DELTA))

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

    AlphaInv_CAP = PI * DELTA
    AlphaInv_MAP = CHI
    AlphaInv_PRO = -(1.0 / (R_M - SIGMA))
    AlphaInv_GOV = -(CHI / DELTA)
    AlphaInv_TOL = (1.0 * CHI * (R_M - SIGMA)) / (N**3 * SIGMA * R_M)
    AlphaInv_MAR = 1.0 / (L_EMBED * (SIGMA + 1) * DELTA**2)
    # Summation
    ALPHA_INV_GEO = AlphaInv_CAP + AlphaInv_MAP + AlphaInv_PRO + AlphaInv_GOV + AlphaInv_TOL + AlphaInv_MAR
    ALPHA_GEO = 1.0 / ALPHA_INV_GEO

    # Table breakdown for human mode
    if not LATEX_MODE:
        print(f"{'COMPONENT':<25} | {'FORMULA':<25} | {'VALUE':<15}")
        print("-" * 70)
        print(f"{'Capacity':<25} | {'π * Δ':<25} | {AlphaInv_CAP:+.8f}")
        print(f"{'Map':<25} | {'χ':<25} | {AlphaInv_MAP:+.8f}")
        print(f"{'Protocol':<25} | {'-1/(DΔ - σ)':<25} | {AlphaInv_PRO:+.8f}")
        print(f"{'Governor':<25} | {'-χ/Δ':<25} | {AlphaInv_GOV:+.8f}")
        print(f"{'Toll':<25} | {'Eq 16a':<25} | {AlphaInv_TOL:+.8e}")
        print(f"{'Margin':<25} | {'Eq 16b':<25} | {AlphaInv_MAR:+.8e}")
        print("-" * 70)
        print(f"{'TOTAL IMPEDANCE':<25} | {'SUM':<25} | {ALPHA_INV_GEO:.9f}")
        print("-" * 70)
        print("")
    else:
        # Export components for Table II generation
        print(f"%<*AlphaInvCAP>{AlphaInv_CAP:.5f}%</AlphaInvCAP>")
        print(f"%<*AlphaInvMAP>{AlphaInv_MAP:.5f}%</AlphaInvMAP>")
        print(f"%<*AlphaInvPRO>{AlphaInv_PRO:.5f}%</AlphaInvPRO>")
        print(f"%<*AlphaInvGOV>{AlphaInv_GOV:.5f}%</AlphaInvGOV>")
        print(f"%<*AlphaInvTOL>{to_latex_sci(AlphaInv_TOL)}%</AlphaInvTOL>")
        print(f"%<*AlphaInvMAR>{to_latex_sci(AlphaInv_MAR)}%</AlphaInvMAR>")
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

    if LATEX_MODE:
        me = REFS['me'].value
        print(f"%<*MeMeV>{me}%</MeMeVPrint>")
        print(f"%<*MeMeVPrint>{me}%</MeMeVPrint>")
        print("")

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
    CHARGE_RATIO = 1.0 / math.sqrt(ALPHA_INV_GEO)
    CHARGE_ATTENUATION = math.sqrt(ALPHA_INV_GEO)
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

    if PAPER_NUM == 1:
        return


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
        formula_sym="phi^2 * T_geo",
        latex_sym=r"\phi^2 \cdot T_{geo}",
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
