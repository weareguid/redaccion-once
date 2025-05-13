import streamlit as st
import os
import json
from typing import Dict, List, Tuple

def load_notes(cleaned_dir: str) -> List[Tuple[str, Dict, str]]:
    """Load all notes and their metadata from the cleaned directory."""
    notes = []
    metadata_files = [f for f in os.listdir(cleaned_dir) if f.endswith('_metadata.json')]
    
    for metadata_file in sorted(metadata_files):
        # Get the base name without '_metadata.json'
        base_name = metadata_file.replace('_metadata.json', '')
        content_file = f"{base_name}.txt"
        
        metadata_path = os.path.join(cleaned_dir, metadata_file)
        content_path = os.path.join(cleaned_dir, content_file)
        
        # Debug logging
        st.write(f"Processing: {metadata_file}")
        st.write(f"Base name: {base_name}")
        st.write(f"Content file: {content_file}")
        st.write(f"Content path: {content_path}")
        
        try:
            # Load metadata
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Load content
            if os.path.exists(content_path):
                with open(content_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    # Extract just the text content, removing metadata headers
                    if "Texto:" in content:
                        content = content.split("Texto:", 1)[1].strip()
            else:
                st.error(f"Content file not found: {content_path}")
                content = "Content file not found"
            
            notes.append((base_name, metadata, content))
            
        except Exception as e:
            st.error(f"Error loading note {base_name}: {str(e)}")
    
    return notes

def main():
    st.set_page_config(page_title="News Notes Viewer", layout="wide")
    st.title("News Notes Viewer")
    
    # Load all notes
    notes = load_notes("cleaned")
    
    # Show total number of notes
    st.sidebar.info(f"Total notes: {len(notes)}")
    
    # Extract unique categories and levels for filtering
    categories = sorted(set(meta['category'] for _, meta, _ in notes if 'category' in meta))
    levels = sorted(set(meta['level'] for _, meta, _ in notes if 'level' in meta))
    
    # Sidebar filters
    st.sidebar.header("Filters")
    selected_category = st.sidebar.selectbox("Category", ["All"] + categories, label_visibility="visible")
    selected_level = st.sidebar.selectbox("Level", ["All"] + levels, label_visibility="visible")
    
    # Filter notes based on selection
    filtered_notes = notes
    if selected_category != "All":
        filtered_notes = [(id, meta, content) for id, meta, content in filtered_notes 
                         if meta.get('category') == selected_category]
    if selected_level != "All":
        filtered_notes = [(id, meta, content) for id, meta, content in filtered_notes 
                         if meta.get('level') == selected_level]
    
    # Show number of filtered notes
    if len(filtered_notes) != len(notes):
        st.sidebar.info(f"Filtered notes: {len(filtered_notes)}")
    
    # Create two columns
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Notes")
        # Create a list of note titles
        note_titles = [f"{meta.get('title', id)}" for id, meta, _ in filtered_notes]
        if note_titles:
            selected_index = st.selectbox("Select a note:", range(len(note_titles)), 
                                        format_func=lambda x: note_titles[x],
                                        key="note_selector",
                                        label_visibility="visible")
        else:
            st.warning("No notes found matching the selected filters.")
            selected_index = None
    
    with col2:
        if selected_index is not None and filtered_notes:
            note_id, metadata, content = filtered_notes[selected_index]
            
            # Display metadata
            st.subheader("Metadata")
            for key, value in metadata.items():
                st.text(f"{key}: {value}")
            
            # Display content
            st.subheader("Content")
            st.text_area("Note content", value=content, height=400, key="content", label_visibility="visible")

if __name__ == "__main__":
    main() 