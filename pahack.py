#!/usr/bin/python 
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.keys import Keys

import time
import os
import sys
import datetime
from datetime import datetime as dt
from argparse import ArgumentParser
from getpass import getpass
import json
import re

ebs_url = EBS_URL

def get_otp_password():
    sys.path.append(os.environ.get('HOME') + '/git/rhlife')
    import otp
    password = otp.get_pin_otp()
    return password

def date_from_string(datestr):
    date = dt.strptime(datestr, '%Y-%m-%d')

def get_start_end_date(date):
    if date == None:
        date = dt.now()
    delta = dt.isoweekday(date) % 7
    sdate = date - datetime.timedelta(days = delta)
    edate = date + datetime.timedelta(days = 6 - delta)
    return sdate.strftime('%d-%m-%Y'), edate.strftime('%d-%m-%Y')

def start_browser():
    driver = webdriver.Firefox()
    driver.get(ebs_url)
    print "Page loaded:", driver.title
    return driver

def login(driver, username, password, auto_otp):
    if not username:
        username = raw_input('Username (Kerberos Username): ')
    elem = driver.find_element_by_name('ssousername')
    elem.send_keys(username)

    elem = driver.find_element_by_name('password')
    if auto_otp:
        password = get_otp_password()
    else:
        if not password:
            password = getpass('Passcode (PIN + LinOTP Token): ')
    elem.send_keys(password)
    elem.submit()

    try:
        WebDriverWait(driver, 10).until(EC.title_contains('Oracle Application'))
        print driver.title
    except NoSuchElementException as e:
        print e.message

def open_menu(driver, menu):
    menutag = {'recent': 'Recent Timecards', 'create': 'Create Timecard'}
    wait = 0.05
    try:
        # Time
        elem = driver.find_element_by_css_selector('li.submenu')
        elem.click()
    except NoSuchElementException as e:
        print e.message
        # "RH JP TIMECARDS"
        try:
            elems = driver.find_elements_by_css_selector('li.rootmenu')
        except NoSuchElementException as e:
            print e.message
            print '!!! exit...'
            sys.exit()
        for e in elems:
            if e.text == 'RH JP TIMECARDS':
                e.click()
                break

        # Time
        loop_count = 0
        while True:
            try:
                elem = driver.find_element_by_css_selector('li.submenu')
            except NoSuchElementException as e:
                #print "** got NoSuchElementException in find_element_by_css_selector('li.submenu'), try again..."
                time.sleep(wait)
                loop_count = loop_count + 1
                continue
            else:
                print "Completed menu open for %s sec, found 'li.submenu'." % str(loop_count * wait)
                elem.click()
                break
    
    loop_count = 1
    while True:
        try:
            elems = elem.find_elements_by_css_selector('a')
        except NoSuchElementException as e:
            #print "** got NoSuchElementException in find_element_by_css_selector('a'), try again..."
            time.sleep(wait)
            loop_count = loop_count + 1
            continue
        else:
            print "Completed menu open for %s sec, found 'a'." % str(loop_count * wait)
            for e in elems:
                if e.text == menutag[menu]:
                    e.click()
                    return
            print "... but menutag '%s' not found, try again..." % menutag[menu]
            time.sleep(wait)
            loop_count = loop_count + 1
            continue

def search_timecard(driver, sdate, edate):
    print "Searching for timecard: %s - %s" % (sdate, edate)
    try:
        WebDriverWait(driver, 10).until(EC.title_contains(u'最近のタイムカード'))
        print driver.title
    except NoSuchElementException as e:
        print e.message
    elem = driver.find_element_by_css_selector('input#Hxcdatesfrom')
    elem.send_keys(sdate)
    elem = driver.find_element_by_css_selector('input#Hxcdatesto')
    elem.send_keys(edate)
    elem = driver.find_element_by_css_selector('button#HxcSrchgocontrol')
    elem.click()

    try:
        elem = driver.find_element_by_css_selector('input[name="Hxctcarecentlist:selected:0"]')
    except NoSuchElementException as e:
        print e.message
        print "There is no timecard from %s to %s, creating..." % (sdate, edate)
        elem = driver.find_element_by_css_selector('a#HXC_TIMECARD_DIRECT')
        elem.click()

        options = driver.find_elements_by_css_selector('select#N56 option')
        for option in options:
            val = option.get_attribute('value')
            sd, sm, sy = sdate.split('-')
            ed, em, ey = edate.split('-')
            matcher = '%s/%s/%s|%s/%s/%s' % (sy, sm, sd, ey, em, ed)
            print 'select option: %s, match: %s' % (val, matcher)
            if val.find(matcher) == 0:
                driver.find_element_by_css_selector('select#N56 > option[value="' + val + '"]').click()
                break

        return

    print "Found timecard from %s to %s, opening..." % (sdate, edate)
    #elem = driver.find_element_by_css_selector('a#Hxctcarecentlist:UpdEnable:0')
    #elem = driver.find_element_by_css_selector('a#Hxctcarecentlist:DetailEnable:0')
    elem = driver.find_element_by_name('Hxctcarecentlist:UpdEnable:0')
    elem.click()

def input_and_wait_for_completion(driver, selector, input_value, is_recursive=False, works=None):
    #print "[input_and_wait_for_completaion:1]"
    try:
        elem = driver.find_element_by_css_selector(selector)
    except NoSuchElementException as e:
        print e.message
    if elem.get_attribute('value'):
        print "There are something in input already."
        if not is_recursive: return

    #print "[input_and_wait_for_completaion:2]"
    print "Keys sent: '%s'" % input_value
    elem.clear()
    elem.send_keys(input_value)
    elem.send_keys('\t')

    loop_count = 0
    #wait = 0.1
    wait = 0.05
    max_loop = 50
    while True:
        #print "[input_and_wait_for_completaion:3:%i]" % loop_count
        elem = driver.find_element_by_css_selector(selector)
        try:
            val = elem.get_attribute('value')
        except StaleElementReferenceException as e:
            print "** got StaleElementReferenceException in get_attribute(), try again..."
            continue

        if len(val) > len(input_value) + 1:
            break

#        elem = driver.find_element_by_css_selector('div#suggestData')
#        attr = elem.get_attribute('style')
#        if attr:
#            #elems = elem.find_elements_by_css_selector('td.OraTableCellText span')
#            #print '*** [lovSuggestTable]', attr, [e.text for e in elems]
#            elem1 = elem.find_element_by_css_selector('td.OraTableCellText')
#            elem2 = elem.find_element_by_css_selector('span')
#            print '*** [lovSuggestTable]', attr, elem2.text

        loop_count = loop_count + 1
        if loop_count > max_loop:
            print '*** loop count exceeds %s, try again...' % max_loop
            input_and_wait_for_completion(driver, selector, input_value, is_recursive=True)
        time.sleep(wait)
    print "Completion finished: '%s' for %s sec." % (val, str(wait * loop_count))

def input_new_timecard_test(driver, works):
    type_id = 'L'
    task_table = {
            1: '1.0-Training',
            2: '2.0-PTO',
            3: '3.0-Holiday',
            4: '4.0-Available',
            5: '5.0-Travel',
            6: '6.0-Vacation',
            7: '7.0-Presales',
            8: '8.0-Private Time Off',
            9: '9.0-AOB',
            10: '10.0-Sick Leave',
            11: '11.0-Internal Project'
    }

    tree = {}
    #nworks = 0
    for work in works:
        key = (work['pa'], work['task'])
        if not tree.get(key):
            tree[key] = []
        tree[key].append(work)
        #nworks = nworks + 1

    metadata_index_base = 241
    row = 0
    #for row in range(0, nworks):
    for pa, task in tree.keys():
        pa_selector = 'input#A' + str(metadata_index_base + row) + 'N1display'
        task_selector = 'input#A' + str(metadata_index_base + row + 10) + 'N1display'
        type_selector = 'input#A' + str(metadata_index_base + row + 20) + 'N1display'

        for work in tree[(pa,task)]:
            # B22_r_c r:1-, c:0-
            date = dt.strptime(work['date'], '%Y-%m-%d')
            wl_selector = 'input#B22_' + str(row + 1) + '_' + str(date.isoweekday())

            print json.dumps(work)
            input_and_wait_for_completion(driver, pa_selector, str(work['pa']))
            input_and_wait_for_completion(driver, task_selector, str(work['task']))
            input_and_wait_for_completion(driver, type_selector, type_id)

            elem = driver.find_element_by_css_selector(wl_selector)
            new = work['time']
            old = elem.get_attribute('value')
            if old:
                new = int(old) + int(new)
                elem.clear()
            elem.send_keys(str(new))

        details = driver.find_elements_by_css_selector('td.x1v td.x1v a')
        details[row * 2].click()    # trashbox img is created after inputting detail.

        for work in tree[(pa,task)]:
            # B14_c_N1
            # detailsubmit
            date = dt.strptime(work['date'], '%Y-%m-%d')
            detail_selector='textarea#B14_' + str(date.isoweekday()) + '_N1'
            elem = driver.find_element_by_css_selector(detail_selector)
            new = date.strftime('%m/%d') + ': ' + str(work['time']) + 'h ' + work['detail']
            if pa == 21347:
                new = new + ' (' + task_table[int(work['task'])] + ')'
            old = elem.get_attribute('value')
            if old:
                new = old + '\n' + new
                elem.clear()
            elem.send_keys(new)

        driver.find_element_by_css_selector('button#detailsubmit').click()
        row = row + 1

def parse_args():
    desc = u'''{0} [Args] [Options]
Detailed options -h or --help'''.format(__file__)
    parser = ArgumentParser(description=desc)
    parser.add_argument('-u', '--username', type=str, dest='username', help='Kerberos Username')
    parser.add_argument('-P', '--password', type=str, dest='password', help='PIN + OTP')
    parser.add_argument('--auto-otp', action='store_true', dest='auto_otp', help='If you have something insane...')
    parser.add_argument('--date', type=str, dest='date', help='Target date (default: today)')
    args = parser.parse_args()
    print "(debug) %s: %s" % ('username', args.username)
    print "(debug) %s: %s" % ('password', args.password)
    print "(debug) %s: %s" % ('auto_otp', args.auto_otp)
    print "(debug) %s: %s" % ('date', args.date)
    return args

def main(args):
    driver = start_browser()
    login(driver, args.username, args.password, args.auto_otp)
    open_menu(driver, 'recent')

    if args.date:
        date = dt.strptime(args.date, '%Y-%m-%d')
    else:
        date = dt.now()
    start, end = get_start_end_date(date)
    search_timecard(driver, start, end)

    jsonstr = sys.stdin.read()
    input_new_timecard_test(driver, json.loads(jsonstr))

if __name__ == '__main__':
    args = parse_args()
    main(args)
