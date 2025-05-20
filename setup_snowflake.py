import snowflake.connector
import streamlit as st
import os

def setup_snowflake():
    try:
        # Connect to Snowflake
        conn = snowflake.connector.connect(
            user=st.secrets["SNOWFLAKE"]["user"],
            password=st.secrets["SNOWFLAKE"]["password"],
            account=st.secrets["SNOWFLAKE"]["account"],
            warehouse=st.secrets["SNOWFLAKE"]["warehouse"],
            role="ACCOUNTADMIN"  # Using ACCOUNTADMIN role for setup
        )
        
        cur = conn.cursor()
        
        # Create database and schema
        print("Creating database and schema...")
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {st.secrets['SNOWFLAKE']['database']}")
        cur.execute(f"USE DATABASE {st.secrets['SNOWFLAKE']['database']}")
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {st.secrets['SNOWFLAKE']['schema']}")
        cur.execute(f"USE SCHEMA {st.secrets['SNOWFLAKE']['schema']}")
        
        # Create tables
        print("Creating tables...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id NUMBER AUTOINCREMENT,
                timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                rating NUMBER,
                comments TEXT,
                generated_text TEXT,
                category TEXT,
                text_type TEXT,
                length TEXT,
                sources TEXT,
                tone TEXT,
                style TEXT,
                additional_instructions TEXT
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS model_metrics (
                id NUMBER AUTOINCREMENT,
                model_name TEXT,
                model_version TEXT,
                training_accuracy FLOAT,
                validation_accuracy FLOAT,
                last_updated TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            )
        """)
        
        # Create views
        print("Creating views...")
        cur.execute("""
            CREATE OR REPLACE VIEW feedback_analytics AS
            SELECT 
                category,
                text_type,
                length,
                tone,
                style,
                AVG(rating) as avg_rating,
                COUNT(*) as feedback_count,
                COUNT(CASE WHEN rating >= 4 THEN 1 END) as positive_feedback_count
            FROM feedback
            GROUP BY category, text_type, length, tone, style
        """)
        
        # Grant permissions
        print("Setting up permissions...")
        # First, create the role if it doesn't exist
        cur.execute(f"CREATE ROLE IF NOT EXISTS {st.secrets['SNOWFLAKE']['user']}")
        
        # Then grant permissions
        cur.execute(f"GRANT USAGE ON WAREHOUSE {st.secrets['SNOWFLAKE']['warehouse']} TO ROLE {st.secrets['SNOWFLAKE']['user']}")
        cur.execute(f"GRANT USAGE ON DATABASE {st.secrets['SNOWFLAKE']['database']} TO ROLE {st.secrets['SNOWFLAKE']['user']}")
        cur.execute(f"GRANT USAGE ON SCHEMA {st.secrets['SNOWFLAKE']['schema']} TO ROLE {st.secrets['SNOWFLAKE']['user']}")
        cur.execute(f"GRANT CREATE TABLE ON SCHEMA {st.secrets['SNOWFLAKE']['schema']} TO ROLE {st.secrets['SNOWFLAKE']['user']}")
        cur.execute(f"GRANT CREATE VIEW ON SCHEMA {st.secrets['SNOWFLAKE']['schema']} TO ROLE {st.secrets['SNOWFLAKE']['user']}")
        
        # Grant the role to the user
        cur.execute(f"GRANT ROLE {st.secrets['SNOWFLAKE']['user']} TO USER {st.secrets['SNOWFLAKE']['user']}")
        
        conn.commit()
        print("Snowflake setup completed successfully!")
        
    except Exception as e:
        print(f"Error during Snowflake setup: {str(e)}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    setup_snowflake() 