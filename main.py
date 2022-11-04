# Copyright (c) 2022. This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with this program.  If not,
# see <https://www.gnu.org/licenses/>.

import subprocess
import asyncio
from concurrent.futures import ThreadPoolExecutor
from icecream import ic
from tkinter import *
from tkinter.ttk import *
import re
import graphviz
import time as t
import numpy as np
import sys


class Dependency():
    def __init__(self, name: str):
        global config
        self.name = name
        self.packages = {
            "depends": [],
            "predepends": [],
            "conflicts": [],
            "recommends": [],
            "suggests": [],
            "breaks": [],
            "replaces": []
        }

    def parse(self):
        all_pkgs = []
        tree = subprocess.run(["apt-cache", "depends", self.name], capture_output=True, universal_newlines=True).stdout
        for i in tree.split("\n"):
            match = re.match(r" [ |](\w*): ([^<]\S*[^>])", ic(i))
            if match:
                m = match[1].lower()
                if m in self.packages.keys():
                    self.packages[m].append(match[2])
                    if config["enabled"][m]:
                        all_pkgs.append(match[2])
        ic(self.packages)
        return all_pkgs


class App(Tk):
    def __init__(self, loop, executor, interval=1 / 240):
        super().__init__()
        self.title("APTree")
        self.loop = loop
        self.executor = executor
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.tasks = []
        self.unchecked_pkgs = []
        self.oneshot_pkgs = []
        self.packages = []
        self.package_names = []
        self.tasks.append(loop.create_task(self.updater(interval)))
        self.start = 0
        self.end = 0
        self.rendered = True

        global config
        config = {
            "enabled": {
                "depends": True,
                "predepends": True,
                "recommends": False,
                "conflicts": False,
                "suggests": False,
                "breaks": False,
                "replaces": False
            },
            "oneshot": {
                "depends": False,
                "predepends": False,
                "recommends": True,
                "conflicts": False,
                "suggests": True,
                "breaks": False,
                "replaces": False
            },
            "style": {
                "nodes": {

                },
                "lines": {
                    "depends": {
                        "color": "red"
                    },
                    "predepends": {
                        "color": "red",
                        "style": "dotted"
                    },
                    "recommends": {
                        "color": "green"
                    },
                    "conflicts": {
                        "color": "gray",
                        "style": "dotted"
                    },
                    "suggests": {
                        "color": "blue"
                    },
                    "breaks": {
                        "color": "gray"
                    },
                    "replaces": {
                        "color": "purple"
                    }
                }
            }
        }

        # make UI
        self.toppkg = StringVar()
        self.progress = 0

        self.pkgframe = Frame(self)
        self.pkgtext = Entry(self.pkgframe, textvariable=self.toppkg)
        self.pkgupdate = Button(self.pkgframe, text="Update", command=self.update_tree)

        self.pkgtext.pack(side=LEFT, fill=BOTH, expand=1, anchor=N)
        self.pkgupdate.pack(side=LEFT, fill=Y, anchor=E)
        self.pkgframe.pack(side=TOP, fill=X, anchor=N)

        self.tree = Canvas(self)
        self.tree.pack(side=TOP, fill=BOTH, anchor=CENTER)

        self.pbar = Progressbar(self, value=0, maximum=100, mode="determinate")
        self.pbar.pack(side=BOTTOM, fill=X, anchor=CENTER)

        # make graph
        self.dot = graphviz.Digraph()
        self.dot.graph_attr['rankdir'] = 'TB'
        self.dot.node_attr['shape'] = 'box'

        loop.run_forever()

    async def updater(self, interval):
        while True:
            if len(self.unchecked_pkgs) > 0:
                await self.parse_pkg()
                print(self.package_names)
            elif not self.rendered:
                await self.on_finish()

            self.pbar['value'] = ic(self.progress)
            self.update()
            await asyncio.sleep(interval)

    def close(self):
        for task in self.tasks:
            task.cancel()
        self.loop.stop()
        self.destroy()

    def get_pkg_id_by_name(self, packages, name: str):
        for i in range(0, len(packages)):
            if packages[i].name == name:
                return i
        else:
            return -1

    def update_tree(self):
        self.tasks.append(self.loop.create_task(self.update_tree_a()))

    async def parse_pkg(self):
        self.progress = (round(len(self.package_names) / (len(self.package_names) + len(self.unchecked_pkgs)) * 100))
        pkg = self.unchecked_pkgs.pop(0)
        self.package_names.append(pkg)
        self.packages.append(Dependency(pkg))
        pkgs = self.packages[-1].parse()
        parsed = [i for i in pkgs if (i not in self.package_names) and (i not in self.unchecked_pkgs)]
        self.unchecked_pkgs = [*self.unchecked_pkgs, *parsed]
        self.dot.node(str(len(self.packages) - 1), pkg)
        return

    async def update_tree_a(self):
        print("Starting render!")
        self.dot.clear()
        self.dot.graph_attr['rankdir'] = 'TB'
        self.dot.node_attr['shape'] = 'box'
        self.rendered = False
        self.start = t.time()
        # get package tree
        ic(self.toppkg.get())
        self.unchecked_pkgs = self.toppkg.get().split(",")
        self.packages = []
        self.package_names = []
        return

    async def on_finish(self):
        print("Visualizing nodes...")
        # create graphviz
        for i in range(0, len(self.packages)):
            self.progress = (round(i / len(self.packages) * 100))
            for j in [k for k in config["enabled"].keys() if config["enabled"][k]]:
                for k in self.packages[i].packages[j]:
                    self.dot.edge(str(i), str(self.get_pkg_id_by_name(self.packages, k)), **config["style"]["lines"][j])

        self.dot.render(directory='doctest-output')
        self.end = t.time()
        elapsed = (self.end - self.start)
        self.rendered = True
        print(f"Rendered! Took {elapsed}s")
        return

if __name__ == "__main__":
    ic.disable()
    executor = ThreadPoolExecutor(4)
    loop = asyncio.get_event_loop()
    app = App(loop, executor)
    loop.run_forever()
    loop.close()
