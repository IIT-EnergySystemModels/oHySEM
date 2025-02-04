"""
Optimized Hybrid Systems for Energy and Market management (oHySEM)


    Args:
        case:   Name of the folder where the CSV files of the case are found
        dir:    Main path where the case folder can be found
        solver: Name of the solver

    Returns:
        Output results in CSV files that are found in the case folder.

    Examples:
        >>> import oHySEM as oH
        >>> oH.routine("VPP1", "C:\\Users\\UserName\\Documents\\GitHub\\oHySEM", "glpk")
"""
__version__ = "1.0.7"

from .oHySEM import main
