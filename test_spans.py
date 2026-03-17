import os
import sys

def test(directory):
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
            span_start = content.find('<span ', idx)
            if span_start == -1: break
            span_end = content.find('</span>', span_start) + 7
            spans.append(content[span_start:span_end])
            idx = span_end
        return spans

    old_nonm = get_all_spans_after(mobile_content, 'name="consent_nonmarketing"')
    old_m = get_all_spans_after(mobile_content, 'name="consent_marketing"')
    new_nonm = get_all_spans_after(new_content, 'name="consent_nonmarketing"')
    new_m = get_all_spans_after(new_content, 'name="consent_marketing"')
    
    print(f"Old nonm count: {len(old_nonm)}, Old m count: {len(old_m)}")
    print(f"New nonm count: {len(new_nonm)}, New m count: {len(new_m)}")

if __name__ == "__main__":
    test(sys.argv[1] if len(sys.argv) > 1 else ".")
