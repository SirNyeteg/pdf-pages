from __future__ import annotations
from dataclasses import dataclass, field

import PyPDF2

from typing import List, Dict, Iterable


@dataclass(order=True)
class PageDimension:
    width: int
    height: int

    def __hash__(self) -> int:
        return hash(frozenset((self.width, self.height)))
    
    def __eq__(self, other:PageDimension) -> bool:
        return self.__hash__() == other.__hash__()


@dataclass
class PageStat:
    dimension: PageDimension
    pages: List[int] = field(default_factory=list)


class PdfReader:
    def __init__(self, path:str):
        self.path = path
        self.stats:Dict[PageDimension, PageStat] = {}
        self.parse()

    def parse(self):
        try:
            with open(self.path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)

                page_sizes = []
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    size = page.mediabox
                    width = convertPointsToMm(float(size[2]))
                    height = convertPointsToMm(float(size[3]))
                    dimension = PageDimension(width, height)
                    if dimension not in self.stats:
                        self.stats[dimension] = PageStat(dimension, [])
                    self.stats[dimension].pages.append(page_num + 1)
        except Exception as e:
            print(e)

    def getStats(self) -> Iterable[PageStat]:
        return self.stats.values()
    

def convertPointsToMm(points:float) -> int:
    mm = round(points * 0.352777778)
    return mm