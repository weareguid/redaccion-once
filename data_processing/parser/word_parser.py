"""
Word document parser for extracting text and metadata from articles.
"""
import os
import re
import json
from docx import Document
from typing import List, Tuple, Dict, Any

class WordParser:
    def __init__(self):
        # Patterns for metadata extraction
        self.metadata_patterns = {
            'title': r'^\d+\.\s+(.+?)$',
            'type': r'Tipo de Nota:\s*(.+?)$',
            'level': r'Nivel:\s*(.+?)$',
            'category': r'Categoría temática:\s*(.+?)$',
        }
        self.note_separator = r'^\d+\.\s+'  # Pattern to identify start of new notes

    def extract_metadata(self, text: str) -> Dict[str, str]:
        """Extract metadata from text using regex patterns."""
        metadata = {}
        lines = text.split('\n')
        
        for line in lines:
            for key, pattern in self.metadata_patterns.items():
                match = re.match(pattern, line.strip())
                if match:
                    metadata[key] = match.group(1).strip()
                    break
        
        return metadata

    def parse_document(self, file_path: str) -> List[Tuple[Dict[str, str], str]]:
        """Parse a Word document and extract metadata and content for each note."""
        doc = Document(file_path)
        notes = []
        current_note = []
        current_metadata = {}
        
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if not text:
                continue
                
            # Check if this is the start of a new note
            if re.match(self.note_separator, text):
                # Save previous note if exists
                if current_note:
                    content = '\n'.join(current_note)
                    notes.append((current_metadata, content))
                    current_note = []
                    current_metadata = {}
                
                # Start new note
                current_note.append(text)
                current_metadata = self.extract_metadata(text)
            else:
                current_note.append(text)
                # Update metadata if this line contains metadata
                new_metadata = self.extract_metadata(text)
                current_metadata.update(new_metadata)
        
        # Add the last note
        if current_note:
            content = '\n'.join(current_note)
            notes.append((current_metadata, content))
        
        return notes

    def process_directory(self, input_dir: str, output_dir: str) -> List[Dict[str, Any]]:
        """Process all Word documents in the input directory."""
        os.makedirs(output_dir, exist_ok=True)
        processing_summary = []
        
        for filename in os.listdir(input_dir):
            if filename.endswith('.docx'):
                input_path = os.path.join(input_dir, filename)
                try:
                    notes = self.parse_document(input_path)
                    
                    for i, (metadata, content) in enumerate(notes, 1):
                        note_id = f"{os.path.splitext(filename)[0]}_note_{i}"
                        
                        # Save content
                        content_path = os.path.join(output_dir, f"{note_id}.txt")
                        with open(content_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        # Save metadata
                        metadata_path = os.path.join(output_dir, f"{note_id}_metadata.json")
                        with open(metadata_path, 'w', encoding='utf-8') as f:
                            json.dump(metadata, f, ensure_ascii=False, indent=2)
                        
                        processing_summary.append({
                            'file_name': filename,
                            'note_id': note_id,
                            'metadata': metadata,
                            'output_files': {
                                'content': content_path,
                                'metadata': metadata_path
                            }
                        })
                        
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
        
        # Save processing summary
        summary_path = os.path.join(output_dir, 'processing_summary.json')
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(processing_summary, f, ensure_ascii=False, indent=2)
        
        return processing_summary

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Parse Word documents containing news articles.')
    parser.add_argument('--input_dir', required=True, help='Input directory containing Word documents')
    parser.add_argument('--output_dir', required=True, help='Output directory for processed files')
    
    args = parser.parse_args()
    
    word_parser = WordParser()
    word_parser.process_directory(args.input_dir, args.output_dir) 