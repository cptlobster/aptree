# APTree
GUI flowcharting tool for apt package dependencies

## Setting up

Clone the repo!

```shell
git clone https://github.com/cptlobster/aptree
cd aptree
```

First you will need to install the graphviz program for creating trees.

```shell
sudo apt install graphviz graphviz-dev
```

Then, install Python dependencies. This can be done in a virtual environment if you so desire.

```shell
# replace this with your desired virtual environment
python -m venv venv

python3 -m pip install -r requirements.txt
```

## Usage

To start:

```shell
# replace this with your desired virtual environment
source .venv/bin/activate
python3 main.py
```
In the new window, enter a package, or comma-separated list of packages, and click "Update". The progress bar on the bottom of the window will update as it parses packages, and then it will render as a PDF.

To view the package list, open up the PDF in the `doctest-output` folder. If you want to generate a new tree, you can repeat the first step, and refresh the PDF in your browser when it's complete.

## Config

Coming soon.

## To Do

 - Interface
   - Add tree display on main interface
     - scrollable, zoomable image(?) or canvas(?)
   - setup links on tree nodes
     - focus this node on click?
     - get details?
     - open details on package archives (i.e. packages.ubuntu.com)?
   - Add config checkboxes on main interface
   - display legend on tree interface
 - Backend
   - Speed up parser
     - Somehow use something other than `apt-cache depends`
     - Cache package dependencies somehow
   - Parallelize Tk, parser, and tree renderer
     - update tree live during render possibly? (might be performance heavy, could ratelimit somehow)
   - Add ability to limit recurse level for certain types
 - Further functionality (way far off)
   - Add other package manager dependencies (not just these, maybe others?)
     - pip
     - arch
     - nodejs
 - Bugs
   - does not close with X button (need to kill script from CLI)
   - moving window while rendering may or may not break script
   - find out if any other weird bugs exist on a real linux system

Let me know if there's any suggestions to add to the list, or any other bugs you notice! I developed this within WSL (I know, a crime) so it's entirely possible things will work (or won't work) on a real Linux system.

## Licensing

This program is licensed under the GNU General Public License, Version 3. Please read (COPYRIGHT.md) for the full license.
