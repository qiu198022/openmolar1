# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License 
# for more details.

'''
contains one class - the yearCalendar
'''
import calendar
import datetime
from PyQt4 import QtGui, QtCore
from openmolar.settings import localsettings

class yearCalendar(QtGui.QWidget):
    '''
    a pyqt4 custom widget to show a year calendar
    ''' 
    def __init__(self, parent=None):
        '''
        initiate the widget
        '''
        super(yearCalendar, self).__init__(parent)
        self.setSizePolicy(QtGui.QSizePolicy(
        QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))
        
        self.setMinimumSize(self.minimumSizeHint())
        self.monthStarts = {}
        self.vheaderwidth = self.width()*0.1
        self.setSelectedDate(datetime.date.today())
        self.setMouseTracking(True)
        self.mouseBrush = QtGui.QColor(self.palette().color(
        QtGui.QPalette.Highlight))
        self.mouseBrush.setAlpha(64)
        self.highlightedDate = None
        self.data = {}
        self.startDOW = 0
        
    def sizeHint(self):
        '''
        set an (arbitrary) size for the widget
        '''
        return QtCore.QSize(700, 400)

    def minimumSizeHint(self):
        '''
        set an (arbitrary) minimum size for the widget
        '''
        return QtCore.QSize(700, 400)
    
    def setColumnNo(self):
        '''
        work out how many columns are required
        the minimum is 31 (when all months start on the same day)
        '''
        startday = 6 #assume sunnday
        self.columnNo = 31
        for month in range(1,13):
            c_date = datetime.date(self.year, month, 1)
            firstDayOfMonth = c_date.weekday()
            self.monthStarts[month] = firstDayOfMonth
            if c_date.weekday() < startday:
                startday = firstDayOfMonth
            colsRequired = firstDayOfMonth + \
            calendar.monthrange(self.year, month)[1]

            if colsRequired > self.columnNo:
                self.columnNo = colsRequired
        
        self.startDOW = startday
        
    def getDateFromPosition(self, xpos, ypos): 
        rowheight = self.height() / 13
        month = ypos//rowheight
        if 0 < month <13:
            day = (xpos - self.vheaderwidth) // self.columnWidth
            day = int(day) - self.monthStarts[month] +1
            
            try:
                d = datetime.date(self.year, month, day)
                return d
            except ValueError:
                # date threw an error.
                pass
    
    def mouseMoveEvent(self, event):
        '''
        note this function works because I set self.setMouseTracking(True)
        catch the mouse Mouse so user knows the widget has capabilities
        '''
        d = self.getDateFromPosition(event.x(), event.y())
        if d != self.highlightedDate:
            self.highlightedDate = d
            self.update()
        
    def mousePressEvent(self, event):
        '''
        catch the mouse press event - 
        '''
        d = self.getDateFromPosition(event.x(), event.y())
        if d and d != self.selectedDate:
            self.setSelectedDate(d)
            self.emit(QtCore.SIGNAL("selectedDate"), d)
            
    def leaveEvent(self,event):
        '''
        clear any false stuff from the mouse
        '''
        self.highlightedDate = None
        self.update()

    
    def setSelectedDate(self, d):
        '''
        d is a pydate
        '''
        self.selectedDate = d
        self.year = d.year
        self.setColumnNo()
        self.update()
        
    def paintEvent(self, event=None):
        '''
        draws the widget - recalled at any point by instance.update()
        '''
        painter = QtGui.QPainter(self)
        myfont = QtGui.QFont(self.fontInfo().family(), localsettings.appointmentFontSize)
        painter.setFont(myfont)
        
        rowHeight = self.height() / 13
        
        self.columnWidth = (self.width() - self.vheaderwidth) / self.columnNo
        
        for month in range(13):
            painter.setBrush(self.palette().alternateBase())        
        
            rect = QtCore.QRect(0, month*rowHeight, self.vheaderwidth, 
            rowHeight)               

            painter.setPen(QtGui.QPen(QtCore.Qt.gray,1))                
                    
            if month == 0: 
                painter.setBrush(self.palette().highlight())        
                painter.drawRect(rect)
                
                painter.setPen(self.palette().color(
                self.palette().HighlightedText))            
                painter.drawText(rect,QtCore.Qt.AlignCenter, str(self.year))
                
                for col in range (self.columnNo):
                    rect = QtCore.QRectF(
                    self.vheaderwidth+col*self.columnWidth, 
                    month * rowHeight, self.columnWidth, rowHeight)
                    
                    painter.setPen(QtGui.QPen(QtCore.Qt.gray,1))                
                    painter.drawRect(rect)
                
                    dayno = col % 7
                    my_text = ("M","Tu","W","Th","F","Sa","Su")[dayno]

                    if dayno > 4: #weekend
                        painter.setPen(QtCore.Qt.red)
                    else:
                        painter.setPen(self.palette().color(
                        self.palette().HighlightedText))
            
                    painter.drawText(rect,QtCore.Qt.AlignCenter, my_text)
                      
            else:                
                if month%2==0:
                    painter.setBrush(self.palette().base())                            
                else:
                    painter.setBrush(self.palette().alternateBase()) 
                
                painter.drawRect(rect)

                painter.setPen(self.palette().color(
                self.palette().HighlightedText))            
                
                c_date = datetime.date(self.year, month, 1)
                my_text = str(localsettings.monthName(c_date))
                painter.drawText(rect, QtCore.Qt.AlignCenter, my_text)
                startday = c_date.weekday()
            
                for col in range (self.columnNo):
                    
                    rect = QtCore.QRectF(self.vheaderwidth+col*self.columnWidth, 
                    month * rowHeight, self.columnWidth, rowHeight)
                                            
                    painter.setPen(QtGui.QPen(QtCore.Qt.gray,1))                
                                                
                    painter.drawRect(rect)
                
                    painter.setPen(self.palette().color(
                    self.palette().WindowText))
                
                    if col >= startday:
                        try:
                            c_date = datetime.date(self.year, month, 
                            col-startday+1)
                            my_text = str(c_date.day)

                            if c_date == self.selectedDate:
                                painter.save()
                                painter.setBrush(self.palette().color(
                                self.palette().Highlight))

                                painter.setPen(self.palette().color(
                                self.palette().HighlightedText))
                                
                                painter.drawRect(rect)
                                painter.drawText(rect, 
                                QtCore.Qt.AlignCenter, my_text)

                                painter.restore()
                                
                            elif c_date == self.highlightedDate:
                                #--mouseOver
                                painter.save()
                                painter.setBrush(self.mouseBrush)

                                painter.setPen(self.palette().color(
                                self.palette().HighlightedText))
                                
                                painter.drawRect(rect)
                                painter.drawText(rect, 
                                QtCore.Qt.AlignCenter, my_text)

                                painter.restore()
                                
                            elif c_date.isoweekday() > 5: 
                                #weekend
                                painter.setPen(QtCore.Qt.red)
                                painter.drawText(rect, 
                                QtCore.Qt.AlignCenter, my_text)

                            else:
                                painter.setPen(self.palette().color(
                                self.palette().WindowText))
                                painter.drawText(rect, 
                                QtCore.Qt.AlignCenter, my_text)

                            
                        except ValueError: 
                            # month doesn't have this day eg feb 30th
                            pass
            

if __name__ == "__main__":
    def catchSignal(d):
        print d
        
    import sys
    app = QtGui.QApplication(sys.argv)
    form = yearCalendar()
    form.setSelectedDate(datetime.date.today())
    form.connect(form, QtCore.SIGNAL("selectedDate"), catchSignal)

    form.show()

    sys.exit(app.exec_())