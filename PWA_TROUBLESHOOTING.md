# PWA Troubleshooting Guide

## 🔧 Installation Issues

### Issue: Install Button Not Appearing

#### Symptoms
- No install prompt in Chrome/Edge
- No "Add to Home Screen" option in Safari
- Install button not in address bar

#### Causes & Solutions

**Check 1: HTTPS Required**
```bash
# ✅ Correct
https://your-domain.com

# ❌ Fails
http://your-domain.com  # HTTP not allowed
http://localhost  # Localhost is OK exception
```

**Check 2: Manifest.json Invalid**
- Open DevTools → Application → Manifest
- Should show manifest loaded without errors
- Click "Errors" section and fix any issues
- Validate at [jsonlint.com](https://jsonlint.com/)

**Check 3: Required Manifest Fields**
```json
{
  "name": "WaveZA",
  "short_name": "WaveZA",
  "start_url": "/",
  "display": "standalone",
  "scope": "/",
  "icons": [
    {
      "src": "/path/to/icon.png",
      "sizes": "192x192 512x512",
      "type": "image/png"
    }
  ]
}
```

**Check 4: Service Worker Registration**
```javascript
// In browser console
navigator.serviceWorker.getRegistrations().then(r => {
    if (r.length === 0) {
        console.error('❌ No service worker registered!');
    } else {
        console.log('✅ SW registered:', r[0].scope);
    }
});
```

**Check 5: Icons Exist**
```bash
# Test each icon manually
curl -I https://your-domain.com/static/img/NEW/icons/android-chrome-512x512.png
# Should return HTTP 200
```

**Check 6: Web App Meta Tags**
```html
<!-- In <head> -->
<meta name="theme-color" content="#1a1a2e">
<meta name="mobile-web-app-capable" content="yes">
<link rel="manifest" href="/static/manifest.json">
```

#### Resolution
1. Fix HTTPS
2. Validate manifest.json
3. Verify icons accessible
4. Hard refresh: Ctrl+Shift+R
5. Wait 5 seconds, refresh again
6. Try on different device or browser

---

### Issue: Install Works but App Won't Open

#### Symptoms
- Install successful
- App icon on home screen
- Clicking opens blank page
- Wrong URL loads

#### Solutions

**Check 1: start_url in manifest.json**
```json
{
  "start_url": "/"  // ✅ Correct
  // or
  "start_url": "/index.html"  // ✅ Also correct
  
  // ❌ Wrong
  "start_url": "/app"  // Path that doesn't exist
}
```

**Check 2: Flask route exists**
```python
# ✅ Correct
@app.route('/')
def index():
    return render_template('index.html')

# ❌ Wrong - missing index route
@app.route('/app')
def app_page():
    ...
```

**Check 3: Clear app data**
- Android: Settings → Apps → WaveZA → Clear data
- iOS: Delete app, reinstall via Home Screen Add
- Desktop: Remove and reinstall app

#### Resolution
1. Verify `start_url` matches existing route
2. Test route in browser directly
3. Clear app cache and reinstall
4. Check server logs for 404 errors

---

## 🔔 Push Notification Issues

### Issue: No Push Notifications Received

#### Symptoms
- No notification on device
- Login shows as successful
- `/notify` endpoint works but no notification appears
- Browser doesn't ask for permission

#### Root Causes

**Check 1: Notification Permission**
```javascript
// In browser console
console.log('Permission:', Notification.permission);
// Expected: "granted"
// If "denied": User blocked notifications
// If "default": Permission never requested
```

**Fix Permission (User Action)**
- Browser: Settings → Notifications → Allow WaveZA
- Android: App info → Notifications → Enabled
- iPhone: Settings → WaveZA → Notifications

**Check 2: Push Subscription Saved**
```python
# In Python shell or endpoint
user = User.query.get(1)
print('Subscription:', user.push_subscription)
# Should show JSON, not None
```

**If None:**
```javascript
// Force subscription in browser console
navigator.serviceWorker.ready.then(async reg => {
    const sub = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: 'BASE64_VAPID_KEY'
    });
    console.log(JSON.stringify(sub));
    // Copy this and POST to /subscribe
});
```

**Check 3: VAPID Keys Configured**
```python
# In Python shell
from app import VAPID_PUBLIC_KEY, VAPID_PRIVATE_KEY
print('Public:', VAPID_PUBLIC_KEY[:20] + '...')
print('Private:', VAPID_PRIVATE_KEY[:20] + '...')
# Both should have values, not empty strings
```

**If empty:**
```env
# Update .env with:
VAPID_PUBLIC_KEY=your_public_key
VAPID_PRIVATE_KEY=your_private_key
VAPID_EMAIL=your@email.com

# Restart Flask
```

**Check 4: Service Worker Installed**
```javascript
// In browser console
navigator.serviceWorker.ready.then(reg => {
    console.log('SW Ready:', reg.active?.state);
    // Expected: "activated"
});
```

**Check 5: Server Logs**
```bash
# Look for errors like:
❌ Web push failed: ...
# Check logs:
tail -f server.log | grep "push"
```

#### Complete Resolution Steps

1. **Grant Permission**
   - Browser settings → Allow notifications
   - Refresh page

2. **Re-subscribe**
   - Clear browser cache: DevTools → Application → Clear storage
   - Refresh page
   - Should ask for permission again
   - Grant permission

3. **Verify Subscription Saved**
   - Check database: `user` table, `push_subscription` field
   - Should have JSON value

4. **Test Push**
   - Login
   - Visit `/notify`
   - Should receive notification

---

### Issue: Notification Received but Wrong Content

#### Symptoms
- Notification shows
- Wrong title/body
- Missing image
- Wrong URL on click

#### Solutions

**Check 1: Notification Service Worker Handler**
```javascript
// In service-worker.js, check push event:
self.addEventListener('push', event => {
    const data = event.data.json();
    console.log('Push data:', data);
    // Verify: title, body, url all present
});
```

**Check 2: Payload Structure**
```python
# When sending notification, structure should be:
payload = json.dumps({
    "title": "Title Here",  # ✅ Required
    "body": "Body text",     # ✅ Required
    "icon": "/path/to/icon.png",  # Icon URL
    "url": "/path/to/open",  # URL to open on click
    "tag": "notification-tag"  # Group notifications
})
```

**Check 3: Image URL Accessible**
```bash
# Test icon URL
curl -I https://your-domain.com/static/img/NEW/icons/android-chrome-512x512.png
# Should return HTTP 200
```

#### Resolution
1. Update push sending code with correct payload
2. Test with `/notify` endpoint
3. Check notification content in browser notification panel
4. Verify image URLs are absolute (not relative)

---

## 📴 Offline Issues

### Issue: App Doesn't Work Offline

#### Symptoms
- Can't access app when offline
- Pages show blank/error
- Offline.html not appearing
- No cached content

#### Causes & Solutions

**Check 1: Service Worker Not Installed**
```javascript
// DevTools → Application → Service Workers
// Should show: "[scope] activated and running"
// If not: Service worker failed to install
```

**Fix:**
```javascript
// Force reinstall in console:
navigator.serviceWorker.getRegistrations().then(regs => {
    return Promise.all(regs.map(reg => reg.unregister()));
}).then(() => {
    location.reload();
});
```

**Check 2: Cache Empty**
```javascript
// In DevTools → Application → Cache Storage
// Should see: "waveza-v1", "waveza-runtime-v1", "waveza-images-v1"
// If empty: May need to visit pages to populate cache
```

**Fix:**
- Visit various pages while online
- This populates cache automatically

**Check 3: Offline.html Route Missing**
```python
# app.py should have:
@app.route('/offline')
def offline():
    return render_template('offline.html'), 200

# If missing: Add it
```

**Check 4: Cache Size Limit Exceeded**
- Chrome: ~1GB total per domain
- Firefox: ~10% available disk
- Safari: ~1GB
- Edge: ~1GB

**Fix:**
- Clear cache: DevTools → Application → Clear storage
- Delete old cache versions

**Check 5: Service Worker Update Failed**
```javascript
// Check for errors:
navigator.serviceWorker.controller === null
// If true: SW not controlling current page

// Check update status:
navigator.serviceWorker.ready.then(reg => {
    reg.update().then(() => console.log('Updated'));
});
```

#### Step-by-Step Resolution

1. **Verify Service Worker**
   ```javascript
   navigator.serviceWorker.getRegistrations()
   // Should show active registration
   ```

2. **Check Cache Storage**
   - DevTools → Application → Cache Storage
   - Should see multiple caches

3. **Test Offline Mode**
   - DevTools → Network → Offline
   - Try to load page
   - Should show cached version or offline.html

4. **Clear and Reinstall**
   ```javascript
   // Force clear and reinstall
   navigator.serviceWorker.getRegistrations().then(regs => {
       regs.forEach(reg => reg.unregister());
   }).then(() => location.reload());
   ```

5. **Re-enable Online**
   - Uncheck Offline in DevTools
   - Refresh

---

### Issue: Offline Page Shows but Shouldn't

#### Symptoms
- App shows offline.html while online
- Network tab shows requests working
- Other device shows content fine

#### Causes

**Check 1: Network Detection Issue**
```javascript
// In browser console:
navigator.onLine
// Should be: true
```

**Check 2: Fetch Failing Even Though Online**
- Might be CORS error
- Might be authentication issue
- Check Network tab for 4xx/5xx errors

**Check 3: Service Worker Cache Serving Wrong Page**
- Service Worker may be serving offline page

**Fix:**
```javascript
// Clear all caches
caches.keys().then(names => {
    names.forEach(name => caches.delete(name));
}).then(() => location.reload());
```

---

## 🔄 Update Issues

### Issue: App Won't Update

#### Symptoms
- New version deployed
- Update banner doesn't show
- Still seeing old version
- New features not available

#### Solutions

**Check 1: Service Worker Update Check Interval**
- Default: Every 60 seconds
- Manual check:
```javascript
navigator.serviceWorker.ready.then(reg => reg.update());
```

**Check 2: Hard Refresh**
```
Windows: Ctrl + Shift + R
Mac: Cmd + Shift + R
```

**Check 3: Clear Cache**
- DevTools → Application → Clear storage
- Refresh

**Check 4: Manifest.json Versioning**
```json
{
  "version": "1.1.0"  // Update this
}
```

**Check 5: Service Worker File Modified**
- Service worker file needs to change for update detection
- Check modification time

#### Resolution
1. Hard refresh: Ctrl+Shift+R
2. Clear storage: DevTools → Clear
3. Close and reopen app
4. Force sync: `navigator.serviceWorker.ready.then(r => r.update())`

---

## 📱 Platform-Specific Issues

### iOS Issues

#### Problem: App Won't Install
**iOS 16.3 and Below:**
- PWA not supported
- User needs iOS 16.4+

**Fix:**
- Recommend user update iOS
- Or use Android/Chrome

#### Problem: No Notifications
**Expected:** Push notifications not supported in PWA on iOS
- iOS treats PWAs like bookmarks
- Standard Web Push not available
- This is an Apple limitation

**Alternative:**
- Email notifications instead
- In-app notification system
- Native app for full support

### Android Issues

#### Problem: Won't Install on Android
**Check:**
1. Using Chrome or Edge
2. HTTPS enabled
3. Manifest.json valid
4. Icons exist

**Fix:**
```bash
# Test with DevTools
Remote debugging → Chrome DevTools → Check manifest errors
```

---

## 🆘 Advanced Debugging

### Enable Verbose Logging

**In service-worker.js:**
```javascript
// Add at top:
const DEBUG = true;

// Wrap logs:
if (DEBUG) console.log('Debug message');
```

**In pwa-manager.js:**
```javascript
// Already has logging:
console.log('') // Green checks
console.error('') // Red X marks
```

### Network Request Debugging

DevTools → Network tab:
1. Filter by name or type
2. Click request
3. Check Headers, Preview, Response
4. Look for non-200 status codes

### Performance Analysis

DevTools → Lighthouse:
1. Run audit (PWA option)
2. Check score
3. Review "Errors" and "Warnings"
4. Fix issues listed

---

## 📞 Getting Help

### Check These First
1. ✅ Review PWA_SETUP_GUIDE.md
2. ✅ Check server logs
3. ✅ Verify DevTools Application tab
4. ✅ Test in Incognito window
5. ✅ Try different browser

### Provide When Reporting Issues

```
Browser: Chrome 120.0.1234.56
OS: Windows 10
Device: Desktop
Error: [Full error message]
Steps to reproduce:
1. ...
2. ...

Console output:
[Paste console.log output]

DevTools:
Service Worker status: ...
Cache status: ...
```

### Common Error Messages

| Error | Reason | Solution |
|-------|--------|----------|
| `Failed to register service worker` | JS syntax error | Check console for exact error |
| `Service Worker failed to install` | Fetch failed | Check offline.html route exists |
| `Push notification failed` | VAPID keys invalid | Regenerate and update .env |
| `Fetch failed in service worker` | Network error | Check CORS headers |

---

## ✅ Testing Checklist

Use this to verify everything works:

- [ ] Install prompt appears
- [ ] Installation succeeds
- [ ] App icon appears on home screen
- [ ] App opens in standalone mode
- [ ] Service Worker registers
- [ ] Notification permission requested
- [ ] Push notification received
- [ ] Click notification opens correct URL
- [ ] Can browse app while offline
- [ ] Cached pages display offline
- [ ] Offline.html shows for new pages
- [ ] App recognizes when back online
- [ ] Update banner appears on new version
- [ ] All features work in incognito
- [ ] Works on multiple devices

---

**Last Updated:** March 8, 2026  
**Version:** 1.0
