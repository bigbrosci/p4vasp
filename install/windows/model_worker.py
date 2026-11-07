"""Frozen standalone Windows ASE/RDKit worker; communicates only over JSON pipes."""
import json
import sys


def main():
    kind=sys.argv[1] if len(sys.argv)>1 else ''
    try:
        if kind=='--versions':
            import ase,rdkit
            print(json.dumps({'ase':ase.__version__,'rdkit':rdkit.__version__,'python':sys.version}))
            return 0
        request=json.load(sys.stdin)
        if kind=='--bulk':
            from p4vasp.ase_bulk import build_bulk
            result={'ok':True,'result':build_bulk(request)}
        elif kind=='--smiles':
            from p4vasp.smiles_builder import build_geometry
            result=build_geometry(request.get('smiles'))
        else:raise ValueError('Use --bulk or --smiles with a JSON request on stdin.')
        print(json.dumps(result,ensure_ascii=True),flush=True)
        return 0
    except Exception as error:
        print(json.dumps({'ok':False,'error':str(error)}),flush=True)
        return 2


if __name__=='__main__':sys.exit(main())
