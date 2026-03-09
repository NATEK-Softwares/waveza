# WaveZA PWA Quick Reference

## 🚀 30-Second Setup

1. **Generate VAPID Keys** (one-time)
   ```bash
   npm install -g web-push
   web-push generate-vapid-keys
   ```

2. **Add to `.env`**
   ```
   VAPID_PUBLIC_KEY=<key>
   VAPID_PRIVATE_KEY=<key>
   VAPID_EMAIL=your@email.com
   ```

3. **Restart Flask**
   ```bash
   python app.py
   ```

✅ **Done!** PWA is live. Test at `https://your-domain.com`

---

## 📱 Installation URLs

### By Device

- **Android**: Open in Chrome → Install button in address bar
- **iOS 16.4+**: Open in Safari → Share → Add to Home Screen  
- **Chrome/Edge**: Open → Install button in address bar
- **Firefox**: Open → Menu → Install

---

## 🔔 Send Notifications

### In Python Code
```python
from app import send_push_notification
import json

user = User.query.get(1)
subscription = json.loads(user.push_subscription)

send_push_notification(
    subscription_info=subscription,
    message_title="Title",
    message_body="Body text",
    action_url="/path/to/action"
)
```

### Batch Notifications
```python
users = User.query.filter(User.push_subscription.isnot(None)).all()
for user in users:
    # Send to each user
```

### From Web Interface
Visit `/notify` (requires login) to send test notification

---

## 🔧 Debug Commands

### Check Installation
```javascript
// In browser console
navigator.serviceWorker.getRegistrations().then(r => 
    console.log('✅ Service Worker:', r[0]?.active?.state)
);
```

### View Cached Files
```javascript
caches.keys().then(names => names.forEach(name => {
    caches.open(name).then(c => 
        c.keys().then(reqs => console.log(`${name}: ${reqs.length} files`))
    );
}));
```

### Force Update
```javascript
navigator.serviceWorker.ready.then(r => r.update());
// Or hard refresh: Ctrl+Shift+R
```

### Check Push Permission
```javascript
console.log('Permission:', Notification.permission);
// Output: "granted", "denied", or "default"
```

---

## 🎯 Key Files Modified

| File | Purpose |
|------|---------|
| `static/manifest.json` | PWA metadata |
| `static/service-worker.js` | Network/cache handler |
| `static/js/pwa-manager.js` | Installation manager |
| `templates/base.html` | PWA meta tags |
| `templates/offline.html` | Offline page |
| `app.py` | PWA endpoints |

---

## 📊 Monitor Installation

### View in Database
```sql
SELECT username, push_subscription IS NOT NULL as has_subscription
FROM user
WHERE push_subscription IS NOT NULL
ORDER BY created_at DESC;
```

### Check Server Logs
```
✅ Service Worker registered successfully
🔔 Setting up push notifications...
📱 PWA installed by [username]
✅ User [username] subscribed to push notifications
✅ Push notification sent: [title]
```

---

## ⚙️ Common Configurations

### Change App Colors
Edit `manifest.json`:
```json
"theme_color": "#1a1a2e",
"background_color": "#ffffff"
```

And `base.html`:
```html
<meta name="theme-color" content="#1a1a2e">
```

### Add App Shortcuts
Edit `manifest.json` shortcuts array:
```json
"shortcuts": [
    {
        "name": "Read Poetry",
        "url": "/categories"
    }
]
```

### Disable Installation Prompt
In `pwa-manager.js`, comment out `showInstallPrompt()` call

### Change Cache Strategy
Edit `service-worker.js` fetch event handler

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Install button missing | Check HTTPS, manifest.json, icons |
| Push not working | Check VAPID keys, permissions, subscription |
| Offline page broken | Check route exists, template renders |
| Service worker not updating | Hard refresh, check cache names |
| Icons not showing | Verify paths, check file exists |
| Permission prompt missing | Check browser settings, permissions already set |

---

## 🔐 Security Checklist

- [ ] VAPID keys in `.env` (not in code)
- [ ] HTTPS enabled in production
- [ ] `push_subscription` only saved for authenticated users
- [ ] Notification payload doesn't contain sensitive data
- [ ] Regular VAPID key rotation schedule
- [ ] Monitor for failed push attempts (subscription expired)

---

## 📋 Deployment Checklist

- [ ] `.env` has VAPID keys
- [ ] `manifest.json` is valid (test with json.org)
- [ ] Icons exist and are accessible
- [ ] `offline.html` renders correctly
- [ ] Service worker registration not blocked by CSP
- [ ] Database migration for push_subscription column run
- [ ] Test push notification sent successfully
- [ ] iOS "Add to Home Screen" works
- [ ] Android install prompt shows
- [ ] HTTPS certificate valid
- [ ] Analytics tracking in place

---

## 📞 Quick Support

**PWA Won't Install:**
1. Check HTTPS (required except localhost)
2. Verify manifest.json in DevTools under Application
3. Check icons are 192x192 & 512x512
4. Wait a few seconds, reload page

**Push Not Received:**
1. Check notification permission granted
2. Verify subscription in database
3. Check VAPID keys in .env
4. Test with `/notify` endpoint

**App Won't Go Offline:**
1. Verify service worker active
2. Check cache creation in DevTools
3. Test with network tab offline
4. Clear cache and reinstall app

---

## 🎓 Learn More

- [Google PWA Guide](https://developers.google.com/web/progressive-web-apps)
- [MDN PWA Checklist](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [Service Worker API Docs](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)

---

**Version:** 1.0  
**Last Updated:** March 8, 2026
