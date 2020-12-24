# mp4gop
Shows GOP for frames inside MP4 container


# How to install

### Mac OS X:

```
brew install pyenv pyenv-virtualenv
export PY_VERSION=`pyenv install --list | grep " 3\." | grep -v '\-dev' | tail -n 1 | sed 's/ //g'`
export VENV_NAME=mp4gop-$PY_VERSION
pyenv install -s $PY_VERSION
pyenv virtualenv $PY_VERSION $VENV_NAME
pyenv activate $VENV_NAME

brew install yajl
pip3 install jsonslicer
```

# How to run

```
env VENV_NAME=`pyenv virtualenvs --bare | grep -E '^mp4gop' | sort | tail -n1`
pyenv activate $VENV_NAME
./show_gop_structure.py <path-to-mp4>
```
