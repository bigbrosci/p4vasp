"""Indexed XDATCAR frames, using the existing POSCAR geometry parser."""
from collections.abc import Sequence
from io import StringIO
import math
import re
from p4vasp.Structure import Structure

MARKER = re.compile(r'^\s*(Direct|Cartesian)\s+configuration\s*=\s*\d+\s*$',re.I)


class XdatcarSequence(Sequence):
    """Keep file offsets, not thousands of resident Structure objects."""
    def __init__(self,path):
        self.path=path
        self.frames=[]
        with open(path) as source:
            first=source.readline()
            while first:
                header=[first]+[source.readline() for _ in range(5)]
                try:
                    counts=[int(v) for v in header[-1].split()]
                except ValueError:
                    header.append(source.readline())
                    try:counts=[int(v) for v in header[-1].split()]
                    except ValueError:raise ValueError('Invalid XDATCAR atom counts.')
                if not counts or min(counts)<0 or sum(counts)<=0:
                    raise ValueError('Invalid XDATCAR atom counts.')
                count=sum(counts);text=''.join(header)
                line=source.readline()
                while True:
                    while line and not line.strip():line=source.readline()
                    match=MARKER.match(line)
                    if not match:break
                    offset=source.tell()
                    for _ in range(count):
                        fields=source.readline().split()
                        try:valid=len(fields)==3 and all(math.isfinite(float(v)) for v in fields)
                        except ValueError:valid=False
                        if not valid:raise ValueError('Incomplete or invalid XDATCAR frame %d.'%(len(self.frames)+1))
                    self.frames.append((text,match[1],offset,count))
                    line=source.readline()
                first=line  # Some variable-cell trajectories repeat the header.
        if not self.frames:raise ValueError('No XDATCAR configurations found.')
        # Check the header with the same parser used for every displayed frame.
        self[0]

    def __len__(self):return len(self.frames)

    def __getitem__(self,index):
        if isinstance(index,slice):return [self[i] for i in range(*index.indices(len(self)))]
        header,mode,offset,count=self.frames[index]
        with open(self.path) as source:
            source.seek(offset)
            coordinates=''.join(source.readline() for _ in range(count))
        structure=Structure()
        structure.read(StringIO(header+mode+'\n'+coordinates))
        return structure
