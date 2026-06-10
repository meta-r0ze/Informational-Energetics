#!python3
import math

from experimental_values import PAPER1_REFS, PAPER3_REFS
REFS = {**PAPER1_REFS, **PAPER3_REFS}

PI = math.pi

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