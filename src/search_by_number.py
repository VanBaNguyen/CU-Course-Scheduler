import requests
import time
import re
import os
from bs4 import BeautifulSoup

BASE_URL = "https://central.carleton.ca/prod"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://central.carleton.ca",
    "Referer": f"{BASE_URL}/bwysched.p_select_term?wsea_code=EXT",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1"
}


def create_session(term):
    """Create and initialize a session for the given term."""
    s = requests.Session()
    s.headers.update(HEADERS)
    
    print("Initializing session...")
    r = s.get(f"{BASE_URL}/bwysched.p_select_term?wsea_code=EXT", timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    sess_input = soup.find("input", {"name": "session_id"})
    
    if not sess_input:
        print("Error: Blocked or Session ID missing.")
        return None, None
    
    sess_id = sess_input["value"]
    print(f"Session established: {sess_id}")

    print(f"Setting term to {term}...")
    s.post(f"{BASE_URL}/bwysched.p_search_fields", data={
        "term_code": term, 
        "session_id": sess_id, 
        "wsea_code": "EXT"
    }, timeout=30)
    
    return s, sess_id


def search_by_course_number(course_number, term, session=None, sess_id=None):
    """
    Search for a course by course number.
    Returns formatted course data matching winter.txt format.
    """
    try:
        # Create session if not provided
        if session is None or sess_id is None:
            session, sess_id = create_session(term)
            if session is None:
                return None

        time.sleep(1)

        payload = [
            ('wsea_code', 'EXT'), ('term_code', term), ('session_id', sess_id),
            ('ws_numb', ''), ('sel_aud', 'dummy'),
            ('sel_subj', 'dummy'), ('sel_subj', ''), 
            ('sel_camp', 'dummy'), ('sel_sess', 'dummy'), ('sel_sess', ''),      
            ('sel_attr', 'dummy'), ('sel_levl', 'dummy'), ('sel_levl', ''),      
            ('sel_schd', 'dummy'), ('sel_schd', ''),      
            ('sel_insm', 'dummy'), ('sel_link', 'dummy'), ('sel_wait', 'dummy'),
            ('sel_day', 'dummy'), ('sel_day', 'm'), ('sel_day', 't'), ('sel_day', 'w'),
            ('sel_day', 'r'), ('sel_day', 'f'), ('sel_day', 's'), ('sel_day', 'u'),
            ('sel_begin_hh', 'dummy'), ('sel_begin_hh', '0'),
            ('sel_begin_mi', 'dummy'), ('sel_begin_mi', '0'),
            ('sel_begin_am_pm', 'dummy'), ('sel_begin_am_pm', 'a'),
            ('sel_end_hh', 'dummy'), ('sel_end_hh', '0'),
            ('sel_end_mi', 'dummy'), ('sel_end_mi', '0'),
            ('sel_end_am_pm', 'dummy'), ('sel_end_am_pm', 'a'),
            ('sel_instruct', 'dummy'), ('sel_special', 'dummy'), ('sel_special', 'N'),
            ('sel_resd', 'dummy'), ('sel_breadth', 'dummy'), 
            ('sel_number', course_number),
            ('sel_crn', ''),
            ('block_button', '')
        ]
        
        print(f"Searching for course number {course_number}...")
        r = session.post(f"{BASE_URL}/bwysched.p_course_search", data=payload, timeout=30)
        
        return parse_course_data(r.text)

    except Exception as e:
        print(f"Error: {e}")
        return None


def parse_course_data(html):
    """Parse HTML and extract course data in the winter.txt format."""
    soup = BeautifulSoup(html, "html.parser")
    lines = []
    seen = set()
    
    # Find all table rows
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"])
            if not cells:
                continue
            
            # Get text from each cell
            row_text = []
            for cell in cells:
                text = cell.get_text(separator=' ', strip=True)
                row_text.append(text)
            
            line = '\t'.join(row_text)
            
            # Skip duplicates
            if line in seen:
                continue
            
            # Keep lines that look like course data
            if any([
                re.search(r'\b\d{5}\b', line),  # Has a 5-digit CRN
                'Meeting Date:' in line,
                'Also Register in:' in line,
                'Section Information:' in line,
            ]):
                seen.add(line)
                lines.append(line)
    
    return '\n'.join(lines) if lines else None


def get_term_filepath(term):
    """Get filepath based on term code's last two digits."""
    suffix = term[-2:]
    if suffix == "10":
        name = "winter.txt"
    elif suffix == "20":
        name = "summer.txt"
    elif suffix == "30":
        name = "fall.txt"
    else:
        name = f"term_{term}.txt"
    return os.path.join(PROJECT_ROOT, "terms", name)
