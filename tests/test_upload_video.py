import os
import uuid
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

# Import app and helper from the project
from app import app, allowed_video

TEST_VIDEO_NAME = 'test_video.mp4'
TEST_VIDEO_BYTES = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42mp41"  # tiny fake mp4 header

print('App upload folder:', app.config.get('VIDEO_UPLOAD_FOLDER'))

# Ensure upload folder exists
os.makedirs(app.config['VIDEO_UPLOAD_FOLDER'], exist_ok=True)

# Create a temp file to act as an uploaded video
tmp_path = os.path.join('/tmp', f"{uuid.uuid4().hex}_{TEST_VIDEO_NAME}")
with open(tmp_path, 'wb') as f:
    f.write(TEST_VIDEO_BYTES)

# Open and wrap in FileStorage (as Flask would provide)
with open(tmp_path, 'rb') as f:
    fs = FileStorage(stream=f, filename=TEST_VIDEO_NAME, content_type='video/mp4')

    print('Allowed video check:', allowed_video(fs))
    if allowed_video(fs):
        video_filename = f"{uuid.uuid4().hex}_{secure_filename(fs.filename)}"
        out_path = os.path.join(app.config['VIDEO_UPLOAD_FOLDER'], video_filename)
        fs.save(out_path)
        print('Saved test video to:', out_path)
        print('File size:', os.path.getsize(out_path))
    else:
        print('File did not pass allowed_video checks')

print('Temp file left at:', tmp_path)
print('Check static URL path: uploads/videos/{}'.format(video_filename if 'video_filename' in locals() else ''))
