"""Frozen DOS GUI/CLI diagnostics using only the public artificial fixture."""
from pathlib import Path
import runpy
import subprocess
import sys
from types import SimpleNamespace


def check_dos(out,pump,report):
    from p4vasp.gtk3 import Gtk
    from p4vasp.SystemPM import getSystem
    from p4vasp.gtk3.dos_analysis import DosAnalysis
    from p4vasp.dos_replay import save_scripts
    from p4vasp.model_worker import launch_options
    root=Path(sys._MEIPASS)
    fixture=runpy.run_path(str(root/'diagnostic-fixtures/dos_projected_fixtures.py'))
    source=fixture['projected_calculation'](out/'artificial-spdf',xml=True,with_f=True)
    applet=SimpleNamespace(system=getSystem(source/'DOSCAR'),queue_plot_redraw=lambda:None)
    window=Gtk.Window();window.set_default_size(540,700)
    panel=DosAnalysis(applet);window.add(panel);window.show_all()
    panel.mode.set_active(2);panel.selection.set_text('1')
    try:
        assert len(panel.orbital_rows)==3
        assert 'included' in panel.hint.caption.get_text()
        for filename in ('DOSCAR','vasprun.xml'):
            panel.set_system(getSystem(source/filename));panel.set_spin_channels(2);panel.set_spin('up')
            for shell in ('s','p','d','f','f_3,f3'):
                panel.set_orbitals(shell);panel.calculate.clicked();pump(lambda:panel.job is None,60)
                assert panel.result is not None,panel.status.get_text()
                assert len(panel.model)==4
                if shell.startswith('f'):assert abs(panel.result['rows'][0][1]-1)<1e-8
        py,sh=save_scripts(out/'f_analysis.py',panel.result)
        assert py.is_file() and sh.is_file() and 'p4vasp-console.exe' in sh.read_text()
        command=[str(Path(sys.executable).with_name('p4vasp-console.exe')),
                 str(source/'DOSCAR'),'1','f_3,f3','up','-6','0',str(out/'f_cli.csv')]
        run=subprocess.run(command,capture_output=True,text=True,timeout=90,**launch_options(command))
        assert run.returncode==0,run.stderr
        assert 'f-band center' in (out/'f_cli.csv').read_text()
        # Frozen Surface replay must work without access to the build checkout.
        command=[str(Path(sys.executable).with_name('p4vasp-console.exe')),'--surface-replay',
                 str(out/'Cu_surface/surface.json'),str(out/'surface_replayed')]
        run=subprocess.run(command,capture_output=True,text=True,timeout=90,**launch_options(command))
        assert run.returncode==0,run.stderr
        from p4vasp.Structure import Structure
        atoms=Structure(str(out/'surface_replayed/POSCAR'));atoms.setCartesian()
        assert len(atoms)==16 and abs(min(p[2] for p in atoms)-.1)<1e-10
        report['checks'].append('frozen s/p/d/f DOSCAR/XML GUI, f component ordering, paired exports, headless DOS and Surface replay')
    finally:
        window.destroy()
