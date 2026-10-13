# Let's write a python script to find the closest combinations of shift assignments to the target
import pandas as pd

logs = [
    ("01-05", "07:08:00", "14:26:30"),
    ("02-05", "07:12:00", "14:20:51"),
    ("03-05", "14:06:06", "21:18:36"),
    ("04-05", "14:09:06", "21:32:43"),
    ("05-05", "21:09:44", "21:13:19"),
    ("06-05", "07:46:39", "07:46:50"),
    ("07-05", "07:46:39", None), # LIBUR
    ("08-05", None, None),        # LIBUR
    ("09-05", "07:19:16", "14:08:52"),
    ("10-05", "07:13:17", "14:20:32"),
    ("11-05", "14:12:55", "21:41:58"),
    ("12-05", "22:10:07", "20:55:13"),
    ("13-05", "07:46:13", "21:02:05"),
    ("14-05", "07:46:13", "07:46:30"),
    ("15-05", "07:46:13", None), # LIBUR
    ("16-05", None, None),        # LIBUR
    ("17-05", "07:24:22", "14:28:02"),
    ("18-05", None, None),        # LIBUR
    ("19-05", "14:09:12", "21:23:27"),
    ("20-05", "14:22:13", "14:22:13"),
    ("21-05", "21:10:39", "21:11:36"),
    ("22-05", "08:05:40", "08:05:54"),
    ("23-05", "08:05:40", None), # LIBUR
    ("24-05", None, None),        # LIBUR
    ("25-05", "14:12:15", "21:18:18"),
    ("26-05", None, "21:18:06"),
    ("27-05", "14:06:28", "14:06:28")
]

target_wm = 34 * 3600 + 6 * 60 + 45 # 122805 s
target_wp = 13 * 3600 + 31 * 60 + 19 # 48679 s

parsed_logs = []
for dt, msk, plg in logs:
    if not msk and not plg:
        continue
    sec_in = None
    if msk:
        parts = msk.split(':')
        sec_in = int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
    sec_out = None
    if plg:
        parts = plg.split(':')
        sec_out = int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
    parsed_logs.append({
        'date': dt,
        'msk': msk,
        'plg': plg,
        'sec_in': sec_in,
        'sec_out': sec_out
    })

# We'll calculate lateness and early checkouts for each day for all possible shifts:
# P: Pagi (07:00 - 14:00)
# S: Siang (14:00 - 21:00)
# M: Malam (21:00 - 07:00+1) -> checkout is early relative to 07:00 next morning (31*3600)
# D: Dinas (07:30 - 16:00)
# L: Libur (0, 0)

# Let's save all daily options to a list
shift_opts = ['P', 'S', 'M', 'D', 'L']

# Let's write a solver that prints out the closest sum to target_wm and target_wp
# Since n=23 (working days), 5^23 is too large.
# But we can limit each day's options based on common sense:
# For example:
# - If check-in is around 07:00-08:00, the shift is likely P, D or L.
# - If check-in is around 14:00, the shift is likely S or L.
# - If check-in is around 21:00-22:00, the shift is likely M or L.
# - If check-in is None, it could be any shift where check-in was missed (Datang Kosong), so lateness is 0 but checkout early is evaluated.

# Let's define restricted options for each day:
options = {}
for item in parsed_logs:
    dt = item['date']
    if item['plg'] is None:
        options[dt] = ['L']
    else:
        sec = item['sec_in']
        if sec is None:
            options[dt] = ['S', 'P', 'M', 'D', 'L']
        else:
            h = sec / 3600.0
            opts = []
            if 7 <= h <= 8.5:
                opts = ['P', 'D']
            elif 13.5 <= h <= 14.5:
                opts = ['S']
            elif 20.5 <= h <= 22.5:
                opts = ['M']
            else:
                opts = ['P', 'S', 'M', 'D']
            opts.append('L')
            options[dt] = opts

# Now we run a search using a genetic algorithm or simply randomized local search / hill climbing,
# or backtracking with pruning to find the closest match!
# Since we want to find the closest match, let's write a simple randomized search (hill climbing with multiple restarts)
# which is extremely effective for this!

import random

def get_fitness(sol_map):
    total_wm = 0
    total_wp = 0
    for dt, sh in sol_map.items():
        if sh == 'L':
            continue
            
        item = [x for x in parsed_logs if x['date'] == dt][0]
        sec_in = item['sec_in']
        sec_out = item['sec_out']
        
        if sh == 'P':
            start = 7 * 3600
            end = 14 * 3600
        elif sh == 'S':
            start = 14 * 3600
            end = 21 * 3600
        elif sh == 'M':
            start = 21 * 3600
            end = 31 * 3600
        elif sh == 'D':
            start = 7.5 * 3600
            end = 16 * 3600
            
        lat = 0
        if sec_in is not None:
            lat = max(0, sec_in - start)
            
        early = 0
        if sec_out is not None:
            early = max(0, end - sec_out)
            
        total_wm += lat
        total_wp += early
        
    diff_wm = abs(total_wm - target_wm)
    diff_wp = abs(total_wp - target_wp)
    return diff_wm + diff_wp, total_wm, total_wp

# Run a simple search
best_score = float('inf')
best_sol = None
best_wm = 0
best_wp = 0

for restart in range(1000):
    # Initialize random solution
    sol_map = {}
    for dt, opts in options.items():
        sol_map[dt] = random.choice(opts)
        
    # Hill climbing
    improved = True
    while improved:
        improved = False
        score, wm, wp = get_fitness(sol_map)
        
        # Try mutations
        for dt, opts in options.items():
            current_sh = sol_map[dt]
            for o in opts:
                if o != current_sh:
                    sol_map[dt] = o
                    new_score, new_wm, new_wp = get_fitness(sol_map)
                    if new_score < score:
                        score = new_score
                        wm = new_wm
                        wp = new_wp
                        improved = True
                    else:
                        sol_map[dt] = current_sh # revert
                        
    if score < best_score:
        best_score = score
        best_sol = sol_map.copy()
        best_wm = wm
        best_wp = wp
        if score == 0:
            break

def format_seconds(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

print(f"Best Score (Diff): {best_score} seconds")
print(f"Target WM: {format_seconds(target_wm)} | Sol WM: {format_seconds(best_wm)}")
print(f"Target WP: {format_seconds(target_wp)} | Sol WP: {format_seconds(best_wp)}")

if best_sol:
    print("\nBest Solution details:")
    for dt, sh in sorted(best_sol.items()):
        item = [x for x in parsed_logs if x['date'] == dt][0]
        msk = item['msk']
        plg = item['plg']
        
        if sh == 'L':
            print(f"  Date {dt}: Libur (L) | In {msk} | Out {plg}")
            continue
            
        if sh == 'P':
            start, end = 7 * 3600, 14 * 3600
        elif sh == 'S':
            start, end = 14 * 3600, 21 * 3600
        elif sh == 'M':
            start, end = 21 * 3600, 31 * 3600
        elif sh == 'D':
            start, end = 7.5 * 3600, 16 * 3600
            
        lat = 0
        if item['sec_in'] is not None:
            lat = max(0, item['sec_in'] - start)
        early = 0
        if item['sec_out'] is not None:
            early = max(0, end - item['sec_out'])
            
        print(f"  Date {dt}: Shift {sh} | In {msk} (late {format_seconds(lat)}) | Out {plg} (early {format_seconds(early)})")
