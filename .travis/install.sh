#!/bin/bash

set -e
set -x

if [[ "$(uname -s)" == 'Darwin' ]]; then
    # Install PyEnv
    git clone --depth 1 https://github.com/yyuu/pyenv.git ~/.pyenv
    PYENV_ROOT="$HOME/.pyenv"
    PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"

    case "${TOXENV}" in
        py26)
            pyenv install 2.6.9
            pyenv global 2.6.9
            ;;
        py27)
            export PATH="/Users/travis/Library/Python/2.7/bin:$PATH"
            curl -O https://bootstrap.pypa.io/get-pip.py
            python get-pip.py --user
            ;;
        py35)
            pyenv install 3.5.6
            pyenv global 3.5.6
            ;;
        py36)
            pyenv install 3.6.6
            pyenv global 3.6.6
            ;;
        py37)
            pyenv install 3.7.0
            pyenv global 3.7.0
            ;;
        py38)
            pyenv install 3.8-dev
            pyenv global 3.8-dev
            ;;
    esac
    pyenv rehash
    pip install --user -U setuptools
    pip install --user virtualenv
    case "${TOXENV}" in
        py27)
            pip install --user tox
            ;;
        *)
            pip install tox
            ;;
    esac
else
    pip install virtualenv
    pip install tox
fi


