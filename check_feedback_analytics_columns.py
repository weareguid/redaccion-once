import snowflake.connector
import streamlit as st

def check_feedback_analytics_columns():
    conn = snowflake.connector.connect(
        user=st.secrets["SNOWFLAKE"]["user"],
        password=st.secrets["SNOWFLAKE"]["password"],
        account=st.secrets["SNOWFLAKE"]["account"],
        warehouse=st.secrets["SNOWFLAKE"]["warehouse"],
        database=st.secrets["SNOWFLAKE"]["database"],
        schema=st.secrets["SNOWFLAKE"]["schema"],
        role=st.secrets["SNOWFLAKE"]["role"]
    )
    cur = conn.cursor()
    cur.execute("DESC VIEW feedback_analytics")
    print("Columns in feedback_analytics view:")
    for row in cur.fetchall():
        print(row)
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_feedback_analytics_columns() 