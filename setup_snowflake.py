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
                COUNT(CASE WHEN rating >= 4 THEN 1 END) as positive_feedback_count,
                MAX(timestamp) as last_feedback_time
            FROM feedback
            GROUP BY category, text_type, length, tone, style
        """)
        
        # Grant permissions
        print("Setting up permissions...")
        # Create a dedicated role for the application
        app_role = "REDACCION_ONCE_ROLE"
        cur.execute(f"CREATE ROLE IF NOT EXISTS {app_role}")
        
        # Grant permissions to the application role
        cur.execute(f"GRANT USAGE ON WAREHOUSE {st.secrets['SNOWFLAKE']['warehouse']} TO ROLE {app_role}")
        cur.execute(f"GRANT USAGE ON DATABASE {st.secrets['SNOWFLAKE']['database']} TO ROLE {app_role}")
        cur.execute(f"GRANT USAGE ON SCHEMA {st.secrets['SNOWFLAKE']['schema']} TO ROLE {app_role}")
        cur.execute(f"GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA {st.secrets['SNOWFLAKE']['schema']} TO ROLE {app_role}")
        cur.execute(f"GRANT SELECT ON ALL VIEWS IN SCHEMA {st.secrets['SNOWFLAKE']['schema']} TO ROLE {app_role}")
        
        # Grant the role to the user
        cur.execute(f"GRANT ROLE {app_role} TO USER {st.secrets['SNOWFLAKE']['user']}")
        
        # Update the secrets.toml with the new role
        print("Updating secrets.toml with the new role...")
        secrets_path = ".streamlit/secrets.toml"
        if os.path.exists(secrets_path):
            with open(secrets_path, 'r') as f:
                secrets_content = f.read()
            
            # Update the role in the secrets file
            secrets_content = secrets_content.replace('role = "ACCOUNTADMIN"', f'role = "{app_role}"')
            
            with open(secrets_path, 'w') as f:
                f.write(secrets_content)
        
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