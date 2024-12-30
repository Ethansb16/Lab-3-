import pandas as pd
import curses


# sql query to give rooms and rates details 
def view_rooms_and_rates(mydb):
    curses.endwin()

    try: 
        query = """
        With daysOccupied as (SELECT 
            r.RoomCode, 
            r.RoomName, 
            SUM(DATEDIFF(re.CheckOut, re.CheckIn)) as total_days
        FROM lab7_rooms as r
            JOIN lab7_reservations as re on re.Room = r.RoomCode
        WHERE DATEDIFF(re.CheckIn, CURDATE()) <= 180 
        GROUP BY r.RoomCode, r.RoomName
        ), 
                       
        lastStayLength as (
        SELECT 
            r1.RoomCode, 
            r1.RoomName, 
            DATEDIFF(MAX(re1.CheckOut), 
            (SELECT CheckIn 
                FROM lab7_reservations 
                WHERE Room = r1.RoomCode AND CheckOut = MAX(re1.CheckOut))) as lastStay
            FROM lab7_rooms as r1
            JOIN lab7_reservations as re1 on re1.Room = r1.RoomCode
            GROUP BY r1.RoomCode, r1.RoomName
        ), 
                       
        nextAvailableCheckIn as (
        SELECT 
            r2.RoomCode, 
            r2.RoomName, 
            MIN(re2.CheckOut) as nextCheckIn
        FROM lab7_rooms as r2
            LEFT JOIN lab7_reservations as re2 on r2.RoomCode = re2.Room
        WHERE re2.CheckOut >= CURDATE()
        GROUP BY r2.RoomCode, r2.RoomName
        )
                       
        SELECT 
            d.RoomName, 
            ROUND(total_days / 180, 2) as popularity_score, 
            COALESCE(n.nextCheckIn, 'Available now') as next_check_in, 
            l.lastStay as recent_stay_length
        FROM daysOccupied as d
        JOIN lastStayLength as l on l.RoomName = d.RoomName AND l.RoomCode = d.RoomCode
        LEFT JOIN nextAvailableCheckIn as n on n.RoomName = d.RoomName AND n.RoomCode = d.RoomCode
        ORDER BY popularity_score desc;"""

        # cursor = mydb.cursor()
        # cursor.execute(query)

        # result = cursor.fetchall()
        # print(result)

        df = pd.read_sql_query(query, mydb)

        print(df)
        input("press enter to return to the menu")

    except Exception as e:
        print(f"An error occurred: {e}")

