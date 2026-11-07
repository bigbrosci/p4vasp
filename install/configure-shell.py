#!/usr/bin/env python3
"""Update only p4vasp's managed alias block; never execute shell configuration."""
from pathlib import Path
import os
import shutil
import stat
import sys
import tempfile

BEGIN = '# >>> p4vasp command >>>'
END = '# <<< p4vasp command <<<'


def configure(filename, alias):
    path=Path(filename).expanduser().resolve()
    existed=path.exists()
    original=path.read_bytes() if existed else b''
    text=original.decode('utf-8',errors='surrogateescape')
    lines=text.splitlines(keepends=True)
    starts=[i for i,line in enumerate(lines) if line.rstrip('\r\n')==BEGIN]
    ends=[i for i,line in enumerate(lines) if line.rstrip('\r\n')==END]
    if starts or ends:
        if len(starts)!=1 or len(ends)!=1 or starts[0]>=ends[0]:
            raise ValueError('Incomplete/duplicate p4vasp markers; review the configuration before retrying.')
        updated=''.join(lines[:starts[0]])+BEGIN+'\n'+alias+'\n'+END+'\n'+''.join(lines[ends[0]+1:])
    else:
        updated=text+('' if not text or text.endswith('\n') else '\n')+'\n'+BEGIN+'\n'+alias+'\n'+END+'\n'
    content=updated.encode('utf-8',errors='surrogateescape')
    if content==original:
        print('Shell alias already configured.')
        return
    temporary=None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent,prefix=path.name+'.p4vasp-',delete=False) as output:
            temporary=Path(output.name)
            output.write(content);output.flush();os.fsync(output.fileno())
        os.chmod(temporary,stat.S_IMODE(path.stat().st_mode) if existed else 0o600)
        if existed:
            with tempfile.NamedTemporaryFile(dir=path.parent,prefix=path.name+'.p4vasp-backup-',delete=False) as backup:
                backup_path=Path(backup.name)
            shutil.copy2(path,backup_path)
            print('Shell config backup: '+str(backup_path))
        os.replace(temporary,path)
        print('Shell alias configured: '+str(path))
    finally:
        if temporary is not None and temporary.exists():temporary.unlink()


if __name__=='__main__':
    try:
        if len(sys.argv)!=3:raise ValueError('Usage: configure-shell.py RC_FILE ALIAS_DEFINITION')
        configure(sys.argv[1],sys.argv[2])
    except Exception as error:
        print('Automatic shell setup failed: '+str(error),file=sys.stderr)
        sys.exit(1)
