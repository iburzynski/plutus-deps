import json
import os
import subprocess


def format_subdir(s):
    return "\n    " + s

def format_comment(c):
    return "\n-- " + c


deps_f = open('plutusDeps.json')
data = json.load(deps_f)
deps_f.close()

common_f = open('../cabal.project.common')
common = common_f.read() + "\n"
common_f.close()

proj_f = open('../cabal.project.temp', 'w')
proj_f.write(f"index-state: {data['indexState']}\n")
proj_f.write(common)

if 'constraints' in data.keys():
    constraints = f"constraints:{''.join(map(format_subdir, data['constraints']))}"
    proj_f.write(constraints)

for dep in data["deps"]:
    repo = dep["location"]
    tag = dep["tag"]
    print(f"Hashing dependency {repo}...")
    bashCommand = f"nix-prefetch-git {repo} {tag}"
    proc = subprocess.run(
        [bashCommand],
        shell=True,
        check=True,
        capture_output=True,
    )
    out = json.loads(proc.stdout.decode("UTF-8"))
    tag = out["rev"] if tag == "" else tag
    subdir = f"\n  subdir:{''.join(map(format_subdir, dep['subdir']))}" if 'subdir' in dep.keys() else ''
    comments = f"{''.join(map(format_comment, dep['comments']))}"
    cabalDep = f"""{comments}
source-repository-package
  type: git
  location: {repo}
  tag: {tag}{subdir}
  --sha256: {out["sha256"]}
"""
    proj_f.write(cabalDep)

proj_f.close()
os.remove('../cabal.project')
os.rename('../cabal.project.temp', '../cabal.project')