## CU Course‑Schedule Optimizer

Small Python Project that takes CU timetable data and spits out the best‑looking week you can get.

~~~bash
pip install matplotlib
python schedule_opt.py
~~~

### What it does

1. **Read your raw term file** (`fall.txt`, `winter.txt`, `summer.txt`).  
2. **Keep just the courses you list** in the `COURSES = {...}` set.  
3. **Pair every lecture with the right tutorial/lab** (or skip if none).  
4. **Test every combination** for time clashes and throw the bad ones out.  
5. **Score each clash‑free schedule**  
   * fewer campus days  
   * shorter gaps  
   * no 8 a.m. misery  
   * (optionally) avoid named people  
6. **Rank & print the top 3** plus one fully drawn timetable.

### Features

| Feature | How to use |
|---------|------------|
| **Dark‑mode plot** | `DARK_MODE = True` |
| **Hide / show room & building** | `SHOW_LOCATION = False` |
| Subtle dotted grid above blocks | default in dark mode |
| Handles online / unknown‑time classes gracefully | automatic |

### Other Things
* Supports classes until **22:00**.    
* Colour‑coded blocks, readable text labels.  
* Tweaks are just booleans at the bottom of the script.  

### Quick start

Open **`schedule_opt.py`**, scroll to the bottom and edit:

~~~python
COURSES       = {"COMP 1234", "MATH 1010", "BUSI 2020"}
TERM_FILE     = winter          # fall / winter / summer
SHOW_LOCATION = True
DARK_MODE     = False
~~~
