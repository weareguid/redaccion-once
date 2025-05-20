import snowflake.connector
import streamlit as st

def test_connection():
    try:
        print("Attempting to connect to Snowflake...")
        conn = snowflake.connector.connect(
            user=st.secrets["SNOWFLAKE"]["user"],
            password=st.secrets["SNOWFLAKE"]["password"],
            account=st.secrets["SNOWFLAKE"]["account"],
            warehouse=st.secrets["SNOWFLAKE"]["warehouse"],
            role="ACCOUNTADMIN"
        )
        print("Successfully connected to Snowflake!")
        
        # Test query
        cur = conn.cursor()
        cur.execute("SELECT current_version()")
        version = cur.fetchone()
        print(f"Snowflake version: {version[0]}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_connection() 