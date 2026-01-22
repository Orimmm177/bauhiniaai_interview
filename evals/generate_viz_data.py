import json
import os
import glob
import sys

def main():
    runs_dir = os.path.join(os.path.dirname(__file__), 'outputs', 'runs')
    web_dir = os.path.join(os.path.dirname(__file__), 'web')
    output_file = os.path.join(web_dir, 'data.js')

    if not os.path.exists(runs_dir):
        print(f"Error: Runs directory not found at {runs_dir}")
        return

    os.makedirs(web_dir, exist_ok=True)

    json_files = glob.glob(os.path.join(runs_dir, "*.json"))
    records = []
    
    print(f"Found {len(json_files)} run files.")

    for f in json_files:
        try:
            with open(f, 'r', encoding='utf-8') as fd:
                data = json.load(fd)
                # Add filename for reference
                data['_filename'] = os.path.basename(f)
                
                # Determine Pass/Fail and Score for easier frontend consumption
                is_pass = True
                total_score = 0
                
                grades = data.get('grades', [])
                for g in grades:
                    if g.get('result') == 'FAIL':
                        is_pass = False
                    
                    if g.get('metric') == 'rubric_eval':
                        if g.get('result') == 'FAIL':
                            is_pass = False
                        
                        s = g.get('total_score', 0)
                        if s == '-': s = 0
                        try:
                            total_score = float(s)
                        except (ValueError, TypeError):
                            total_score = 0

                data['_is_pass'] = is_pass
                data['_total_score'] = total_score
                
                records.append(data)
        except Exception as e:
            print(f"Error reading {f}: {e}")

    # Sort by timestamp descending
    records.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

    # Write as a JS variable
    js_content = f"window.EVAL_DATA = {json.dumps(records, ensure_ascii=False, indent=2)};"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(js_content)

    print(f"Successfully wrote {len(records)} records to {output_file}")

if __name__ == "__main__":
    main()
