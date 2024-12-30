import curses
import pandas as pd
import os
from datetime import datetime


def view_reservations(mydb): 
    os.system('clear')

    # Gather Reservation Information
    curses.endwin()
    user_fname = input("Please input your first name here: ")
    user_lname = input("Please input your last name here: ")
    user_room_code = input("Please specify a room code here (otherwise enter 'Any'): ")
    user_bed_type = input("Please specify a bed type here (otherwise enter 'Any'): ")
    user_check_in = input("Please specify a check in date here (format yyyy-mm-dd): ")
    user_check_out = input("Please specify a check out date here (format yyyy-mm-dd): ")
    user_children = int(input("How many children?: "))
    user_adults = int(input("How many adults?: "))

    print("Searching...")

    #Execute sql query with provided data

    # TODO: room_name, room_code, cost_of_stay, bed_type

    try: 
        params = (user_check_in, user_check_out, user_children, user_adults, user_room_code, 
                  user_room_code, user_bed_type, user_bed_type, user_check_in, user_check_out, 
                  user_check_in, user_check_out, user_children, user_adults)
        
        query = """
WITH RECURSIVE date_range AS (
    SELECT %s AS stay_date  -- user_check_in
    UNION ALL
    SELECT DATE_ADD(stay_date, INTERVAL 1 DAY)
    FROM date_range
    WHERE stay_date < %s  -- user_check_out
), 

available_rooms AS (
    SELECT 
        ROW_NUMBER() OVER (ORDER BY r.RoomName) AS ranked, 
        r.RoomName, 
        r.RoomCode, 
        r.bedType, 
        r.maxOcc, 
        r.BasePrice
    FROM lab7_rooms AS r
    WHERE r.maxOcc >= (%s + %s)  -- user_children + user_adults
        AND (r.RoomCode = %s OR %s = 'Any')  -- user_room_code
        AND (r.bedType = %s OR %s = 'Any')  -- user_bed_type
        AND NOT EXISTS (
            SELECT 1
            FROM lab7_reservations AS re
            WHERE r.RoomCode = re.Room
              AND %s < re.CheckOut  -- user_check_in
              AND %s > re.CheckIn   -- user_check_out
        )
),

days_split AS (
    SELECT 
        SUM(CASE 
            WHEN DAYOFWEEK(stay_date) IN (2, 3, 4, 5, 6) THEN 1  -- Weekdays
            ELSE 0                                        
        END) AS total_WeekDays,
        SUM(CASE 
            WHEN DAYOFWEEK(stay_date) IN (1, 7) THEN 1  -- Weekends
            ELSE 0                                       
        END) AS total_WeekEnds
    FROM date_range
),

suggestions AS (
    SELECT 
        ar.ranked, 
        ar.RoomName, 
        ar.RoomCode, 
        ar.bedType, 
        (ar.BasePrice * ds.total_WeekDays + 1.1 * ar.BasePrice * ds.total_WeekEnds) AS cost_of_stay
    FROM available_rooms AS ar
    CROSS JOIN days_split AS ds
),

alternative_rooms AS (
    SELECT 
        ROW_NUMBER() OVER (ORDER BY r.RoomName) AS ranked, 
        r.RoomName, 
        r.RoomCode, 
        r.bedType, 
        (re.Rate * ds.total_WeekDays + 1.1 * re.Rate * ds.total_WeekEnds) AS cost_of_stay
    FROM lab7_rooms AS r
    JOIN lab7_reservations AS re 
        ON r.RoomCode = re.Room
    CROSS JOIN days_split AS ds
    WHERE NOT (%s BETWEEN re.CheckIn AND re.CheckOut)  -- user_check_in
        AND NOT (%s BETWEEN re.CheckIn AND re.CheckOut)  -- user_check_out
        AND r.maxOcc >= (%s + %s)  -- user_children + user_adults
)

SELECT 
    ranked, 
    RoomName, 
    RoomCode, 
    bedType, 
    cost_of_stay
FROM suggestions
WHERE EXISTS (SELECT 1 FROM available_rooms)

UNION ALL

SELECT 
    ranked, 
    RoomName, 
    RoomCode, 
    bedType, 
    cost_of_stay
FROM alternative_rooms
WHERE NOT EXISTS (SELECT 1 FROM available_rooms)
LIMIT 5; 
        """

        # cursor = mydb.cursor()
        # cursor.execute(query, params)
        # result = cursor.fetchall()
        df = pd.read_sql_query(query, mydb, params=params)

        print(df)

        selected_row = int(input("Which reservation would you like? (select rank)"))
        reservation_data = df.iloc[selected_row - 1]
        room_name = reservation_data['RoomName']
        bed_type = reservation_data['bedType']
        room_code = reservation_data['RoomCode']
        cost_of_stay = reservation_data['cost_of_stay']

        print("Your selected reservation: \n" + str(reservation_data))    
            
        print(f"Type [Yes] to confirm your reservation for {user_adults + user_children} people starting on {user_check_in} ending on {user_check_out} for room {room_name}")
        if input() == 'Yes':

            check_in_date = datetime.strptime(user_check_in, '%Y-%m-%d')
            check_out_date = datetime.strptime(user_check_out, '%Y-%m-%d')

            stay_duration = (check_out_date - check_in_date).days

            # Calculate rate (cost_of_stay / stay_duration)
            if stay_duration > 0:
                rate = cost_of_stay / stay_duration
             
            query = '''
                INSERT INTO lab7_reservations (CODE, Room, CheckIn, CheckOut, Rate, LastName, FirstName, Adults, Kids)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)            
            '''
            real_room_code = char_5(room_code)

            params = (real_room_code, room_name, user_check_in, user_check_out, rate, user_lname, user_fname, user_adults, user_children)
            cursor = mydb.cursor()
            cursor.execute(query, params)

            mydb.commit()

            print(f"Placing Reservation for {user_fname}, {user_lname}"
                  f"{room_code}, {room_name}, {bed_type}"
                  f"{user_check_in} -> {user_check_out}"
                  f"{user_adults}"
                  f"{user_children}"
                  f"{cost_of_stay}")
        else: 
            print("Reservation not submitted...\n Returning to the Main Menu")
            return

    except Exception as e:
        print(f"An error occurred: {e}")
        input("Reservation not submitted properly")

    finally: 
        cursor.close()



def char_5(value):
    # Convert to string, truncate to 5 characters, and pad if necessary
    value = str(value)  # Ensure input is a string
    return value[:5].ljust(5) 

