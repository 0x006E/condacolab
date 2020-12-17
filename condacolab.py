"""
condacolab.py
Install Conda and friends on Google Colab, easily
"""

import shutil
from urllib.request import urlopen
from subprocess import call
import os
import sys
from pathlib import Path


def install(prefix="/usr/local"):
    """
    Install Miniconda
    """
    installer_url = r"https://github.com/jaimergp/miniforge/releases/download/refs%2Fpull%2F1%2Fmerge/Mambaforge-colab-Linux-x86_64.sh"
    print(f"Downloading {installer_url}...")
    installer_fn = "_miniconda_installer_.sh"
    with urlopen(installer_url) as response, open(installer_fn, "wb") as out:
        shutil.copyfileobj(response, out)
    call(["bash", installer_fn, "-bfp", prefix])
    os.unlink(installer_fn)

    print("Configuring pinnings...")
    cuda_version = ".".join(os.environ.get("CUDA_VERSION", "*.*.*").split(".")[:2])
    prefix = Path(prefix)
    condameta = prefix / "conda-meta"
    condameta.mkdir(parents=True, exist_ok=True)
    pymaj, pymin = sys.version_info[:2]

    with open(condameta / "pinned", "a") as f:
        f.write(f"python {pymaj}.{pymin}.*\n")
        f.write(f"python_abi {pymaj}.{pymin}.* *cp{pymaj}{pymin}*\n")
        f.write(f"cudatoolkit {cuda_version}.*\n")

    with open(prefix / ".condarc", "a") as f:
        f.write("always_yes: true\n")

    print("Injecting site-packages...")
    with open("/etc/ipython/ipython_config.py", "a") as f:
        f.write("c.InteractiveShellApp.exec_lines = [\n")
        f.write('  "import sys",\n'),
        f.write(f'  "sys.path.insert(0, f"{prefix}/lib/python{pymaj}.{pymin}/site-packages")",\n')
        f.write("]\n")

    print("Reloading kernel with injected environment...")
    os.environ["LD_LIBRARY_PATH"] = f"/usr/local/lib:{os.environ.get('LD_LIBRARY_PATH', '')}"
    os.execve(sys.executable, [sys.executable] + sys.argv, os.environ)