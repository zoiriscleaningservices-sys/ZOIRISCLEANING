import os
import sys
from multiprocessing import Pool, cpu_count
import time

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

def process_chunk(chunk):
    filepaths, replacements = chunk
    files_processed = 0
    files_updated = 0
    for filepath in filepaths:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                c = f.read()
            orig_c = c
            for old_span, new_span in replacements:
                c = c.replace(old_span, new_span)
            if c != orig_c:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(c)
                files_updated += 1
            files_processed += 1
        except Exception:
            pass
    return files_processed, files_updated

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
    
    # We will only look at directories containing '-al' or '-tx' or are the root itself 
    # Since we know those are the ones generated
    for d in os.listdir(directory):
        d_path = os.path.join(directory, d)
        if os.path.isdir(d_path):
            if d.endswith('-al') or d.endswith('-tx'):
                for root, dirs, files in os.walk(d_path):
                    for file in files:
                        if file.endswith('.html'):
                            all_files.append(os.path.join(root, file))
    
    # Also add the root files if they are not index.html
    for file in os.listdir(directory):
        if file.endswith('.html') and file != 'index.html':
            all_files.append(os.path.join(directory, file))

    print(f"Total HTML files to process: {len(all_files)}", flush=True)
    
    num_procs = max(1, cpu_count() - 1)
    chunk_size = max(1, len(all_files) // num_procs)
    chunks = [(all_files[i:i + chunk_size], replacements) for i in range(0, len(all_files), chunk_size)]
    
    print(f"Processing with {num_procs} processes...", flush=True)
    t0 = time.time()
    try:
        with Pool(num_procs) as pool:
            results = pool.map(process_chunk, chunks)
        
        total_processed = sum(r[0] for r in results)
        total_updated = sum(r[1] for r in results)
        t1 = time.time()
        print(f"Processed {total_processed} files. Updated {total_updated} files in {t1-t0:.2f} seconds.", flush=True)
    except Exception as e:
        print(f"Error during multiprocessing: {e}", flush=True)

if __name__ == "__main__":
    update_forms(sys.argv[1] if len(sys.argv) > 1 else ".")
