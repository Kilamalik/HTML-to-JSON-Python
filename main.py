# Author: Malik Samath
# GitHub: https://github.com/Kilamalik

# ------------------------------------------------------------------#
# ------------------------------------------------------------------#
# ------------------------------------------------------------------#
# ------------------------------------------------------------------#

# import json
# import re
from openpyxl import Workbook
from bs4 import BeautifulSoup, Tag
from bs4 import Comment


def main(section):
    with open('timetable.html', 'r') as content:
        soup = BeautifulSoup(content, 'html.parser')

    wb = Workbook()
    ws = wb.active
    dataTemp = ['startTime', 'endTime', 'dayOfTheWeek', 'module', 'venue', 'group', 'batch']
    ws.append(dataTemp)

    # these new tags are created to replace the span comments with the td tags
    # this is done so that the day counter can increment. It does not increment when there are span comments and hence, outputs wrong days for the slots
    myTag = soup.new_tag("td")
    myTag.string = "---"

    myTag2 = soup.new_tag("td")
    myTag2.string = "---"

    myTag3 = soup.new_tag("td")
    myTag3.string = "---"

    myTag4 = soup.new_tag("td")
    myTag4.string = "---"

    # loop through all the timetable only tables
    tables = soup.find_all('table', class_=[section])
    for table in tables:
        thead = table.thead
        tbody = table.tbody

        # batch group only
        thead_tr_batch = thead.find_all('tr')[0].th.text
        print(thead_tr_batch)

        # days of the table
        thead_tr_days = thead.find_all('tr')[1]

        # Removes the footer table row because it causes complications during the scraping process
        tbody.find('tr', {'class': 'foot'}).decompose()

        # recursive=False prevents the loop from accessing the desired tags within inner tables
        rows = tbody.find_all('tr', recursive=False)
        # loops through all the rows of a tables body accept the footer row
        for row in rows:
            row_Time = row.th.text

            spanned = 0  # holds the index to the nextToComment array
            nextToComment = []  # holds whats next to the comment in the row to be compared to data variable in the coming for loop
            previousToComment = []  # holds whats previous to the comment in the row to be compared to data variable in the coming for loop
            dayIndex = 0  # holds the index to the thead_tr_days.find_all('th') array

            # finding span comments within the rows column to be able to identify its location
            comments = row.find_all(text=lambda text: isinstance(text, Comment))

            # for every comment replace it with the td tag.
            # comments array contains all the comments of the current row.
            # each comment is replaced with a different tag because using same tag for each comment does not work.
            # the duplicate tags get ignored and the day increment fails to work then.
            # there will be max 5 span comments in a row but a 5th tag is not needed since it would move on the next row by then
            for index, comment in enumerate(comments):
                previousToComment.append(comment.findPrevious())
                if index == 0:
                    comment.replaceWith(myTag)
                elif index == 1:
                    comment.replaceWith(myTag2)
                elif index == 2:
                    comment.replaceWith(myTag3)
                elif index == 3:
                    comment.replaceWith(myTag4)

            # gets the td tags which are the columns of the selected row
            # recursive=False prevents the loop from accessing the desired tags within inner tables
            row_tdList = row.find_all(['td'], recursive=False)

            # enumeration and index not needed atm. Index (not used atm) only works if data is enumerated.
            for index, data in enumerate(row_tdList):

                # The day is obtained by first getting the tr that contains all the days in the row, and then getting the th tag by index
                slotDay = thead_tr_days.find_all('th')[dayIndex].text

                # Gathering data of each slot
                if data.table:
                    # print('this is a table at time', row_Time, 'and day', slotDay)
                    data.table_tr = data.table.find_all("tr")  # get all the rows of this inner table
                    sessionHourHand = int(row_Time.split(":")[0]) + 1

                    # For formatting reasons need to make sure the end time is stored, for example, as hh:mm instead of h:mm
                    if sessionHourHand < 10:
                        sessionEndTime = "0" + str(sessionHourHand) + ":" + row_Time.split(":")[1]
                    else:
                        sessionEndTime = str(sessionHourHand) + ":" + row_Time.split(":")[1]

                    # Manually get slot data of each slot in each column.
                    data.table_tr_firstSubBatch = data.table_tr[0].find_all("td")[
                        0].string  # subbatch of first column in the cell
                    data.table_tr_firstSession = data.table_tr[1].find_all("td")[
                        0].string  # module of first column in the cell
                    data.table_tr_firstVenue = data.table_tr[3].find_all("td")[
                        0].string  # venue of first column in the cell

                    # Storing the data of the first slot
                    dataTemp = [row_Time, sessionEndTime, slotDay, data.table_tr_firstSession, data.table_tr_firstVenue,
                                data.table_tr_firstSubBatch, thead_tr_batch]
                    ws.append(dataTemp)

                    # this condition is in place due to some tabled cells not having a second column
                    # the if block only runs if a second columne exists
                    if len(data.table_tr[0].find_all("td")) > 1:
                        data.table_tr_secondSubBatch = data.table_tr[0].find_all("td")[
                            1].string  # subbatch of second column in the cell
                        data.table_tr_secondSession = data.table_tr[1].find_all("td")[
                            1].string  # module of second column in the cell
                        data.table_tr_secondVenue = data.table_tr[3].find_all("td")[
                            1].string  # venue of second column in the cell

                        # Storing the data of the second slot
                        dataTemp = [row_Time, sessionEndTime, slotDay, data.table_tr_secondSession,
                                    data.table_tr_secondVenue, data.table_tr_secondSubBatch, thead_tr_batch]
                        ws.append(dataTemp)

                elif data.text == '---' or data.text == '-x-':
                    dayIndex = dayIndex + 1
                    continue
                else:
                    # print('this is a normal table at time', row_Time, 'and day', slotDay)

                    # rowspan - To use in sessionEndTime calculation
                    # conditional check due to some normal slot cells not having the rowspan class
                    # if rowspan class exists then if block runs, else the else block runs
                    if data.attrs != {}:
                        rowspan = int(data['rowspan'])
                    else:
                        rowspan = int(1)
                    sessionHourHand = int(row_Time.split(":")[0]) + rowspan

                    # For formatting reasons need to make sure the end time is stored as hh:mm instead of h:mm
                    if sessionHourHand < 10:
                        sessionEndTime = "0" + str(sessionHourHand) + ":" + row_Time.split(":")[1]
                    else:
                        sessionEndTime = str(sessionHourHand) + ":" + row_Time.split(":")[1]

                    # Storing everything except instructor/lecturer information
                    normalTd = data.contents
                    if len(normalTd) == 6:  # if the normal slot cell has 6 elements
                        # checks if batch comes first in the 6 element slot cell, then run the if block
                        # else run the else block if session comes first
                        if thead_tr_batch in normalTd[0]:
                            normalTd_batch = normalTd[0]  # The batch is in te 0th index of this array
                            normalTd_session = normalTd[2]  # The module is the in the 2nd index of this array
                            normalTd_venue = normalTd[4]  # The venue is in the 4th index of this array
                            dataTemp = [row_Time, sessionEndTime, slotDay, normalTd_session, normalTd_venue,
                                        normalTd_batch, thead_tr_batch]
                        else:
                            normalTd_session = normalTd[0]  # The module is in the 0th index of this array
                            normalTd_venue = normalTd[4]  # The venue is in the 4th index of this array
                            dataTemp = [row_Time, sessionEndTime, slotDay, normalTd_session, normalTd_venue,
                                        thead_tr_batch, thead_tr_batch]

                        ws.append(dataTemp)

                    elif len(normalTd) == 8:  # if the normal slot cell has 8 elements
                        normalTd_batch = normalTd[0]  # The batch info is in the 0th index of this array
                        normalTd_session = normalTd[2]  # The module is in the 2nd index of this array
                        normalTd_venue = normalTd[6]  # The venue is in the 4th index of this array
                        dataTemp = [row_Time, sessionEndTime, slotDay, normalTd_session, normalTd_venue, normalTd_batch,
                                    thead_tr_batch]
                        ws.append(dataTemp)

                dayIndex = dayIndex + 1
    if section == 'odd_table':
        wb.save('Timetable1.xlsx')
    elif section == 'even_table':
        wb.save('Timetable2.xlsx')


if __name__ == "__main__":
    choice = input(
        "**********Please ensure the HTML timetable file is renamed to timetable.html and is within the same directory as this script*********\n" +
        "The timetable.html will have to be scraped into two separate excel files\n" +
        "Both files will be needed to be fed separately into the initial configuration of the IAS system\n" +
        "Enter anything to proceed:")

    print("\nGathering the first half into Timetable1.xlsx\n")

    main('odd_table')

    print("\nGathering the second half into Timetable2.xlsx\n")

    main('even_table')

    input("\nEnter anything to close.")
