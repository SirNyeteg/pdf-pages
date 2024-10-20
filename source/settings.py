from pdf import PageDimension

from typing import Dict, Optional, Tuple, List

import os
import sys
import yaml


class Rule:
    def __init__(self, minShort:Optional[int], maxShort:Optional[int],
                 minLong:Optional[int], maxLong:Optional[int]):
        self.minShort = minShort
        self.maxShort = maxShort
        self.minLong = minLong
        self.maxLong = maxLong

    def match(self, short:int, long:int) -> bool:
        if self.minShort is not None and short < self.minShort:
            return False
        if self.maxShort is not None and short > self.maxShort:
            return False
        if self.minLong is not None and long < self.minLong:
            return False
        if self.maxLong is not None and long > self.maxLong:
            return False
        return True

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"Rule({str(self.minShort)},{str(self.maxShort)},{str(self.minLong)},{str(self.maxLong)})"


class Filter:
    def __init__(self, text:str, rules:List[Rule]):
        self.text = text
        self.rules = rules

    def match(self, short:int, long:int) -> bool:
        return any([r.match(short, long) for r in self.rules])


class Dictionary:
    def __init__(self, name:str):
        self.name = name
        self.words:Dict[str, str] = {}

    def addWord(self, id:str, word:str):
        self.words[id] = word

    def getWord(self, id:str) -> str:
        if id in self.words:
            return self.words[id]
        else:
            return id

class Settings:
    width: int = 1024
    height: int = 400
    pageSizes: Dict[PageDimension, str]
    groupPages:bool = True
    error:Optional[str] = None
    filters:List[Filter] = []
    dictionary:Dictionary = Dictionary("default")

    def __init__(self, path:str):
        self.pageSizes = {}
        self.bigPages = []
        self.parse(path)

    def parse(self, path:str):
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as file:
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
                if "filters" in data and data["filters"] is not None:
                    for filter in data["filters"]:
                        text = filter["text"]
                        rules:List[Rule] = []
                        for ruleData in filter["rules"]:
                            rules.append(Rule(
                                ruleData.get("min-short-side", None),
                                ruleData.get("max-short-side", None),
                                ruleData.get("min-long-side", None),
                                ruleData.get("max-long-side", None)
                            ))

                        self.filters.append(Filter(text, rules))
                language = "EN"
                if "language" in data:
                    language = data["language"]
                if "dictionaries" in data:
                    for dictionary in data["dictionaries"]:
                        name = dictionary["name"]
                        if name != language:
                            continue
                        d = Dictionary(name)
                        for word in dictionary["words"]:
                            d.addWord(word["id"], word["value"])
                        self.dictionary = d
                        break

        except Exception as e:
            self.error = f"settings.yaml cannot be opened:\n{e}"
