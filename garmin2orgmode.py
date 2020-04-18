#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import argparse
import datetime
import os
import re
import time


os.environ['TZ'] = 'Europe/Warsaw'
time.tzset()

from datetime import date, timedelta
from conf import ENTRY_LEVEL

def get_parser():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-v", "--verbose",
                        action="store_true", help="be verbose")
    parser.add_argument("-d", "--debug",
                        action="store_true", help="be verbose")
    parser.add_argument("-f", "--force",
                        action="store_true", help="be verbose")
    parser.add_argument("--calendar", help="Send event to this Apple Calendar",
                        default="Clocking life")

    parser.add_argument("file", help="", nargs='+')
    return parser


def hr(t, verbose):
    if t:
        if verbose: print(t)
    if verbose: print('-' * 80)


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    logfn = os.path.basename('garmin2orgmode.log')

    cycling = []        
    running = []

    try:
        log = open(logfn)
    except:
        logs = []
    else:
        logs = log.read()
        log.close()

    for f in args.file:
        if 'summary.json' in f:
            pass
        else:
            continue

        hr(f, args.verbose)

        with open(f, "r") as read_file:
            data = json.load(read_file)

        if args.debug:
            print(data)
            print('Start', data['summaryDTO']['startTimeLocal'])
            print('Duration in min', data['summaryDTO']['movingDuration']/60)
            print('Calc', data['summaryDTO']['calories'])

        duration = timedelta(seconds = data['summaryDTO']['duration'])
        dur_in_min = int(data['summaryDTO']['duration']/60)
        
        startdt = data['summaryDTO']['startTimeLocal'] # 2019-10-18T17:49:20.0
        start = datetime.datetime.strptime(startdt, '%Y-%m-%dT%H:%M:%S.%f')
        
        end = start + duration
        start2 = start.strftime("%Y-%m-%d %a %H:%M") # %A, %B %d, %Y %I:%M %p")

        date = start.strftime("%Y-%m-%d %a") # %A, %B %d, %Y %I:%M %p")

        end2 = end.strftime("%Y-%m-%d %a %H:%M")
        entrylog = data['activityName'] + ' ' + start2 + ' ' + end2

        if entrylog not in logs or args.force:
            # CLOCK: [2019-08-02 Fri 09:10]--[2019-08-02 Fri 16:40]
            txt = ' ' + str(int(data['summaryDTO']['calories'])) + ' kcal ' + \
                         '' + str(int(data['summaryDTO']['movingDuration']/60)) + \
                         '/'+ str(int(data['summaryDTO']['duration']/60)) + ' min'
            entry = ENTRY_LEVEL + ' ' + data['activityName'] + txt + ' [' + date + ']\n'
            entry += '   :LOGBOOK:\n     CLOCK: [' + start2 + ']--[' + end2 + '] => ' + \
              '{:01d}:{:02d}'.format(*divmod(dur_in_min, 60)) + '\n   :END:'
            #print(entry)

            if 'Cycling' in data['activityName']:
                cycling.append(entry)
            if 'Running' in data['activityName']:
                running.append(entry)
            log = open(logfn, 'a')
            log.write(entrylog + '\n')
        else:
            #if args.verbose:
            print('- already in your calendar: ' + entrylog)

    log.close()

    def hr():
        print('-' * 80)
        
    if cycling:
        print('* Sport Bike')
        for e in cycling:
           print(e)

    hr()

    if running:
        print('* Sport Run')

        for e in running:
            print(e)
