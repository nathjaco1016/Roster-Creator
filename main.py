# Project by Nathan Jacobs
import sqlite3
import ssl
from urllib.request import urlopen
from bs4 import BeautifulSoup

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Try other teams!
url = 'https://en.wikipedia.org/wiki/Charlotte_Hornets'
#url = 'https://en.wikipedia.org/wiki/Golden_State_Warriors'

doc = urlopen(url, context=ctx)
html = doc.read()
soup = BeautifulSoup(html, 'html.parser')
tags = soup('table')

plyr_table = []

for tag in tags:
    id = tag.get('class', None)
    # Know the class of the overall table is toccolours
    if not id : continue
    if id[0] != 'toccolours' : continue
    # getting sub table and elements
    table = tag.find_next('table')
    table_body = table.find_next('tbody')
    elements = table_body.find_all('tr')
    # looping through table elements and getting data
    i = 0
    for elem in elements:
        i += 1
        if i == 1 : continue
        stats = elem.find_all('td')
        # Retrieving data
        plyr_pos = stats[0].get_text().rstrip()
        plyr_num = stats[1].get_text().rstrip()
        plyr_name = stats[2].get_text().rstrip()

        plyr_data = [plyr_name, plyr_num, plyr_pos]
        plyr_table.append(plyr_data)

# Writing to file
file_str = "\n".join(map(" ".join, plyr_table))

#os.chdir('/Users/nathanjacobs/Desktop')
html_file = open('team_roster.txt', 'x')
html_file.write(file_str)
html_file.close()

# Writing to DB
con = sqlite3.connect('rosterdb.sqlite')
cur = con.cursor()

cur.executescript('''
DROP TABLE IF EXISTS Player;

CREATE TABLE Player (
    name   TEXT UNIQUE,
    number     INTEGER,
    position    TEXT
);
''')

# adding data to SQL table
for plyr_data in plyr_table:
    cur.execute('''INSERT OR IGNORE INTO Player (name, number, position)
            VALUES ( ?, ?, ? )''', (plyr_data[0], int(plyr_data[1]), plyr_data[2]))

    con.commit()
