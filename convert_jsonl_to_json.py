import json

input_path = 'model_training/data/training_data.jsonl'
output_path = 'training_data.json'

data = []
with open(input_path, 'r', encoding='utf-8') as infile:
    for line in infile:
        line = line.strip()
        if line:
            data.append(json.loads(line))

with open(output_path, 'w', encoding='utf-8') as outfile:
    json.dump(data, outfile, ensure_ascii=False, indent=2)

print(f"Converted {input_path} to {output_path} as a JSON array.") 