#!/usr/bin/env python3
import sqlite3
from pathlib import Path

DB = Path(__file__).parent / 'mishwrites.db'
TEST_VIDEO = 'static/uploads/videos/fac2e6bf042749e39c95de5df1c6aafa_test_video.mp4'
IDS = (5,6)

if not DB.exists():
    print('Database file not found at', DB)
    raise SystemExit(1)

conn = sqlite3.connect(str(DB))
cur = conn.cursor()

print('Before update:')
for row in cur.execute('SELECT id, title, video_url, video_public_id FROM poem WHERE id IN (5,6);'):
    print(row)

# Perform the update: set video_url to TEST_VIDEO and clear video_public_id
cur.execute('UPDATE poem SET video_url = ?, video_public_id = NULL WHERE id IN (?, ?);', (TEST_VIDEO, IDS[0], IDS[1]))
conn.commit()

print('\nUpdate applied.')

print('\nAfter update:')
for row in cur.execute('SELECT id, title, video_url, video_public_id FROM poem WHERE id IN (5,6);'):
    print(row)

conn.close()
