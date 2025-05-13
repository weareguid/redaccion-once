import os
import json
import re
from typing import Dict, Any

class NoteCleaner:
    def __init__(self, processed_dir: str, cleaned_dir: str):
        self.processed_dir = processed_dir
        self.cleaned_dir = cleaned_dir
        os.makedirs(self.cleaned_dir, exist_ok=True)

    def clean_text(self, text: str) -> str:
        # Remove extra whitespace and blank lines
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        text = text.strip()
        return text

    def clean_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        # Standardize and strip whitespace from all metadata fields
        return {k: v.strip() if isinstance(v, str) else v for k, v in metadata.items()}

    def clean_notes(self):
        for filename in os.listdir(self.processed_dir):
            if filename.endswith('.txt'):
                note_id = filename[:-4]
                txt_path = os.path.join(self.processed_dir, filename)
                meta_path = os.path.join(self.processed_dir, f'{note_id}_metadata.json')
                
                # Read content
                with open(txt_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                cleaned_content = self.clean_text(content)
                
                # Read metadata
                if os.path.exists(meta_path):
                    with open(meta_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    cleaned_metadata = self.clean_metadata(metadata)
                else:
                    cleaned_metadata = {}
                
                # Save cleaned content
                cleaned_txt_path = os.path.join(self.cleaned_dir, filename)
                with open(cleaned_txt_path, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                
                # Save cleaned metadata
                cleaned_meta_path = os.path.join(self.cleaned_dir, f'{note_id}_metadata.json')
                with open(cleaned_meta_path, 'w', encoding='utf-8') as f:
                    json.dump(cleaned_metadata, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Clean processed notes and metadata.')
    parser.add_argument('--processed_dir', required=True, help='Directory with processed notes')
    parser.add_argument('--cleaned_dir', required=True, help='Directory to save cleaned notes')
    args = parser.parse_args()
    cleaner = NoteCleaner(args.processed_dir, args.cleaned_dir)
    cleaner.clean_notes() 