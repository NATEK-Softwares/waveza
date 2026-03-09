#!/usr/bin/env python3
import sqlite3
from pathlib import Path

DB = Path(__file__).parent / 'mishwrites.db'
URL = 'https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4'
IDS = (5,6)

if not DB.exists():
    print('Database not found at', DB)
    raise SystemExit(1)

conn = sqlite3.connect(str(DB))
cur = conn.cursor()

print('Before:')
for r in cur.execute('SELECT id, video_url FROM poem WHERE id IN (5,6);'):
    print(r)

cur.execute('UPDATE poem SET video_url = ? WHERE id IN (?, ?);', (URL, IDS[0], IDS[1]))
conn.commit()

print('\nAfter:')
for r in cur.execute('SELECT id, video_url FROM poem WHERE id IN (5,6);'):
    print(r)

conn.close()
