# Time-based Task Scheduler (Greedy Algorithm)

## Overview
A user-friendly version of the Job Sequencing project where users enter **task durations** instead of deadlines.
The system selects tasks that fit within available total time and maximize profit.

### Algorithm Used
Greedy approach based on **profit-to-time ratio**.

### Steps
1. Accept tasks (name, duration, profit)
2. Ask for available total time
3. Sort tasks by profit/time ratio (descending)
4. Add tasks until no more fit in the time limit

### How to Run
1. Unzip this folder.
2. Open `index.html` in a browser.
3. Add tasks or load the sample.
4. Enter total available time and click **Run Scheduler**.

### Example
| Task | Time | Profit |
|------|------|--------|
| Study | 2 | 60 |
| Workout | 1 | 40 |
| Lecture | 3 | 80 |

If available time = 4 hours → Scheduler picks `Lecture` + `Workout`.

**Total Profit = 120**
