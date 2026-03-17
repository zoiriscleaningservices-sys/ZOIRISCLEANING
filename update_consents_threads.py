import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

def get_all_spans_after(content, marker):
    spans = []
    idx = 0
    while True:
        idx = content.find(marker, idx)
        if idx == -1: break
        span_start = content.find('<span', idx)
        if span_start == -1: break
        span_end = content.find('</span>', span_start) + 7
        spans.append(content[span_start:span_end])
        idx = span_end
    return spans

def update_forms(directory):
    mobile_file = os.path.join(directory, 'mobile-al', 'index.html')
    main_file = os.path.join(directory, 'index.html')
    
    with open(mobile_file, 'r', encoding='utf-8') as f: mobile_content = f.read()
    with open(main_file, 'r', encoding='utf-8') as f: new_content = f.read()

    old_nonm = get_all_spans_after(mobile_content, 'name="consent_nonmarketing"')
    old_m = get_all_spans_after(mobile_content, 'name="consent_marketing"')
    new_nonm = get_all_spans_after(new_content, 'name="consent_nonmarketing"')
    new_m = get_all_spans_after(new_content, 'name="consent_marketing"')
    
    if len(old_nonm) != 2 or len(new_nonm) != 2:
        print(f"Error: expected 2 non-marketing spans, got old={len(old_nonm)} new={len(new_nonm)}", flush=True)
        return
        
    replacements = [
        (old_nonm[0], new_nonm[0]),
        (old_m[0], new_m[0]),
        (old_nonm[1], new_nonm[1]),
        (old_m[1], new_m[1])
    ]

    print("Gathering files...", flush=True)
    all_files = []
    
    for d in os.listdir(directory):
        d_path = os.path.join(directory, d)
        if os.path.isdir(d_path):
            if d.endswith('-al') or d.endswith('-tx'):
                for root, dirs, files in os.walk(d_path):
                    for file in files:
                        if file.endswith('.html'):
                            all_files.append(os.path.join(root, file))
    
    for file in os.listdir(directory):
        if file.endswith('.html') and file != 'index.html':
            all_files.append(os.path.join(directory, file))

    total_files = len(all_files)
    print(f"Total HTML files to process: {total_files}", flush=True)
    
    processed_count = 0
    updated_count = 0

    def process_file(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                c = f.read()
            orig_c = c
            for old_span, new_span in replacements:
                c = c.replace(old_span, new_span)
            
            updated = False
            if c != orig_c:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(c)
                updated = True
            return True, updated
        except Exception:
            return False, False

    print("Processing files...", flush=True)
    t0 = time.time()
    
    # Use ThreadPoolExecutor for I/O bound
    with ThreadPoolExecutor(max_workers=32) as executor:
        for i, (success, updated) in enumerate(executor.map(process_file, all_files), 1):
            if success:
                processed_count += 1
            if updated:
                updated_count += 1
            
            if i % 1000 == 0:
                print(f"[{i}/{total_files}] Processed, Updates so far: {updated_count}", flush=True)

    t1 = time.time()
    print(f"Done. Processed {processed_count} files, updated {updated_count} files in {t1-t0:.2f}s.", flush=True)

if __name__ == "__main__":
    update_forms(sys.argv[1] if len(sys.argv) > 1 else ".")
