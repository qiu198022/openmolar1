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

from openmolar.connect import connect
from openmolar.settings import localsettings

QUERY = '''select serialno, title, fname, sname,
addr1, addr2, addr3, town, county, pcde, dob, status, tel1 from new_patients
where familyno = %s order by dob'''

PATIENT_QUERY = QUERY.replace("familyno", "serialno")

LINK_QUERY = 'update new_patients set familyno=%s where serialno=%s'

SYNC_QUERY = '''update new_patients set
addr1=%s, addr2=%s, addr3=%s, town=%s, county=%s, pcde=%s
where familyno=%s'''

NEXT_FAMILYNO_QUERY = "select max(familyno)+1 from new_patients"
NEW_GROUP_QUERY = "update new_patients set familyno=%s where serialno=%s"

DELETE_FAMILYNO_QUERY = \
    "update new_patients set familyno=NULL where familyno=%s"

ADDRESS_MATCH_QUERY = '''select
    case when addr1 = %s then 4 else 0 end +
    case when addr1 like %s then 3 else 0 end +
    case when addr2 like %s then 3 else 0 end +
    case when addr3 like %s then 1 else 0 end +
    case when town like %s then 1 else 0 end +
    case when pcde = %s then 5 else 0 end as matches ,
    serialno, title, fname, sname, dob, addr1, addr2, addr3, town, pcde
from new_patients
where
addr1 like %s or
(addr2 != "" and addr2 like %s) or
(town != "" and town like %s) or
(pcde=%s and pcde != "")
order by matches desc
limit 12
'''


def new_group(serialno):
    '''
    start a new family with one member - serialno
    '''
    db = connect()
    cursor = db.cursor()
    cursor.execute(NEXT_FAMILYNO_QUERY)
    family_no = cursor.fetchone()[0]
    if family_no is None:
        family_no = 1
    cursor.execute(NEW_GROUP_QUERY, (family_no, serialno))
    cursor.close()
    return family_no


def delete_group(family_no):
    '''
    delete all reference to familyno for all records
    '''
    db = connect()
    cursor = db.cursor()
    cursor.execute(DELETE_FAMILYNO_QUERY, (family_no,))
    cursor.close()


def add_member(family_no, serialno):
    '''
    add serialno to group familyno
    '''
    db = connect()
    cursor = db.cursor()
    cursor.execute(LINK_QUERY, (family_no, serialno))
    cursor.close()


def remove_member(serialno):
    '''
    remove any family reference for record serialno
    '''
    add_member(None, serialno)


def get_members(family_no):
    '''
    get members of the family with number familyno
    '''
    db = connect()
    cursor = db.cursor()
    cursor.execute(QUERY, (family_no,))
    members = cursor.fetchall()
    cursor.close()
    return members


def sync_addresses(family_no, chosen_address):
    '''
    set all familyno addresses to this address
    returns the number of records changed.
    '''
    db = connect()
    cursor = db.cursor()
    values = tuple(chosen_address) + (family_no,)
    count = cursor.execute(SYNC_QUERY, values)
    cursor.close()
    return count


def get_patient_details(serialno):
    db = connect()
    cursor = db.cursor()
    cursor.execute(PATIENT_QUERY, (serialno,))
    member = cursor.fetchone()
    cursor.close()
    return member


def get_address_matches(address):
    '''
    find possible address matches for the address used.
    '''

    addr1 = address[0]
    addr2 = address[1]
    addr3 = address[2]
    town = address[3]
    county = address[4]
    pcde = address[5]

    db = connect()
    cursor = db.cursor()
    values = (
        addr1,
        addr1[:10],
        addr2[:10],
        addr3[:10],
        town[:10],
        pcde,
        addr1[:10],
        addr2[:10],
        town[:10],
        pcde[:10],
    )

    cursor.execute(ADDRESS_MATCH_QUERY, (values))
    rows = cursor.fetchall()
    cursor.close()

    return rows


if __name__ == "__main__":
    print(new_group(1))
