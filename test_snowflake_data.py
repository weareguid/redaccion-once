import snowflake.connector
import streamlit as st
from datetime import datetime

def test_snowflake_data():
    try:
        # Connect to Snowflake
        print("Connecting to Snowflake...")
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
        
        # Insert sample feedback data
        print("\nInserting sample feedback data...")
        sample_feedback = [
            (5, "Great article!", "This is a sample generated text about technology.", 
             "Technology", "Article", "Medium", "Tech News", "Professional", "Informative", 
             "Include latest trends"),
            (4, "Good content", "Another sample text about business strategy.", 
             "Business", "Blog Post", "Long", "Industry Reports", "Formal", "Analytical", 
             "Focus on ROI"),
            (3, "Average quality", "Sample text about marketing tips.", 
             "Marketing", "Social Media", "Short", "Social Media", "Casual", "Engaging", 
             "Make it viral")
        ]
        
        cur.executemany("""
            INSERT INTO feedback (
                rating, comments, generated_text, category, text_type, 
                length, sources, tone, style, additional_instructions
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, sample_feedback)
        
        # Insert sample model metrics
        print("\nInserting sample model metrics...")
        sample_metrics = [
            ("GPT-4", "1.0", 0.95, 0.92),
            ("GPT-3.5", "1.0", 0.90, 0.88)
        ]
        
        cur.executemany("""
            INSERT INTO model_metrics (
                model_name, model_version, training_accuracy, validation_accuracy
            ) VALUES (%s, %s, %s, %s)
        """, sample_metrics)
        
        # Query feedback analytics
        print("\nQuerying feedback analytics...")
        cur.execute("SELECT * FROM feedback_analytics")
        analytics_results = cur.fetchall()
        
        print("\nFeedback Analytics Results:")
        print("Category | Text Type | Length | Tone | Style | Avg Rating | Feedback Count | Positive Feedback")
        print("-" * 100)
        for row in analytics_results:
            print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]:.2f} | {row[6]} | {row[7]}")
        
        # Query model metrics
        print("\nQuerying model metrics...")
        cur.execute("SELECT * FROM model_metrics ORDER BY last_updated DESC")
        metrics_results = cur.fetchall()
        
        print("\nModel Metrics Results:")
        print("Model | Version | Training Accuracy | Validation Accuracy | Last Updated")
        print("-" * 80)
        for row in metrics_results:
            print(f"{row[1]} | {row[2]} | {row[3]:.2f} | {row[4]:.2f} | {row[5]}")
        
        conn.commit()
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    test_snowflake_data() 