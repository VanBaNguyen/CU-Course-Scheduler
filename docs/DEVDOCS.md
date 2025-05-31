# CU CourseScheduler — Developer Documentation

## 1. Purpose

The package assembles the best possible weekly timetable for a student given

1. a list of desired courses

2. text term files that contain every offered lecture/tutorial section

3. an exclusion list of professors (EXCLUDE_PROFS) you do not want to take.

The optimiser removes or penalises unwanted professors, respects tutorial‑lecture pairings, rejects any schedule with time collisions, and ranks the remainder with a heuristic that prefers fewer campus days, shorter gaps, later start times, and friendly professors.
The winning timetable is rendered as a colour‑coded grid (blue = normal, red = unavoidable excluded prof).

## 2. Start

```bash
# 1.  install deps
python -m pip install matplotlib

# 2.  clone or copy this folder
tree
├── parsing.py
├── optimal_schedule.py
├── fall.txt         # example data
└── winter.txt

# 3.  edit the block at the bottom of optimal_schedule.py …
#     – point to the desired term file
#     – supply your own wanted‑course list
#     – tweak EXCLUDE_PROFS if needed

python3 optimal_schedule.py      # launches optimisation + plot
```

## 3. Input file format (fall.txt, winter.txt)

Carleton Central's course viewer is literally a mess if pasted and so the parser tries its best to skip over anything unneeded. A known limitation is that if the fall or winter text file is formatted with too little indentation or tabs, the following courses will not be read properly.

Generally, what is wanted from each course listing:
```bash
COMP 3007  A   John Doe                                 <‑‑ line‑0:   code  section  professor
Days: Mon Wed    Time: 10:05 - 11:25   Room: 435        <‑‑ line‑1:   meeting pattern
```
Important:

Tutorials end with a digit (A1, T02, …).

“Unknown” time or days means an online / asynchronous section.

## 4. Configuration knobs

EXCLUDE_PROFS: Hard blacklist. Any lecture/tutorial with a professor whose display name equals a member of this set is removed from consideration.

## 5. Control Flow

```mermaid
flowchart TD
    subgraph parsing.py
       IN[term.txt] --> P[parse_input()] --> SR[structured_results]
    end

    subgraph optimal_schedule.py
       SR --> BS[build_slots()]
       BS --> CG[group_by_course()]
       CG --> VS[generate_valid_schedules()]
       VS --> SC[score_schedule()]
       SC --> SORT[sort + pick top N]
       SORT --> TTY[display_top_schedules()]
       SORT --> PLOT[plot_schedule()]
    end
```

### 5.1 parse_input() → list[StructuredRow]

Returns a list whose items have this order and meaning:

| Index | Field                | Example                                           |
| ----: | -------------------- | ------------------------------------------------- |
|     0 | `has_number`  (bool) | `True` for tutorials (`A1`, `T01`…), else `False` |
|     1 | `course_code`        | `"COMP 3007"`                                     |
|     2 | `section`            | `"A"`                                             |
|     3 | `prof_name`          | `"John Doe"`                                      |
|     4 | `days` (str)         | `"Mon Wed"`                                       |
|     5 | `time` (str)         | `"10:05 - 11:25"` or `"Unknown"`                  |

### 5.2 build_slots()

Transforms each row into a slot dict ready for collision testing:

```python
{
  'has_number':  False,
  'course':      'COMP 3007',
  'section':     'A',
  'prof':        'John Doe',
  'days':        ['Mon','Wed'],
  'start':       datetime.time(10,5),
  'end':         datetime.time(11,25),
  'original':    <same list row passed in>,
  # 'forced_excluded': True   ← set later only if no good prof exists
}
```

### 5.3 group_by_course()

Collects every slot under its course key.

### 5.4 generate_valid_schedules()

1. Split each course into lecture‐like (has_number == False) and tutorial‐like (True).

2. Filter lectures through _preferred_mains()

    If at least one lecture is taught by an acceptable prof → only keep those.

    Otherwise keep all (because the course is still needed) and mark them forced_excluded = True.

For every lecture chosen, attach tutorials whose section prefix matches (A ↔ A1, etc.).

Enumerate the Cartesian product so every course contributes exactly one lecture plus (possibly) one tutorial.

Reject any combination where two slots overlap in time and day.

### 5.5 score_schedule()

score = (days_on_campus × 1000) + gap_minutes + early_class_penalty

Score was formerly adjusted with a AVOID_PROFS variable where the professors listed simply lowered the score of a given schedule.

### 5.6 plot_schedule()

Creates a weekday grid from 08:00 – 22:00

Draws one rectangle per slot and per day occurrence

Colour picks:

    sky‑blue – professor not in exclusion set, or another acceptable prof exists for that course.

    light‑coral/red – professor in exclusion set and every lecture of that course is likewise excluded (no alternative).

## 6. Extending / maintaining

### 6.1 Adding new terms

Just drop another text export (summer.txt, 2025‑fall.txt…) in the same directory; pass its filename to parse_input().

### 6.2 GUI

Maybe in the future with Flask...

## Limitations

Assumes lectures meet ≤ 2 days per week (but more would just duplicate rectangles, not break logic).

Tutorials must share the prefix letter with their lecture; cross‑course shared labs aren’t handled.

Text file inputs must be formatted in a way the parser can reliably read.