import json
import re
from bs4 import BeautifulSoup
from bs4 import Comment


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
    thead_tr_days = thead.find_all('tr')[1]
    # for day in thead_tr_days:
    # print(day.text)

    ##########################################################################################################################################################

    # row of slots
    row = tbody.find_all('tr', recursive=False)[1]  # gets a single row from the specified table
    row_Time = row.th.text

    row_tdList = row.find_all('td', recursive=False)  # gets the td tags which are are the columns of the row
    # recursive=False prevents the loop from accessing the desired
    # tags within the inner tables

    # firstRow_tdList = firstRow.find_all('td', {'class': None})
    # the 'class': None, here means that the td tags within the table
    # in the row will not be selected because they have a class. I am
    # trying to find td tags with no class, which are the td tags
    # outside the detailed table

    spanned = 0  # holds the index to the nextToComment array
    nextToComment = []  # holds whats next to the comment in the row to be compared to data variable in the coming for loop
    dayIndex = 0  # holds the index to the thead_tr_days.find_all('th') array

    # finding span comments within the rows column to be able to identify its location
    comments = row.find_all(text=lambda text: isinstance(text, Comment))
    for comment in comments:
        # print(comment.findPrevious().prettify(), comment.findNext().prettify())
        nextToComment.append(
            comment.findNext())  # stores whatever td tag is next to the comment to be used to check what td tag will be affected

    # print(list(enumerate(row_tdList)))

    for index, data in enumerate(row_tdList):
        ''' The spanned <= len(nextToComment)-1 is to prevent index out of range errors,
            data == nextToComment[spanned] is to check if the current td in data variable is equal to the array value
        '''
        if spanned <= len(nextToComment) - 1 and data == nextToComment[
            spanned]:  # if true, this td tags day will be incremented to match its correct location in the column
            dayIndex = dayIndex + 1
            slotDay = thead_tr_days.find_all('th')[
                dayIndex].text  # The day is obtained by first getting the tr that contains all the days in the row, and then getting the th tag by index
            spanned = spanned + 1
        else:
            slotDay = thead_tr_days.find_all('th')[
                dayIndex].text  # The day is obtained by first getting the tr that contains all the days in the row, and then getting the th tag by index

        if data.table:
            print('this is a table at time', row_Time, 'and day', slotDay)
            data.table_tr = data.table.find_all("tr")
            print(data.table_tr)
        elif data.text == '---':
            print('It\'s ---', row_Time, 'and day', slotDay)
        else:
            print('this is a normal table at time', row_Time, 'and day', slotDay)

        dayIndex = dayIndex + 1


if __name__ == "__main__":
    main()
