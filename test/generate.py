from PyPDF2 import PdfWriter, PageObject, PaperSize
from PyPDF2.papersizes import Dimensions

from reportlab.pdfgen import canvas

import random

from typing import Dict

def convertPointsToMm(points:float) -> int:
    mm = round(points * 0.352777778)
    return mm

def convertMmToPoints(mm:float) -> int:
    points = round(mm / 0.352777778)
    return points

Letter = Dimensions(612, 792)

pageSizes:Dict[str, Dimensions] = {
    'A0': PaperSize.A0,
    'A1': PaperSize.A1,
    'A2': PaperSize.A2,
    'A3': PaperSize.A3,
    'A4': PaperSize.A4,
    'A5': PaperSize.A5,
    'A6': PaperSize.A6,
    'B2': Dimensions(1417.5, 2004.3),
    'B3': Dimensions(1000.8, 1417.5),
    'Letter': Letter
}

def genRandomSide() -> int:
    # 100-800 mm in points
    return convertMmToPoints(random.randint(1, 8) * 100)

def genRandomDimension() -> Dimensions:
    return Dimensions(genRandomSide(), genRandomSide())

def genRandomLongDimension() -> Dimensions:
    height = random.choice([PaperSize.A4.height, PaperSize.A3.height])
    width = convertMmToPoints(random.randint(6, 16) * 100)
    return Dimensions(width, height)

def rotate(dimension:Dimensions, orientation:str) -> Dimensions:
    if orientation == "portrait":
        return dimension
    else:
        return Dimensions(dimension.height, dimension.width)

orientations = ['portrait', 'landscape']

pdfWriter = PdfWriter()

def createRandomPdf(filename:str, numPages:int):
    c = canvas.Canvas(filename)
    pages = []



    for pageSize, dimension in pageSizes.items():
        for orientation in orientations:
            pages.append((
                rotate(dimension, orientation),
                f'This is a page with size {pageSize} and orientation {orientation}',
                50
            ))

    for i in range(20):
        dimension = genRandomDimension()
        pages.append((
            dimension,
            f'This is a page with custom size {convertPointsToMm(dimension.width)}x{convertPointsToMm(dimension.height)} mm',
            1
        ))
        
    for i in range(10):
        dimension = genRandomLongDimension()
        pages.append((
            dimension,
            f'This is a very long page with size {convertPointsToMm(dimension.width)}x{convertPointsToMm(dimension.height)} mm',
            1
        ))

    remainingPageCount = numPages - sum([count for _,_,count in pages])

    while remainingPageCount > 0:
        pageSize, dimension = random.choice(list(pageSizes.items()))
        orientation = random.choice(orientations)
        count = random.randint(1,15)
        pages.append((
            rotate(dimension, orientation),
            f'This is a page with size {pageSize} and orientation {orientation}',
            count
        ))
        remainingPageCount -= count

    random.shuffle(pages)

    for dimension, text, count in pages:
        for _ in range(count):
            c.setPageSize(dimension)
            c.drawString(30, 30, text)
            c.showPage()

    c.save()

createRandomPdf('output.pdf', 2000)
