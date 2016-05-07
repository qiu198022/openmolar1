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
update perio dates, xray dates, and write items to the daybook
'''

import logging
import re

from openmolar.settings import localsettings
from openmolar.dbtools import daybook

from openmolar.qt4gui.fees import fees_module
from openmolar.qt4gui.printing import bookprint

LOGGER = logging.getLogger("openmolar")


def perioDates(om_gui, arg):
    '''
    update the patient's "last scale/polish" date
    '''
    if "SP" in arg:
        om_gui.pt.pd10 = localsettings.currentDay()


def xrayDates(om_gui, arg):
    '''
    update the patient's "last xray" dates
    '''
    if "M" in arg or "S" in arg:
        om_gui.pt.pd9 = localsettings.currentDay()
    if "P" in arg:
        om_gui.pt.pd8 = localsettings.currentDay()


def updateDaybook(om_gui):
    '''
    looks for newly completed treatments when a record is closed
    '''
    daybookdict = {
        "diagn": "",
        "perio": "",
        "anaes": "",
        "misc": "",
        "ndu": "",
        "ndl": "",
        "odu": "",
        "odl": "",
        "other": "",
        "chart": ""
    }
    feesa = 0  # fee
    feesb = 0  # ptfee
    hashes = []

    courseno = om_gui.pt.treatment_course.courseno
    not_new_course = (courseno == om_gui.pt.dbstate.treatment_course.courseno)

    for tx_hash in om_gui.pt.completed_tx_hash_tups:

        if not_new_course and \
                tx_hash in om_gui.pt.dbstate.completed_tx_hash_tups:
            continue  # already written to daybook.
        LOGGER.debug("write to daybook %s %s %s" % tx_hash)

        hash_, att, treatment = tx_hash

        if att == "examt":
            key = "exam"
        else:
            key = re.sub("cmp$", "", att)

        if key in list(daybookdict.keys()):
            daybookdict[key] += "%s" % treatment
        elif key in ("xray", "exam"):
            daybookdict["diagn"] += "%s" % treatment
        elif key == "custom":
            daybookdict["other"] += "CUSTOM:%s" % treatment
        else:
            # tooth include the key ie ul7 etc...
            daybookdict["chart"] += "%s %s " % (key.upper(), treatment)

        hashes.append(hash_)

        fees = fees_module.getFeesFromEst(om_gui, hash_)

        if fees:
            feesa += fees[0]
            feesb += fees[1]
        else:
            LOGGER.warning(
                "daybook module - no fees for '%s' '%s' '%s'" % tx_hash)

    if hashes != []:
        if om_gui.pt.dnt2 != 0 and om_gui.pt.cset != "I":
            dent = om_gui.pt.dnt2
        else:
            dent = om_gui.pt.dnt1
        trtid = localsettings.clinicianNo

        daybook.add(om_gui.pt.serialno, om_gui.pt.cset, dent, trtid,
                    daybookdict, feesa, feesb, hashes)


def daybookView(om_gui, print_=False):
    dent1 = str(om_gui.ui.daybookDent1ComboBox.currentText())
    dent2 = str(om_gui.ui.daybookDent2ComboBox.currentText())
    sdate = om_gui.ui.daybookStartDateEdit.date()
    edate = om_gui.ui.daybookEndDateEdit.date()
    if sdate > edate:
        om_gui.advise(_("bad date sequence"), 1)
        return False
    filters = str(om_gui.ui.daybook_filters_lineEdit.text())
    if filters:
        filters = "AND %s" % filters.replace("%", "%%")
    om_gui.wait()
    om_gui.ui.daybookTextBrowser.setHtml(_("polling database..."))
    try:
        html = daybook.details(dent1, dent2, sdate, edate, filters)
    except daybook.connect.ProgrammingError as exc:
        LOGGER.exception("Bad Query")
        html = "<h1>%s</h1><pre>%s</pre>" % (_("Bad Query"), str(exc))
    except daybook.connect.OperationalError as exc:
        LOGGER.exception("Bad Query")
        html = "<h1>%s</h1><pre>%s</pre>" % (_("Bad Query"), str(exc))
    except Exception as exc:
        LOGGER.exception("Unknown Error")
        html = "<h1>%s</h1><pre>%s</pre>" % (_("Unknown Error"), str(exc))
    om_gui.ui.daybookTextBrowser.setHtml(html)
    if print_:
        myclass = bookprint.printBook(html, om_gui)
        myclass.printpage()
    om_gui.wait(False)
