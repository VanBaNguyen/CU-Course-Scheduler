## ⚠️ Disclaimer

## ⚠️ Disclaimer

> See the [LICENSE](./LICENSE) file for full restrictions.

By using this repository, you agree to these terms.


# CU Course Schedule Optimizer

Python Tool to create the most optimized schedule for CU students, at least the way I see it...
You do need to alter the code in the main() guard to input your courses.

## Features

- ✅ Parses university schedule data from `input.txt`
- ✅ Filters for only the courses you care about
- ✅ Automatically matches lectures with tutorials when needed
- ✅ Handles courses with **no tutorials required**
- ✅ Avoids **overlapping class times**
- ✅ Scores and ranks schedules based on:
  - Minimal number of campus days
  - Short gaps between classes
  - Avoiding early morning classes
  - Avoiding specific professors
- ✅ Displays top 3 best-fit schedules
- ✅ Visualizes the optimal schedule on a weekly calendar (via `matplotlib`)
- ✅ Supports late classes (up to 22:00)

### Install dependencies

Make sure you have Python 3.7+ and install `matplotlib`:

```bash
pip install matplotlib
```