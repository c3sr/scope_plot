Contributors
------------

## Author & Maintainer

* Abdul Dakkak <dakkak@illinois.edu>
* Carl Pearson <pearson@illinois.edu>

## Contributors

In chronological order:

* Abdul Dakkak <dakkak@illinois.edu>
* Carl Pearson <pearson@illinois.edu>

## Generating a Release

See [RELEASE.md](RELEASE.md) for instructions on how to create a new release.

## Development Environment

Install the system python and python3

```
sudo apt install -y python python-dev python3 python3-dev python3-distutils
```

Install pyenv, possibly with the [pyenv-installer](https://github.com/pyenv/pyenv-installer):

```bash
curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
echo 'eval "$(pyenv virtualenv-init -)"' ~/.zshrc
```

You may need to fix [common build problems](https://github.com/pyenv/pyenv/wiki/common-build-problems) for pyenv:

    sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev Libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev


Install pip

Don't install the system pip. Instead, use `get-pip.py`.
This is because using pip to upgrade the system pip can cause problems.
Install for both python2 and python3, if desired.

    wget https://bootstrap.pypa.io/get-pip.py
    python get-pip.py --user

Probably add $HOME/.local/bin to the PATH.

    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc

Install pipenv

    pip install --user pipenv

Add PIPENV_VENV_IN_PROJECT to the environment. This puts the .venv directory in the directory you run pipenv from, not in .local/share/virtualenvs.

    echo 'export PIPENV_VENV_IN_PROJECT=1' >> ~/.zshrc

Install tox

    pip install --user tox

Install multiple pythons and make them local in the `scope_plot` directory so tox can find them.

    pyenv install 3.5.5
    pyenv install 3.7.0
    pyenv local 3.5.5 3.7.0

Run tox.
It should pick up the different python versions installed with pyenv.

    tox