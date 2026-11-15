"""Local text preparation for manual chat; no network or model dependency."""
from collections import Counter
from io import StringIO
from p4vasp.Structure import Structure


def capture_structure(system, viewer=None):
    """Snapshot the source frame, before visual wrapping/hiding/replication."""
    if system is None:
        return None, 'No active system'
    if viewer is not None and viewer.system is system and viewer.swin is not None:
        sequence = viewer.getSequence()
        if sequence is not None and len(sequence) and 0 <= viewer.index < len(sequence):
            return Structure(sequence[viewer.index]), 'Show source frame %d (1-based)' % (viewer.index + 1)
    structure = system.INITIAL_STRUCTURE
    return (Structure(structure) if structure is not None else None), 'Active system initial structure'


def format_context(structure=None, source='Active system initial structure', include_poscar=False, incar=None):
    lines = ['Please help me with this VASP/p4vasp model.', '', 'Structure source: ' + source]
    if structure is None:
        lines.append('No structure loaded.')
    else:
        counts = Counter()
        for index in range(len(structure.info)):
            record = structure.info.getRecord(index)
            counts[str(record.element).strip() or 'Unknown'] += int(record.atomspertype)
        lines += ['Atoms: %d' % len(structure),
                  'Composition: ' + ', '.join('%s: %d' % item for item in counts.items() if item[1])]
        # Normalize only a private copy; neither coordinates nor scale in the
        # source/snapshot are changed by constructing this compact summary.
        physical = Structure(structure)
        physical.correctScaling()
        lines.append('Cell vectors (angstrom):')
        lines.extend('  ' + ' '.join('%.6g' % value for value in row) for row in physical.basis)
        if include_poscar:
            stream = StringIO()
            structure.write(stream)
            lines += ['', 'POSCAR (all source atoms; no visual replicas):', '```text', stream.getvalue().rstrip(), '```']
        else:
            lines += ['Atomic coordinates omitted to shorten the prompt.',
                      'This summary cannot establish bonds, defects or local atomic geometry.']
    if incar is not None:
        lines += ['', 'INCAR:', '```text', str(incar).rstrip(), '```']
    return '\n'.join(lines) + '\n'
