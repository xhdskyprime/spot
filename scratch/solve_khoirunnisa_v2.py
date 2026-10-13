import datetime

# Cleaned actual logs from task 162
# Date, Masuk, Pulang
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

# Targets
target_wm = 34 * 3600 + 6 * 60 + 45 # 122805 s
target_wp = 13 * 3600 + 31 * 60 + 19 # 48679 s

# Parse logs to seconds
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

# Shift hours definition
# Pagi (P): 07:00 to 14:00
# Siang (S): 14:00 to 21:00
# Malam (M): 21:00 to 07:00 (next day) -> 31 * 3600
# Dinas (D): 07:30 to 16:00
# Libur (L): No calculation (0, 0)
# Wait, are there other shifts?
# What if some days have "Libur" but have taps? In SPOT, if a day is marked as Libur, does it compute 0? Yes.
# Let's write a recursive search to assign shift to each day and see if we can match target_wm and target_wp.
# To make it fast, let's limit choices for each day.
# If Day is marked as LIBUR in logs, it is Libur (L)
# For other days:
# If check-in is around 7am and checkout around 14pm: P is highly likely.
# If check-in around 14pm and checkout around 21pm: S is highly likely.
# If check-in around 21pm: M is highly likely.

candidates = {}
for item in parsed_logs:
    dt = item['date']
    if item['plg'] is None: # marked as LIBUR in our logs
        candidates[dt] = ['L']
    else:
        # Check based on check-in time
        sec = item['sec_in']
        opts = []
        
        # If check-in is None (day 26)
        if sec is None:
            opts = ['S', 'P', 'M', 'D', 'L']
        else:
            h = sec / 3600.0
            if 6 <= h <= 9:
                opts.append('P')
                opts.append('D')
            if 13 <= h <= 15:
                opts.append('S')
            if 20 <= h <= 23:
                opts.append('M')
                opts.append('S') # Siang late check-in?
            
            # Add other options just in case
            if not opts:
                opts = ['P', 'S', 'M', 'D']
            opts.append('L') # Could always be Libur
            
        candidates[dt] = opts

# Let's do a backtracking search to find a combination that sums to target_wm and target_wp
sol = []

def search(idx, current_wm, current_wp):
    if idx == len(parsed_logs):
        if current_wm == target_wm and current_wp == target_wp:
            return True
        return False
        
    # Pruning: if current exceeds target, stop
    if current_wm > target_wm or current_wp > target_wp:
        return False
        
    item = parsed_logs[idx]
    dt = item['date']
    sec_in = item['sec_in']
    sec_out = item['sec_out']
    
    for sh in candidates[dt]:
        # Calculate lateness and early checkout
        lat = 0
        early = 0
        
        if sh != 'L':
            if sh == 'P':
                start = 7 * 3600
                end = 14 * 3600
            elif sh == 'S':
                start = 14 * 3600
                end = 21 * 3600
            elif sh == 'M':
                start = 21 * 3600
                end = 31 * 3600 # 24 + 7
            elif sh == 'D':
                start = 7.5 * 3600
                end = 16 * 3600
                
            if sec_in is not None:
                lat = max(0, sec_in - start)
            if sec_out is not None:
                early = max(0, end - sec_out)
                
        sol.append((dt, sh, lat, early))
        if search(idx + 1, current_wm + lat, current_wp + early):
            return True
        sol.pop()
        
    return False

if search(0, 0, 0):
    print("MATCH FOUND!")
    total_lat = 0
    total_early = 0
    for dt, sh, lat, early in sol:
        # Find original times
        log_item = [x for x in parsed_logs if x['date'] == dt][0]
        msk = log_item['msk']
        plg = log_item['plg']
        print(f"Date {dt}: Shift {sh} | In {msk} (late {lat}s) | Out {plg} (early {early}s)")
        total_lat += lat
        total_early += early
    print(f"Total Lateness: {total_lat}s, Total Early: {total_early}s")
else:
    print("No combination matches both targets exactly with standard shift definitions.")
    # Let's search with relaxed targets or check if there is an alternative shift definition
    # e.g. Dinas start is 07:30, end is 14:30? Or Friday is different?
    # Let's do a wider search or print the closest combinations
