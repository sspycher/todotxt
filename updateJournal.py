# -*- coding: iso-8859-1 -*-

from datetime import datetime
import threading
import time
import sys


def background():
    while True:
        time.sleep(1000)


def save_state():
    print('Saving current state...\nQuitting Plutus. Goodbye!')


JournalFile = "../../Lists2/journal.txt"
with open(JournalFile, 'r',encoding='UTF-8') as file:
    try:
        lines = file.readlines()
        for line in reversed(lines):
            print(line)
    except:
        lines = []
# now threading1 runs regardless of user input
threading1 = threading.Thread(target=background)
threading1.daemon = True
threading1.start()


while True:
    entry = input("? ")
    if entry.lower() == 'exit':
        save_state()
        sys.exit()
    else:
        try:
            newline = " ".join([datetime.now().strftime("%Y-%m-%d"), entry, "\n"])
            print(entry)
        except:# where does the encoding crash happen? at out.write() maybe, then the except must be placed downwards
            print("encoding error")
            newline = "encoding error in string, adding nothing"
        with open(JournalFile, 'w', encoding='UTF-8') as out:
            lines.insert(0,newline)
            lines_sortedCopy = reversed(lines)
            for line in lines_sortedCopy:
                print(line)
            for line in lines:
                 out.write(line)

