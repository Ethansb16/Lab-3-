import curses
import os
import pandas as pd

def reservation_info(mydb):
    curses.endwin() #close main menu window 
    os.system('clear')

    # gather name information
    user_first_name = input("Please input desired First Name: ")

    if user_first_name == "": 
        user_first_name = "%"

    user_last_name = input("Please input desired Last Name: ")
    
    if user_last_name == "": 
        user_last_name = "%"
    
    # gather date range
    user_lower_range = input("Please input the lower date range (yyyy-mm-dd): ")
    user_upper_range = input("Please input the upper date range (yyyy-mm-dd): ")
    
    # gather room and reservation codes
    user_room_code = input("Please input desired Room Code: ")
    
    if user_room_code == "": 
        user_room_code = "%"
    
    user_res_code = input("Please input desired Reservation Code: ")
    
    if user_res_code == "": 
        user_res_code = "%"

    try: 
        print("Searching for reservations matching your input...")

        query = """
        SELECT * 
        FROM lab7_reservations as re 
            JOIN lab7_rooms as r on r.RoomCode = re.Room
        WHERE (re.FirstName LIKE %s) and
            (re.LastName LIKE %s) and 
            (re.CheckIn BETWEEN %s and %s) and
            (r.RoomCode LIKE %s) and 
            (re.Code LIKE %s )
        """
        # TODO: may need to check the data types for the dates

        params = (user_first_name, user_last_name, user_lower_range, user_upper_range, user_room_code, user_res_code)

        # cursor = mydb.cursor()
        # cursor.execute(query, params)

        # result = cursor.fetchall()
        df = pd.read_sql_query(query, mydb, params=params)


        os.system('clear')

        print(df)
        input("press enter to return to menu")


    except Exception as e:
        print(f"An error occurred: {e}")

