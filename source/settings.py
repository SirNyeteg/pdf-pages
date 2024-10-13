from pdf import PageDimension

from typing import Dict, Optional, Tuple, List

import os
import sys
import yaml


class Settings:
    width: int = 1024
    height: int = 400
    pageSizes: Dict[PageDimension, str]
    groupPages:bool = True
    error:Optional[str] = None
    bigPages:List[Tuple[int, int]]

    def __init__(self, path:str):
        self.pageSizes = {}
        self.bigPages = []
        self.parse(path)

    def parse(self, path:str):
        if not os.path.exists(path):
            return
        try:
            with open(path, "r") as file:
                data = yaml.load(file, Loader=yaml.Loader)
                if "dimensions" in data: 
                    for dimension in data["dimensions"]:
                        d = PageDimension(int(dimension["size"]["width"]), int(dimension["size"]["height"]))
                        if d in self.pageSizes:
                            self.error = f"Same dimension ({d.width}x{d.height}) present multiple times: {self.pageSizes[d]} and {dimension['name']}"
                            return
                        self.pageSizes[d] = dimension["name"]
                if "configuration" in data:
                    config = data["configuration"]
                    if "window-size" in config:
                        windowSize = config["window-size"]
                        if "width" in windowSize:
                            self.width = int(windowSize["width"])
                        if "height" in windowSize:
                            self.height = int(windowSize["height"])
                    if "group-pages" in config:
                        self.groupPages = bool(config["group-pages"])
                if "big-pages" in data:
                    for rule in data["big-pages"]:
                        self.bigPages.append((int(rule["min-short-side"]),int(rule["min-long-side"])))

        except Exception as e:
            self.error = f"settings.yaml cannot be opened:\n{e}"
