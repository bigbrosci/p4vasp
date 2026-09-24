"""Run isolated startup checks for every GTK applet.

Pass --include-glut to additionally check the separate GLUT k-point viewer.
"""
import argparse
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'lib'))
from p4vasp.applet.appletlist import appletlist


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--include-glut', action='store_true')
    args = parser.parse_args()
    failed = []
    passed = 0
    for name in appletlist():
        if name.endswith('.KpointsViewerApplet') and not args.include_glut:
            print('SKIP KpointsViewerApplet (GLUT/OpenGL; use --include-glut)')
            continue
        try:
            result = subprocess.run(
                [sys.executable, str(root / 'test/gtk3_applet_smoke.py'), name],
                capture_output=True, text=True, timeout=30)
            if result.returncode or 'RESULT PASS' not in result.stdout:
                failed.append(name)
                print(result.stdout + result.stderr)
            else:
                passed += 1
                print('PASS', name.rsplit('.', 1)[-1], flush=True)
        except subprocess.TimeoutExpired:
            failed.append(name)
            print('TIMEOUT', name)
    print('%d passed; %d failed' % (passed, len(failed)))
    return bool(failed)


if __name__ == '__main__':
    sys.exit(main())
