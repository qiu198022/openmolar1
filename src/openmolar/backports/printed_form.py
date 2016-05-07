#! /usr/bin/python

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2016 Neil Wallace <neil@openmolar.com>               # #
# #                                                                         # #
# # This file is part of OpenMolar.                                         # #
# #                                                                         # #
# # OpenMolar is free software: you can redistribute it and/or modify       # #
# # it under the terms of the GNU General Public License as published by    # #
# # the Free Software Foundation, either version 3 of the License, or       # #
# # (at your option) any later version.                                     # #
# #                                                                         # #
# # OpenMolar is distributed in the hope that it will be useful,            # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of          # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           # #
# # GNU General Public License for more details.                            # #
# #                                                                         # #
# # You should have received a copy of the GNU General Public License       # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.      # #
# #                                                                         # #
# ########################################################################### #

'''
Provides a Class for printing on an A4 Sheet
'''

import logging
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtPrintSupport
from PyQt5 import QtWidgets

from openmolar.settings import localsettings

LOGGER = logging.getLogger("openmolar")


class PrintedForm(object):

    '''
    a class to set up and print an a4 form
    '''
    testing_mode = False
    print_background = False

    rects = {}
    off_set = QtCore.QPoint(0, 0)
    scale_x = 1
    scale_y = 1

    def __init__(self, parent=None):

        self.parent = parent
        self.printer = QtPrintSupport.QPrinter()
        self.pdfprinter = QtPrintSupport.QPrinter()
        self.pdfprinter.setPrinterName("PDF PRINTER")
        self.pdfprinter.setOutputFormat(QtPrintSupport.QPrinter.PdfFormat)
        self.pdfprinter.setOutputFileName(localsettings.TEMP_PDF)

        self.chosen_printer = self.printer

        for printer in (self.printer, self.pdfprinter):
            printer.setPaperSize(QtPrintSupport.QPrinter.A4)
            printer.setFullPage(True)
            printer.setResolution(96)

    def set_testing_mode(self, mode):
        self.testing_mode = mode

    def set_background_mode(self, mode):
        self.print_background = mode

    def set_offset(self, x, y):
        '''
        offsets all printing by x,y
        '''
        self.off_set = QtCore.QPointF(x, y)

    def set_scaling(self, scale_x, scale_y):
        '''
        offsets all printing by x,y
        '''
        self.scale_x = scale_x
        self.scale_y = scale_y

    def controlled_print(self):
        '''
        raise a dialog before printing
        '''
        dl = QtPrintSupport.QPrintDialog(self.printer, self.parent)
        if dl.exec_():
            self.chosen_printer = self.printer
            self.print_()
            self.set_background_mode(False)
            self.set_testing_mode(True)
            self.chosen_printer = self.pdfprinter
            self.print_()

            return True

    @property
    def BACKGROUND_IMAGE(self):
        '''
        overwrite this image when subclassing.
        '''
        LOGGER.error("No pixmap set")
        return QtGui.QPixmap()

    def print_(self, painter=None):
        '''
        print the background and any rects if in testing_mode

        note - this functions return the active painter so that classes which
        inherit from PrintedForm can finalise the printing.
        '''
        LOGGER.info("printing to %s" % self.chosen_printer.printerName())
        if painter is None:
            painter = QtGui.QPainter(self.chosen_printer)

        if self.print_background:
            pm = self.BACKGROUND_IMAGE
            if not pm.isNull():
                painter.save()
                painter.translate(
                    -self.printer.pageRect().x(),
                    -self.printer.pageRect().y()
                )
                painter.drawPixmap(self.printer.paperRect(), pm, pm.rect())
                painter.restore()

            else:
                LOGGER.warning("background image is null")

        painter.translate(self.off_set)
        LOGGER.info("translating form by %s" % self.off_set)
        painter.scale(self.scale_x, self.scale_y)
        LOGGER.info("scaling output by %s x %s" % (self.scale_x, self.scale_y))

        if self.testing_mode:  # outline the boxes
            painter.save()
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
            painter.setBrush(QtGui.QBrush(QtCore.Qt.black))
            painter.drawRect(0, 0, 20, 5)
            painter.drawRect(0, 0, 5, 20)
            painter.restore()

            # put down a marker at position 0 (for alignment purposes)

            painter.save()
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
            for rect in list(self.rects.values()):
                painter.drawRect(rect)
            painter.restore()

        return painter


if __name__ == "__main__":
    import os
    os.chdir(os.path.expanduser("~"))  # for print to file

    app = QtWidgets.QApplication([])
    form = PrintedForm()
    form.testing_mode = True

    form.rects = {"test": QtCore.QRect(100, 100, 100, 100)}

    form.controlled_print()
