"""Portable, data-only image recipes; never execute commands from a preset."""
import itertools
import json
import math
import os
from pathlib import Path
import shlex
import sys
import tempfile

SCHEMA = 'p4vasp-image-view'
DEFAULTS = dict(view='top', turns=(), size=(1000,1000), radius_scale=.5, cell=True,
                transparent=True, force=True, model='spheres', brightness=1., bond_radius=.10,
                bond_factor=1.15, quality=2, material='matte', renderer='studio')
SETTINGS = set(DEFAULTS)-{'view','turns','force'}


def _number(value, positive=False):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
        raise ValueError('Preset numbers must be finite')
    if positive and value <= 0: raise ValueError('Preset value must be positive')
    return value


def validate(data):
    if not isinstance(data,dict) or data.get('schema') != SCHEMA or data.get('version') != 1:
        raise ValueError('Unsupported view preset schema/version')
    camera, settings, display = data['camera'], data['render'], data['display']
    matrix = camera['matrix']
    if len(matrix) != 4 or any(len(row) != 4 for row in matrix):
        raise ValueError('Preset camera matrix must be 4x4')
    for row in matrix:
        for value in row: _number(value)
    if list(matrix[3]) != [0,0,0,1]: raise ValueError('Preset matrix must be affine')
    for key in ('zoom','width','height'): _number(camera[key],True)
    if not isinstance(camera['perspective'],bool): raise ValueError('Invalid projection flag')
    if set(settings) != SETTINGS: raise ValueError('Preset render settings are incomplete or unknown')
    for key, choices in dict(model=('spheres','ball-stick','stick','space-filling'),
                             material=('matte','classic','glossy'), renderer=('studio','fast')).items():
        if settings[key] not in choices: raise ValueError('Invalid preset '+key)
    for key in ('brightness','radius_scale','bond_radius','bond_factor'): _number(settings[key],True)
    if type(settings['quality']) is not int or settings['quality'] not in (1,2,3,4):
        raise ValueError('Invalid preset quality')
    size = settings['size']
    if (len(size) != 2 or any(type(v) is not int or not 32 <= v <= 8192 for v in size)
            or size[0]*size[1] > 32000000): raise ValueError('Invalid preset image size')
    for key in ('cell','transparent'):
        if type(settings[key]) is not bool: raise ValueError('Invalid preset '+key)
    counts, hidden = display['repeat'], display['hidden']
    if len(counts) != 3 or any(type(n) is not int or not 1 <= n <= 10 for n in counts):
        raise ValueError('Preset repeats must be three integers in 1..10')
    if not isinstance(hidden,list) or any(type(i) is not int or i < 0 for i in hidden):
        raise ValueError('Invalid preset hidden atom indices')
    return data


def load(path):
    with open(path,encoding='utf-8') as handle: return validate(json.load(handle))


def make(camera, options, display):
    return validate(dict(schema=SCHEMA,version=1,camera=camera,
                         render={key: options.get(key,DEFAULTS[key]) for key in SETTINGS},display=display))


def scene_from_source(source, display):
    from p4vasp.render_cli import load_structure
    basis, positions, elements = load_structure(source)
    hidden, counts = set(display['hidden']), display['repeat']
    if hidden and max(hidden) >= len(positions):
        raise ValueError('Preset hidden atom index exceeds this structure; use a compatible structure or edit the preset')
    origins = [tuple(sum((n[i]-counts[i]//2)*basis[i][j] for i in range(3)) for j in range(3))
               for n in itertools.product(*(range(c) for c in counts))]
    points, labels = [], []
    for origin in origins:
        for i, position in enumerate(positions):
            if i in hidden: continue
            points.append(tuple(position[j]+origin[j] for j in range(3)))
            labels.append(elements[i])
    return basis, points, labels, origins


def poscar_text(base):
    basis, positions, elements = base
    species, counts = [], []
    for element in elements:
        element = element or 'X'
        if not species or species[-1] != element:
            species.append(element); counts.append(1)
        else: counts[-1] += 1
    lines = ['p4vasp export snapshot (Cartesian angstrom)','1']
    lines += [' '.join(format(v,'.17g') for v in row) for row in basis]
    lines += [' '.join(species),' '.join(map(str,counts)),'Cartesian']
    lines += [' '.join(format(v,'.17g') for v in row) for row in positions]
    return '\n'.join(lines)+'\n'


def bundle_paths(output):
    """Avoid overwriting unrelated companion files by choosing another prefix."""
    output = Path(output).absolute()
    for index in itertools.count(1):
        replay = '' if index == 1 else '.replay-'+str(index)
        prefix = str(output)+replay
        paths = [Path(prefix+'.POSCAR'), Path(prefix+'.view.json'),
                 output.parent/('command_for_'+output.stem+replay+
                                ('.ps1' if sys.platform == 'win32' else '.sh'))]
        if not any(path.exists() for path in paths): return paths


def command(source, output, preset):
    if sys.platform == 'win32':
        if getattr(sys, 'frozen', False):
            executable = Path(sys.executable).with_name('p4vasp-console.exe')
            args = [str(executable if executable.is_file() else Path(sys.executable))]
        else:
            from p4vasp import p4vasp_home
            args = [sys.executable, str(Path(p4vasp_home)/'p4v.py')]
        args += [str(source), '-o', str(output), '--preset', str(preset)]
        return '& ' + ' '.join("'"+arg.replace("'", "''")+"'" for arg in args)
    from p4vasp import p4vasp_home
    launcher = Path(p4vasp_home)/'p4v.sh'
    args = ['bash',str(launcher.resolve())] if launcher.is_file() else ['p4v']
    return shlex.join(args+[str(source),'-o',str(output),'--preset',str(preset)])


def save_bundle(paths, output, base, data):
    """Write companions after a successful PNG; filenames are newly reserved names."""
    source, preset, text = paths
    cmd = command(source,output,preset)
    script = ("$ErrorActionPreference = 'Stop'\n"+cmd+' @args\nexit $LASTEXITCODE\n'
              if sys.platform == 'win32' else
              '#!/usr/bin/env bash\nset -euo pipefail\n\n'+cmd+' \"$@\"\n')
    payloads = (poscar_text(base),json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+'\n',
                script)
    for path,payload in zip(paths,payloads):
        fd, temporary = tempfile.mkstemp(prefix='.p4v-recipe-',dir=path.parent)
        try:
            encoding = 'utf-8-sig' if path == text and sys.platform == 'win32' else 'utf-8'
            with os.fdopen(fd,'w',encoding=encoding) as handle:
                handle.write(payload)
                if path == text and sys.platform != 'win32': os.fchmod(handle.fileno(),0o755)
            # Exclusive publication: even a concurrent export cannot replace a companion.
            os.link(temporary,path)
        finally:
            os.unlink(temporary)
    return cmd
