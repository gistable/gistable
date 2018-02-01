#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012 Caner BASARAN
# Licensed under the GNU General Public License, version 2.
# See the file http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt


def turkish_id_no_check(tc_no):
    ''' turkish_id_no_check(long) -> bool
        
    Return the validation of Turkish Identification Number
      
    >>> turkish_id_no_check(98768109974)
    True 
    '''
 
    list_tc = map(int,str(tc_no))
    tc10 = (sum(list_tc[0:10:2])*7 - sum(list_tc[1:9:2])) % 10
    tc11 = (sum(list_tc[0:9]) + tc10) % 10
    return True if list_tc[9] == tc10 and list_tc[10] == tc11 else False