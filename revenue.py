import curses
import pandas as pd
import os

def view_revenue(mydb):
    curses.endwin() #close main menu window 
    os.system('clear')

    try: 
        print("Gathering Revenue Report...")

        query = """
        WITH RevenuePerStay AS (
    SELECT
        Room,
        CheckIn,
        Checkout,
        ROUND(Rate / (DATEDIFF(Checkout, CheckIn) + 1), 2) AS daily_revenue
    FROM lab7_rooms 
    JOIN lab7_reservations on lab7_reservations.Room = lab7_rooms.RoomCode
    WHERE YEAR(CheckIn) = YEAR(CURRENT_DATE) or YEAR(Checkout) = YEAR(CURRENT_DATE)
), 
MonthlyBreakdown as (
    SELECT
        Room,
        YEAR(month_start) as year,
        MONTH(month_start) as month,
        ROUND(DATEDIFF(LEAST(Checkout, LAST_DAY(month_start)), GREATEST(CheckIn, month_start)) + 1, 0) 
        * daily_revenue as monthly_revenue
    FROM RevenuePerStay
    CROSS JOIN (
        SELECT 
            DATE_FORMAT(DATE_ADD(DATE(CURRENT_DATE), INTERVAL -(MONTH(CURRENT_DATE)-1) MONTH), '%Y-%m-01') + INTERVAL seq MONTH as month_start
        FROM (
            SELECT 0 as seq UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4
            UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9
            UNION ALL SELECT 10 UNION ALL SELECT 11
        ) as seq
    ) as months
    WHERE Checkout >= month_start AND CheckIn <= LAST_DAY(month_start)
), 
RoomMonthlyRevenue as (
    SELECT
        Room,
        month,
        SUM(monthly_revenue) as monthly_revenue
    FROM MonthlyBreakdown
    GROUP BY Room, month
), 
PivotedRevenue as (
    SELECT
        Room,
        COALESCE(SUM(CASE WHEN month = 1 THEN monthly_revenue END), 0) as Jan,
        COALESCE(SUM(CASE WHEN month = 2 THEN monthly_revenue END), 0) as Feb,
        COALESCE(SUM(CASE WHEN month = 3 THEN monthly_revenue END), 0) as Mar,
        COALESCE(SUM(CASE WHEN month = 4 THEN monthly_revenue END), 0) as Apr,
        COALESCE(SUM(CASE WHEN month = 5 THEN monthly_revenue END), 0) as May,
        COALESCE(SUM(CASE WHEN month = 6 THEN monthly_revenue END), 0) as Jun,
        COALESCE(SUM(CASE WHEN month = 7 THEN monthly_revenue END), 0) as Jul,
        COALESCE(SUM(CASE WHEN month = 8 THEN monthly_revenue END), 0) as Aug,
        COALESCE(SUM(CASE WHEN month = 9 THEN monthly_revenue END), 0) as Sep,
        COALESCE(SUM(CASE WHEN month = 10 THEN monthly_revenue END), 0) as Oct,
        COALESCE(SUM(CASE WHEN month = 11 THEN monthly_revenue END), 0) as Nov,
        COALESCE(SUM(CASE WHEN month = 12 THEN monthly_revenue END), 0) as `Dec`
    FROM RoomMonthlyRevenue
    GROUP BY Room
)

SELECT 
    Room,
    Jan,
    Feb,
    Mar,
    Apr,
    May,
    Jun,
    Jul,
    Aug,
    Sep,
    Oct,
    Nov,
    `Dec`,
    (Jan + Feb + Mar + Apr + May + Jun + Jul + Aug + Sep + Oct + Nov + `Dec`) as YearlyTotal
FROM PivotedRevenue
UNION ALL
SELECT 
    'TOTALS' as Room,
    SUM(Jan) as Jan,
    SUM(Feb) as Feb,
    SUM(Mar) as Mar,
    SUM(Apr) as Apr,
    SUM(May) as May,
    SUM(Jun) as Jun,
    SUM(Jul) as Jul,
    SUM(Aug) as Aug,
    SUM(Sep) as Sep,
    SUM(Oct) as Oct,
    SUM(Nov) as Nov,
    SUM(`Dec`) as `Dec`,
    SUM(Jan + Feb + Mar + Apr + May + Jun + Jul + Aug + Sep + Oct + Nov + `Dec`) as YearlyTotal
FROM PivotedRevenue;
        """

        # cursor = mydb.cursor()
        # cursor.execute(query)

        # result = cursor.fetchall()
        # os.system('clear')

        # print(result)
        # input("press enter to return to menu")

        df = pd.read_sql_query(query, mydb)

        print(df)
        input("press enter to return to the menu")


    except Exception as e:
        print(f"An error occurred: {e}")




