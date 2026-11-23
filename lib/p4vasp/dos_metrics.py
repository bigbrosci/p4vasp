"""Shared numerical d-DOS calculation, also embedded in standalone exports."""
import math

HILBERT_GRID_TOLERANCE = .05  # Fraction of the mean energy step.


def calculate_metrics(energies, density, structure, emin=None, emax=None):
    from importlib.metadata import version
    import numpy as np
    from pymatgen.electronic_structure.core import Spin, Orbital
    from pymatgen.electronic_structure.dos import CompleteDos, Dos
    energies=np.asarray(energies,dtype=float);density=np.asarray(density,dtype=float)
    if energies.ndim!=1 or len(energies)<2 or density.shape!=energies.shape:
        raise ValueError('Invalid energy/density arrays.')
    if not np.all(np.isfinite(energies)) or np.any(np.diff(energies)<=0):
        raise ValueError('Energy grid must be finite and strictly increasing.')
    if not np.all(np.isfinite(density)) or np.any(density<0):
        raise ValueError('Expected finite nonnegative d-DOS.')
    lower = float(emin if emin is not None else energies[0])
    upper = float(emax if emax is not None else energies[-1])
    if not math.isfinite(lower) or not math.isfinite(upper) or lower>=upper:
        raise ValueError('Energy limits must be finite with minimum < maximum.')
    if lower < energies[0]-1e-7 or upper > energies[-1]+1e-7:
        raise ValueError('Analysis range lies outside the available E−EF grid: %.6g to %.6g eV.'%(energies[0],energies[-1]))
    lower=max(lower,float(energies[0]));upper=min(upper,float(energies[-1]))
    grid = np.unique(np.r_[lower, energies[(energies>lower)&(energies<upper)], upper,
                           [0.] if lower<0<upper else []])
    values = np.interp(grid, energies, density)
    weight = float(np.trapezoid(values,x=grid))
    if weight <= 1e-12: raise ValueError('Selected d-DOS has zero weight in this range.')
    # A summed selected d projection is sufficient for the moment methods.
    def selected_dos(grid, values):
        channels = {Spin.up:values}
        return CompleteDos(structure, Dos(0.,grid,channels),
                           {structure[0]:{Orbital.dxy:channels}})
    clipped = selected_dos(grid, values)
    center = float(clipped.get_band_center())
    width = float(clipped.get_band_width())
    # Include interpolated EF exactly; pymatgen's < EF mask omits that endpoint.
    occupied = grid<=0
    filling = float(np.trapezoid(values[occupied],x=grid[occupied])/weight) if occupied.sum()>1 else 0.
    notes = []
    edge = None
    uniform = np.linspace(energies[0],energies[-1],len(energies))
    step = float(uniform[1]-uniform[0])
    deviation = float(np.max(np.abs(energies-uniform)))
    if deviation <= max(1e-8,step*HILBERT_GRID_TOLERANCE):
        hilbert_density = np.interp(uniform,energies,density)
        edge = float(selected_dos(uniform,hilbert_density).get_upper_band_edge(erange=(lower,upper)))
        if deviation > max(1e-8,step*1e-5):
            notes.append('Upper edge: slightly irregular/rounded source grid linearly resampled to %d uniform points (step %.8g eV; maximum adjustment %.8g eV).'%(len(uniform),step,deviation))
    else: notes.append('Upper edge unavailable: source grid differs from a uniform grid by more than 5% of the mean energy step.')
    rows = [['d-band center',center,'eV'],['d-band width (standard deviation)',width,'eV'],
            ['d-band filling (selected window)',filling,'dimensionless'],
            ['d-band upper edge (Hilbert)',edge,'eV']]
    return dict(rows=rows, emin=lower, emax=upper, energy_reference='E−EF', weight=weight,
                pymatgen_version=version('pymatgen'), notes=notes,
                filling_definition='Integral within selected window up to EF / integral over selected window; interpolated endpoints.',
                upper_edge_definition='Peak of Hilbert transform of full selected d-DOS, searched inside the selected window; source grid deviations <=5% of mean step are linearly resampled to uniform spacing.',
                normalization='Sum over selected atoms and spin channels; not per atom.')
