"""Axis text formatting: roundoff, fine zoom and large/small scales."""
import unittest
from p4vasp.GraphPM import createGraph


class TickLabelsTest(unittest.TestCase):
    def test_roundoff_on_both_axes(self):
        graph=createGraph('dos')[0]
        for axis in (graph.xaxis,graph.yaxis):
            axis.major=.2
            self.assertEqual(axis.formatTick(3*.2),'0.6')
            self.assertEqual(axis.formatTick(7*.2),'1.4')
            self.assertEqual(axis.formatTick(-3*.2),'-0.6')
            self.assertEqual(axis.formatTick(-0.),'0')
            axis.major=.25
            self.assertEqual(axis.formatTick(.25),'0.25')

    def test_zoom_does_not_merge_neighboring_ticks(self):
        axis=createGraph('dos')[0].yaxis
        for start,step in [(1.,1e-8),(1e9,.2),(0.,2e-12)]:
            axis.major=step
            values=[start+i*step for i in range(5)]
            labels=[axis.formatTick(value) for value in values]
            self.assertEqual(len(set(labels)),len(values),labels)
            for value,label in zip(values,labels):
                self.assertLess(abs(float(label)-value),step*.01)

if __name__=='__main__':unittest.main()
