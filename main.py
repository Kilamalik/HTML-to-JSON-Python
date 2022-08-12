import json
from bs4 import BeautifulSoup


def main():
    with open('timetable.html', 'r') as content:
        soup = BeautifulSoup(content, 'html.parser')

    # first table
    oddTable = soup.find_all('table', class_='odd_table')[0]
    thead = oddTable.thead
    tbody = oddTable.tbody
    # print(oddTable.prettify())

    # table without caption
    # print(thead.prettify(), tbody.prettify())

    # batch group only
    # thead_tr_batch = thead.find_all('tr')[0].th.text
    # print(thead_tr_batch)

    # days of the table
    # thead_tr_days = thead.find_all('tr')[1]
    # for day in thead_tr_days:
    # print(day.text)

    # first row of slots
    firstRow = tbody.find_all('tr')[0]
    firstRowTime = firstRow.th.text
    for data in firstRow:
        if data.name == 'td':
            if data.table:
                print('this is a table')


if __name__ == "__main__":
    main()
