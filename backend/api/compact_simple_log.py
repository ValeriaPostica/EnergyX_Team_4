#!/usr/bin/env python3
import os, re, shutil

# Paths
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(HERE, '..', 'data'))
SIMPLE_LOG = os.path.join(DATA_DIR, 'simple_log.txt')
BACKUP = os.path.join(DATA_DIR, 'simple_log.bak')

# Make a backup
if os.path.exists(SIMPLE_LOG):
    shutil.copy2(SIMPLE_LOG, BACKUP)
    print(f"Backed up {SIMPLE_LOG} -> {BACKUP}")
else:
    print(f"No simple_log at {SIMPLE_LOG}")

# Read and scan lines
pattern = re.compile(r'^\s*(\d)\)\s*(.*)$')
latest = { '0':'', '1':'', '2':'', '3':'' }

with open(SIMPLE_LOG, 'r', encoding='utf-8') as f:
    for raw in f:
        line = raw.rstrip('\n')
        m = pattern.match(line)
        if m:
            idx = m.group(1)
            if idx in latest:
                latest[idx] = m.group(2)

# Write compacted file (keep order 0..3)
with open(SIMPLE_LOG, 'w', encoding='utf-8') as f:
    for i in ['0','1','2','3']:
        content = latest.get(i, '')
        if content:
            f.write(f"{i}){content}\n")
        else:
            f.write(f"{i})\n")

print('Wrote compacted simple_log with keys 0..3:')
with open(SIMPLE_LOG, 'r', encoding='utf-8') as f:
    print(f.read())
