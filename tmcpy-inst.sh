#!/bin/bash

# tmc.py (https://github.com/JuhaniImberg/tmc.py) installer script
#
# Author: Markus Holmström (MawKKe) | markus dot holmstrom2 ät gmail.com
# Date: 2014/08/17
#
# Needs python3.2+ and virtualenv to be installed
#
# Ubuntu and others: apt-get install python-virtualenv
#
# Mac users: install virtualenv with this guide:
# http://docs.python-guide.org/en/latest/starting/install/osx/
#
# Windows users: install linux.
#

command -v python3 >/dev/null 2>&1 || { echo >&2 "Using tmc.py requires python3. Aborting."; exit 1; }
command -v virtualenv >/dev/null 2>&1 || { echo >&2 "Using tmc.py requires virtualenv. Aborting."; exit 1; }

DOCSURL="https://juhaniimberg.github.io/tmc.py/"

VENVPATH=$HOME/.venv_tmc
BINPATH=$HOME/.local/bin

PATHMODIFY='export PATH=$PATH:$HOME/.local/bin'

function pipinstall-tmcpy() {
    # installs or upgrades
    $VENVPATH/bin/pip -q install --upgrade tmc;
}

function uninstall-tmcpy() {
    # simply remove venv and symlinks
    [ -f $BINPATH/tmc ] && { echo "Removing symlink $BINPATH/tmc"; rm $BINPATH/tmc; }
    [ -d $VENVPATH ] && { echo "Removing $VENVPATH"; rm -r $VENVPATH; }
}

function append_path() {
    # Would be perfect if all shells source .profile, but AFAIK they do not..
    echo ">>> Appending '$PATHMODIFY' to ~/.profile and ~/.zprofile"
    echo $PATHMODIFY >> $HOME/.profile
    echo $PATHMODIFY >> $HOME/.zprofile # Aalto Ubuntu's have zsh as default shell
}

function create_venv() {
    # create virtualenv just for tmc.py
    echo "Creating virtualenv into $VENVPATH"
    virtualenv --python=python3 $VENVPATH -q;
}

function create_symlink() {
    # relink in case the venv path changed..
    [ -f $BINPATH/tmc ] && { echo "Removing old symlink $BINPATH/tmc"; rm $BINPATH/tmc; }

    echo "Creating symlink to $BINPATH"
    ln -s $VENVPATH/bin/tmc $BINPATH/
}

function hrline() {
    echo "---------------------------------"
}

# Fresh install
function install-tmcpy() {

    create_venv

    pipinstall-tmcpy

    mkdir -p $BINPATH

    create_symlink

    hrline
    echo "In order to be able to use tmc.py next time you log in,"
    echo "'$BINPATH' must be added to you PATH environment variable."
    echo
    echo "Some users might want to make changes to PATH manually,"
    echo "but the installer can make necessary modifications for you."
    echo "If you have no clue what all this is about,"
    echo "just hit return (or answer 'y') and enjoy the ride."
    echo
    read -p "Proceed to make automatic modifications? [y/n] " yn;
    hrline
    case $yn in
        [Nn]* ) echo "Alright then! Make sure you add the line:" ;
                echo "  $PATHMODIFY";
                echo "to one of your shell's configuration files (.profile, .bash_profile, .bashrc or similar)" ;;
        * ) append_path ;;
    esac

    hrline
    echo "Installing tmc.py was successful!"
    echo
    echo "Now, to start using tmc.py, please run command"
    echo "  $PATHMODIFY"
    echo "or just log out and back in again!"
    echo
    echo "Also, don't forget to run 'tmc init'!"
    echo
    echo "Documentation is available at $DOCSURL"
    echo "Thanks for using tmc.py!"

    # Just in case..
    export PATH=$PATH:$HOME/.local/bin
}
echo "Running tmc.py installer"
echo "------------------------"
if [ -d $VENVPATH ] || [ -f $BINPATH/tmc ]
then
    while true; do
        echo "tmc.py seems to be already installed."
        read -p "Upgrade (u), Reinstall(r), Uninstall(d) or Quit(q)? " choosed;
        hrline
        case $choosed in
            [Uu]* ) pipinstall-tmcpy; exit 0;;
            [Rr]* ) uninstall-tmcpy; break;;
            [Dd]* ) uninstall-tmcpy; exit 0;;
            [Qq]* ) exit;;
            * ) echo "Please answer u,r,d or q";;
        esac
    done
fi
install-tmcpy

exit 0;
