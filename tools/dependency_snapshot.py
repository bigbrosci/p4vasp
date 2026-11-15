#!/usr/bin/env python3
"""Read-only dependency metadata snapshot. Run with the interpreter being recorded."""
import argparse
from datetime import datetime,timezone
import hashlib
from importlib import metadata
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import sysconfig

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/'doc/dependencies/catalog.json'
KINDS={'runtime','feature','transitive','build','development','legacy'}


def canonical(name):
    return re.sub(r'[-_.]+','-',name).lower()


def validate(catalog):
    if catalog.get('schema_version')!=1:raise ValueError('Unsupported catalog schema.')
    profiles=set(catalog['profiles']);seen=set()
    for group in ('python','native','tools','vendored','legacy'):
        for item in catalog[group]:
            if item['id'] in seen:raise ValueError('Duplicate dependency id: '+item['id'])
            seen.add(item['id'])
            if item['kind'] not in KINDS:raise ValueError('Unknown dependency kind.')
            if not item['purpose'] or not item['sources']:raise ValueError('Missing purpose/source.')
            for source in item['sources']:
                path=ROOT/source
                if not path.resolve().is_relative_to(ROOT) or not path.is_file():
                    raise ValueError('Missing or invalid source: '+source)
            if group=='python':
                if not item['distribution'] or not item['profiles'] or not set(item['profiles'])<=profiles:
                    raise ValueError('Invalid Python distribution/profile.')


def collect(catalog,profile):
    """Metadata only: do not import dependencies, run installers or infer usage."""
    if profile not in catalog['profiles']:raise ValueError('Unknown profile: '+profile)
    packages=[]
    for dist in metadata.distributions():
        name=dist.metadata.get('Name')
        if name:
            packages.append({'name':name,'version':dist.version,
                             'requires_dist':sorted(dist.requires or [])})
    packages.sort(key=lambda d:(canonical(d['name']),d['version']))
    versions={canonical(p['name']):p['version'] for p in packages}
    declared=[]
    for item in catalog['python']:
        if profile in item['profiles']:
            version=versions.get(canonical(item['distribution']))
            declared.append({'id':item['id'],'distribution':item['distribution'],
                             'kind':item['kind'],'version':version,
                             'status':'metadata-present' if version is not None else 'metadata-not-found'})
    try:
        revision=subprocess.run(['git','-C',str(ROOT),'rev-parse','HEAD'],capture_output=True,
                                text=True,timeout=5,check=True).stdout.strip()
    except (OSError,subprocess.SubprocessError):revision=None
    return {'schema_version':1,'captured_at_utc':datetime.now(timezone.utc).isoformat(),
            'profile':profile,'source_revision':revision,
            'catalog_sha256':hashlib.sha256(CATALOG.read_bytes()).hexdigest(),
            'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'platform':{'system':platform.system(),'machine':platform.machine()},
            'python':{'version':platform.python_version(),'implementation':platform.python_implementation(),
                      'soabi':sysconfig.get_config_var('SOABI')},
            'scope':'All discoverable distribution metadata in this interpreter, not a minimum dependency set or lockfile.',
            'limits':['No dependency import or functional check. Missing metadata need not mean missing system library.',
                      'Requirements include raw markers/extras; they are not a resolved active dependency graph.',
                      'No native-library, operating-system package or frozen-archive inventory.'],
            'declared':declared,'distributions':packages}


def main(argv=None):
    catalog=json.loads(CATALOG.read_text(encoding='utf-8'));validate(catalog)
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true',help='Validate catalog sources/structure without probing packages.')
    parser.add_argument('--profile',choices=sorted(catalog['profiles']))
    parser.add_argument('--output',type=Path,help='Create a new UTF-8 JSON file; never overwrite an existing snapshot.')
    args=parser.parse_args(argv)
    if args.check:
        if args.output or args.profile:parser.error('--check does not accept --profile/--output.')
        print('Dependency catalog structure and source references OK.');return
    if not args.profile:parser.error('Select the interpreter role with --profile.')
    data=collect(catalog,args.profile)
    output=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x',encoding='utf-8',newline='\n') as handle:handle.write(output)
        print('Snapshot saved:',args.output)
    else:print(output,end='')


if __name__=='__main__':main()
