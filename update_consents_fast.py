import os
import sys

def update_forms(directory):
    mobile_file = os.path.join(directory, 'mobile-al', 'index.html')
    main_file = os.path.join(directory, 'index.html')
    
    with open(mobile_file, 'r', encoding='utf-8') as f: mobile_content = f.read()
    with open(main_file, 'r', encoding='utf-8') as f: new_content = f.read()

    def get_all_spans_after(content, marker):
        spans = []
        idx = 0
        while True:
            idx = content.find(marker, idx)
            if idx == -1: break
            span_start = content.find('<span style="font-size:0', idx)
            if span_start == -1: break
            span_end = content.find('</span>', span_start) + 7
            spans.append(content[span_start:span_end])
            idx = span_end
        return spans

    old_nonm = get_all_spans_after(mobile_content, 'name="consent_nonmarketing"')
    old_m = get_all_spans_after(mobile_content, 'name="consent_marketing"')
    new_nonm = get_all_spans_after(new_content, 'name="consent_nonmarketing"')
    new_m = get_all_spans_after(new_content, 'name="consent_marketing"')
    
    if len(old_nonm) != 2 or len(new_nonm) != 2:
        print(f"Error: expected 2 non-marketing spans, got old={len(old_nonm)} new={len(new_nonm)}")
        return
        
    replacements = [
        (old_nonm[0], new_nonm[0]),
        (old_m[0], new_m[0]),
        (old_nonm[1], new_nonm[1]),
        (old_m[1], new_m[1])
    ]

    files_processed = 0
    files_updated = 0
    for root, dirs, files in os.walk(directory):
        if '.git' in root: continue
        for file in files:
            if file.endswith('.html'):
                files_processed += 1
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f: c = f.read()
                    orig_c = c
                    for old_span, new_span in replacements:
                        c = c.replace(old_span, new_span)
                    if c != orig_c:
                        with open(filepath, 'w', encoding='utf-8') as f: f.write(c)
                        files_updated += 1
                except Exception as e: pass

    print(f"Processed {files_processed} files. Updated {files_updated} files.")

if __name__ == "__main__":
    update_forms(sys.argv[1] if len(sys.argv) > 1 else ".")
