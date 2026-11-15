"""VAC FFT compatibility and boundary filtering against independent expectations."""
import importlib
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import numpy as np
from p4vasp.schedule import Scheduler


class LegacyFFTTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from p4vasp.gtk3 import Gtk
        if not Gtk.init_check()[0]:raise unittest.SkipTest('VAC import needs a GTK display.')
        cls.module=importlib.import_module('p4vasp.applet.VACApplet')

    def run_fft(self,count,window,filtered,signal=None):
        module=self.module;applet=module.VACApplet.__new__(module.VACApplet)
        applet.vac=np.cos(np.arange(count)*.4)+.1*np.sin(np.arange(count)*.8) if signal is None else signal
        applet.freq=[];applet.windowfunction=window;applet.showtype=1;applet.canvas=None
        applet.system=SimpleNamespace(PARAMETERS={'POTIM':2})
        applet.worlds=[[SimpleNamespace(),SimpleNamespace()] for _ in range(3)]
        applet.setGraphData=lambda data:None
        applet.setWorldAndData=lambda world,data:setattr(applet,'display_data',data)
        applet.viewAll=lambda:None;applet.update=lambda:None
        texts={'wleft_entry':'7','wright_entry':'7','wpolyn_entry':'3'}
        applet.xml=SimpleNamespace(get_widget=lambda key:SimpleNamespace(get_active=lambda:filtered,get_text=lambda:texts[key]))
        driver=SimpleNamespace(status=lambda *a:None,message=lambda *a:None,step=lambda *a:None,error=lambda text:self.fail(text))
        queue=Scheduler()
        with patch.object(module,'msg',return_value=driver),patch.object(module,'scheduleFirst',side_effect=queue.scheduleFirst):
            queue.schedule(applet.fftGen());queue.run()
        signal=applet.vac.copy();i=np.arange(count)
        if window==1:signal*=1-np.abs((i-.5*count)/(.5*count))
        elif window==2:signal*=.5*(1-np.cos(2*np.pi*i/count))
        elif window==3:signal*=1-((i-.5*count)/(.5*count))**2
        expected=np.abs(np.fft.fft(signal))
        if filtered:
            expected=np.array([np.polynomial.polynomial.polyval(j,np.polynomial.polynomial.polyfit(
                np.arange(max(0,j-7),min(count,j+8)),expected[max(0,j-7):min(count,j+8)],
                min(3,min(count,j+8)-max(0,j-7))-1)) for j in range(count)])
        np.testing.assert_allclose(applet.freq,expected,rtol=1e-10,atol=1e-10)
        output=applet.display_data[0][0]
        self.assertEqual(output.shape,(count//2,2))
        np.testing.assert_allclose(output[:,0],np.arange(count//2)/(count*2.997925e10*2e-15))
        scale=count*sum(1-((i-.5*count)/(.5*count))**2)
        np.testing.assert_allclose(output[:,1],2/scale*expected[:count//2]*.7,rtol=1e-10,atol=1e-10)
        return applet

    def test_known_cosine_spectrum(self):
        applet=self.run_fft(8,0,False,np.cos(2*np.pi*np.arange(8)/8))
        np.testing.assert_allclose(applet.freq,[0,4,0,0,0,0,0,4],atol=1e-12)

    def test_even_odd_and_all_windows(self):
        for count in (5,6):
            for window in range(4):
                with self.subTest(count=count,window=window):self.run_fft(count,window,False)

    def test_filter_larger_than_signal(self):
        for count in (3,4,5):
            with self.subTest(count=count):self.run_fft(count,0,True)

    def test_invalid_filter_preserves_result(self):
        applet=self.module.VACApplet.__new__(self.module.VACApplet)
        applet.vac=np.ones(5);applet.freq=[17];errors=[]
        applet.xml=SimpleNamespace(get_widget=lambda key:SimpleNamespace(get_active=lambda:True,get_text=lambda:'-1'))
        with patch.object(self.module,'msg',return_value=SimpleNamespace(status=lambda *a:None,error=errors.append)):
            list(applet.fftGen())
        self.assertEqual(applet.freq,[17]);self.assertEqual(len(errors),1)

    def test_too_short_vac_preserves_result(self):
        for samples in ([],[1]):
            applet=self.module.VACApplet.__new__(self.module.VACApplet)
            applet.vac=samples;applet.freq=[17];errors=[]
            with patch.object(self.module,'msg',return_value=SimpleNamespace(status=lambda *a:None,error=errors.append)):
                list(applet.fftGen())
            self.assertEqual(applet.freq,[17]);self.assertEqual(len(errors),1)

    def test_boundary_polynomial(self):
        for count in (2,5,15):
            x=np.arange(count,dtype=float);values=x*x+2*x+1
            expected=values
            np.testing.assert_allclose(self.module.savitzky_golay_filter(values,7,7,3),expected,atol=1e-9)


if __name__=='__main__':unittest.main()
