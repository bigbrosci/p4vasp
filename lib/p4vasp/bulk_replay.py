"""Export the original Bulk request as standalone Python and an editable p4v command."""
from pathlib import Path
from pprint import pformat
import shlex

from p4vasp.bulk_geometry import parameters
from p4vasp.model_worker import bash_launcher


def bash_script(request):
    name, crystal, mode, values, repeat = parameters(request)
    command = ['p4v', 'bulk', name, crystal, mode]
    for key, value in values.items():
        command.extend((f'--{key}', str(value)))
    command.extend(('--repeat', *(str(count) for count in repeat)))
    return (
        '#!/usr/bin/env bash\nset -euo pipefail\n'
        '# Run: bash rebuild_bulk.sh [NEW_POSCAR_PATH]\n'
        'if ! command -v p4v >/dev/null 2>&1; then\n'
        + bash_launcher()
        + 'fi\n'
        + shlex.join(command) + ' -o "${1:-POSCAR.rebuilt}"\n'
    )


def python_script(result):
    name, crystal, mode, values, repeat = parameters(result['request'])
    request = dict(name=name, crystal=crystal, mode=mode, **values, repeat=repeat)
    source = Path(__file__).with_name('bulk_geometry.py').read_text(encoding='utf-8')
    header = f'''#!/usr/bin/env python3
"""Rebuild the saved bulk structure with ASE {result['ase_version']}.
Run: python rebuild_bulk.py [-o NEW_POSCAR_PATH]
The saved bulk parameters are in REQUEST below.
"""
'''
    tail = f'''

REQUEST = {pformat(request, sort_dicts=False)}
EXPECTED_ASE = {result['ase_version']!r}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-o', '--output', type=Path, default=Path('POSCAR.rebuilt'))
    args = parser.parse_args()
    try:
        result = build_bulk(REQUEST)
        if result['ase_version'] != EXPECTED_ASE:
            print('Warning: ASE version differs from the saved construction.', file=sys.stderr)
        output = args.output.expanduser()
        write_bulk_poscar(output, result['poscar'])
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(1, f'Bulk rebuild failed: {{error}}\\n')
    print(f'Saved {{output}}')


if __name__ == '__main__':
    main()
'''
    imports = 'import argparse\nfrom pathlib import Path\nimport sys\n'
    text = header + imports + source.split('\n', 1)[1] + tail
    compile(text, 'rebuild_bulk.py', 'exec')
    return text


def bulk_contents(result):
    return {
        'POSCAR': result['poscar'],
        'rebuild_bulk.py': python_script(result),
        'rebuild_bulk.sh': bash_script(result['request']),
    }
