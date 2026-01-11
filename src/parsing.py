import os
import re
from pprint import pprint

def parse_input(wanted_courses, term):
    """
    Parse course data from term file.
    Returns list of: [has_number, course_code, section, prof, days, time, building]
    """
    structured_results = []
    seen_courses = set()

    # Locate the term file
    src_dir = os.path.dirname(os.path.abspath(__file__))
    project = os.path.dirname(src_dir)
    terms_dir = os.path.join(project, "terms")
    file_path = os.path.join(terms_dir, term)

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Cannot find term file: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            i += 1
            continue

        crn_match = re.search(r'\b(\d{5})\b', line)
        course_match = re.search(r'([A-Z]{4})\s+(\d{4})\s+([A-Z]+\d*)', line)
        
        if crn_match and course_match:
            subject = course_match.group(1)
            number = course_match.group(2)
            section = course_match.group(3)
            course_code = f"{subject} {number}"
            course_key = f"{course_code} {section}"
            
            if course_code not in wanted_courses:
                i += 1
                continue
            if course_key in seen_courses:
                i += 1
                continue
            seen_courses.add(course_key)
            
            has_number = bool(re.search(r'\d', section)) or section.endswith('T')
            
            parts = line.split('\t')
            prof_name = "Unknown"
            for part in reversed(parts):
                part = part.strip()
                if part and not re.search(r'(Meeting|Date|Yes|No|Lecture|Tutorial|Lab|\.5|^0$|\d{5})', part):
                    words = part.split()
                    if len(words) >= 2 and all(w[0].isupper() for w in words if w):
                        prof_name = part
                        break
            
            days = "Unknown"
            time_str = "Unknown"
            building = "Unknown"
            
            for j in range(i, min(i + 4, len(lines))):
                next_line = lines[j].strip()
                if 'Meeting Date:' in next_line or 'Days:' in next_line:
                    days_match = re.search(r'Days:\s*([A-Za-z ]*?)\s*Time:', next_line)
                    time_match = re.search(r'Time:\s*([\d:\- ]+)', next_line)
                    bldg_match = re.search(r'Building:\s*([^R]+?)\s*Room:', next_line)
                    
                    if days_match:
                        days = days_match.group(1).strip() or "Unknown"
                    if time_match:
                        time_str = time_match.group(1).strip()
                    if bldg_match:
                        building = bldg_match.group(1).strip()
                    break
            
            structured_results.append([
                has_number,
                course_code,
                section,
                prof_name,
                days,
                time_str,
                building
            ])
        
        i += 1

    pprint(structured_results)
    return structured_results
