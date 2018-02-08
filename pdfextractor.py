from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
import pdfminer
from PyPDF2 import PdfFileReader
import numpy as np
import matplotlib.pyplot as plt
import os

# between 1 and 100
ScaleX = 100
ScaleY = 100

pathToPDF = "pdf"


def draw_fig(matrix):
    fig = plt.figure(figsize=(6, 3.2))

    ax = fig.add_subplot(111)
    ax.set_title('colorMap')
    plt.imshow(matrix.transpose())
    ax.set_aspect('equal')

    cax = fig.add_axes([0.12, 0.1, 0.78, 0.8])
    cax.get_xaxis().set_visible(False)
    cax.get_yaxis().set_visible(False)

    cax.patch.set_alpha(0)
    cax.set_frame_on(False)
    plt.colorbar(orientation='vertical')
    plt.show()
    print("done")


def parse_obj(lt_objs, width, height, matrix):
    for obj in lt_objs:
        if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
            x0 = int((obj.bbox[0] * ScaleX) / width)
            y0 = int((obj.bbox[1] * ScaleY) / height)
            x1 = int((obj.bbox[2] * ScaleX) / width)
            y1 = int((obj.bbox[3] * ScaleY) / height)
            for y_ in range(y1 - y0):
                try:
                    for x_ in range(x1 - x0):
                        matrix[x0 + x_, 100 - (y0 + y_)] += 1
                except:
                    pass
        # if it's a container, recurse
        elif isinstance(obj, pdfminer.layout.LTFigure):
            parse_obj(obj._objs, width, height,matrix)

    return matrix


for a, key in enumerate(os.listdir(pathToPDF)):
    fp = open(os.path.join(pathToPDF, key), 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser)
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    rsrcmgr = PDFResourceManager()
    device = PDFDevice(rsrcmgr)
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    inputpdf = PdfFileReader(open(os.path.join("pdf", key), 'rb'))
    # loop over all pages in the document
    for page in PDFPage.create_pages(document):
        interpreter.process_page(page)
        layout = device.get_result()
        matrix = np.zeros((100, 100))
        vector = parse_obj(layout._objs, page.cropbox[2], page.cropbox[3],matrix)
        draw_fig(vector)

