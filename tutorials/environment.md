## Dev
Install in this order:
1. python=3.x.0 (conda)
   ***remark:** (don't install any version with `3.x.y` where `y>0`)*, otherwise, `dvc` will break  ^54b08a
2. Pytorch with cuda=10.2 (conda)
3. Scipy, sklearn, pandas all latest version (conda)
4. networkx >=2.5 (below 2.5 are bugged [python 3.x - Import Error: can't import name gcd from fractions - Stack Overflow](https://stackoverflow.com/questions/66174862/import-error-cant-import-name-gcd-from-fractions) and [ImportError: cannot import name 'gcd' from 'fractions' for Python3.9 · Issue #1667 · snorkel-team/snorkel · GitHub](https://github.com/snorkel-team/snorkel/issues/1667)) which latest version is preferred (conda)
5. dvc (mamba)
   ***Remark:*** before installing `dvc`, install `mamba` using `conda-forge`. Then update `mamba` to latest version, first by pinning `python 3.x.0` in `~/anaconda3/envs/your_env_name/conda-meta/pinned` so that updating `mamba` does not update `python` which breaks `dvc` (see [[#^54b08a]]).