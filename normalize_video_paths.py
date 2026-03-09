#!/usr/bin/env python3
import sqlite3
from pathlib import Path

DB = Path(__file__).parent / 'mishwrites.db'
if not DB.exists():
    print('Database not found at', DB)
    raise SystemExit(1)

conn = sqlite3.connect(str(DB))
cur = conn.cursor()

print('Rows to normalize (video_url starts with static/ or /static/):')
for row in cur.execute("SELECT id, video_url FROM poem WHERE video_url LIKE 'static/%' OR video_url LIKE '/static/%';"):
    print(row)

cur.execute("UPDATE poem SET video_url = SUBSTR(video_url, 8) WHERE video_url LIKE 'static/%';")
cur.execute("UPDATE poem SET video_url = SUBSTR(video_url, 9) WHERE video_url LIKE '/static/%';")
conn.commit()

print('\nAfter normalization:')
for row in cur.execute("SELECT id, video_url FROM poem WHERE id IN (5,6);"):
    print(row)

conn.close()
