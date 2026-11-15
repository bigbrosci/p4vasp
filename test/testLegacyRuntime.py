"""Actual thread-state and VAC numerical paths for the first legacy-API fixes."""
import importlib
import math
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np
from p4vasp.Property import Property
from p4vasp.Structure import Structure
from p4vasp.Selection import Selection
from p4vasp.schedule import Scheduler


class LegacyThreadTest(unittest.TestCase):
    def test_real_thread_lifecycle(self):
        prop=Property('thread-state');entered=threading.Event();release=threading.Event()
        def run():entered.set();release.wait(3)
        thread=threading.Thread(target=run);prop.thread=thread
        self.assertFalse(prop.isPending())
        try:
            thread.start();self.assertTrue(entered.wait(1));self.assertTrue(prop.isPending())
        finally:release.set();thread.join(2)
        self.assertFalse(thread.is_alive());self.assertFalse(prop.isPending())
        prop.thread=None;self.assertFalse(prop.isPending())

    def test_property_require_reads_once_and_notifies(self):
        module=importlib.import_module('p4vasp.Property')
        entered=threading.Event();release=threading.Event();finished=threading.Event();calls=[];notified=[]
        def read(prop):
            calls.append(prop.name);entered.set();release.wait(3);return 42
        def notify(prop):notified.append(prop.value);finished.set()
        prop=Property('worker',read=read)
        with patch.object(module,'has_threading',1):
            try:
                prop.require(notify);self.assertTrue(entered.wait(1))
                worker=prop.thread;self.assertTrue(prop.isPending())
                prop.require();self.assertIs(prop.thread,worker)
            finally:release.set();worker.join(2)
        self.assertTrue(finished.wait(1));self.assertFalse(prop.isPending())
        self.assertEqual(prop.get(),42);self.assertEqual(calls,['worker']);self.assertEqual(notified,[42])


class LegacyVacTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from p4vasp.gtk3 import Gtk
        if not Gtk.init_check()[0]:raise unittest.SkipTest('VAC applet import requires a GTK display.')

    def run_vac(self,multi,selected,skip):
        module=importlib.import_module('p4vasp.applet.VACApplet')
        cls=module.VACApplet
        frames=[]
        for i in range(6):
            frame=Structure();frame.basis[0][0]=frame.basis[1][1]=frame.basis[2][2]=10
            frame.setCarthesian();frame.appendAtom(0,[i*i*.05,i*.05,0]);frame.appendAtom(0,[2+i*.02,2,2])
            frames.append(frame)
        def system(name,seq):return SimpleNamespace(NAME=name,current=lambda key:name,CSTRUCTURE_SEQUENCE_L=seq,INITIAL_STRUCTURE=seq[0])
        systems=[system('part1',frames[:3]),system('part2',frames[3:])] if multi else [system('single',frames)]
        applet=cls.__new__(cls);applet.system=systems[0];applet.multi=multi
        applet.sel=Selection('1' if selected else '')
        applet.world=[SimpleNamespace(subtitle='')];enabled={}
        class Widget:
            def __init__(self,name):self.name=name
            def get_text(self):return str(skip)
            def set_sensitive(self,value):enabled[self.name]=value
        applet.xml=SimpleNamespace(get_widget=Widget);applet.updateGraph=lambda:None
        messages=[]
        driver=SimpleNamespace(status=lambda text:messages.append(text),message=lambda text:messages.append(text),step=lambda *args:None)
        schedule=Scheduler()
        with patch.object(module,'msg',return_value=driver),patch.object(module,'systemlist',return_value=systems),patch.object(module,'scheduleFirst',side_effect=schedule.scheduleFirst):
            schedule.schedule(applet.readVacGen());schedule.run()
        initial=skip+1
        expected=[]
        for i in range(initial,5):
            cosine=(4*initial*i+1)/(math.sqrt(4*initial*initial+1)*math.sqrt(4*i*i+1))
            expected.append(cosine if selected else (cosine+1)/2)
        np.testing.assert_allclose(applet.vac,expected,rtol=1e-12,atol=1e-12)
        self.assertEqual(len(applet.freq),0);self.assertTrue(all(enabled.values()))
        self.assertTrue(any(text.startswith('t(vac):') for text in messages))
        self.assertTrue(np.isfinite(applet.vac).all())

    def test_single(self):self.run_vac(False,False,0)
    def test_single_selected_and_skip(self):self.run_vac(False,True,1)
    def test_multi(self):self.run_vac(True,False,0)
    def test_multi_selected_and_skip(self):self.run_vac(True,True,1)


if __name__=='__main__':unittest.main()
