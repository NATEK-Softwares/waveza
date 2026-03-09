# WaveZA PWA Implementation Guide

## Overview

This document outlines the Progressive Web App (PWA) implementation for WaveZA, enabling the app to be installed on mobile and desktop devices with native-like experience, including push notifications, offline support, and background sync.

## ✨ Features Implemented

### 1. **PWA Installation**
- **Installable on iOS** (requires iOS 16.4+)
  - Add to Home Screen functionality via Web App Manifest
  - Native app appearance with splash screens
  - Status bar styling
  
- **Installable on Android**
  - Native install prompts
  - Home screen shortcuts
  - App drawer presence
  
- **Installable on Desktop** (Chrome, Edge, Firefox)
  - "Install" button in address bar
  - Start menu/desktop shortcuts
  - Standalone window mode

### 2. **Push Notifications**
- Background push delivery
- User subscription management
- Rich notifications with images and actions
- Notification click handling with deep linking
- Vibration feedback (on supported devices)

### 3. **Offline Support**
- Service Worker caching strategy
- Offline fallback page
- Network-first for HTML
- Cache-first for static assets
- Intelligent image caching

### 4. **Advanced Features**
- Background sync (for future offline post queuing)
- Periodic sync (for checking new notifications)
- App update detection and prompts
- Installation tracking

---

## 🔧 Setup Instructions

### Step 1: Generate VAPID Keys

VAPID keys are required for push notifications. Generate them using web-push package:

```bash
npm install -g web-push
web-push generate-vapid-keys
```

This will output:
```
Public Key: [base64-string]
Private Key: [base64-string]
```

### Step 2: Configure Environment Variables

Add to your `.env` file:

```env
# VAPID Keys for Push Notifications
VAPID_PUBLIC_KEY=your_public_key_here
VAPID_PRIVATE_KEY=your_private_key_here
VAPID_EMAIL=your_email@example.com

# Example:
VAPID_PUBLIC_KEY=BCdRj1CvyIzXn3I356t7oZGpGalj5CqemFYCSds6DyOR8BHW3uy-yUcvnTaE6NQkCDSPZFMlzvtWKcj6k7LQO5g
VAPID_PRIVATE_KEY=4yGY_ZSv-sWLFCbzm3tSZkSsi_tLtMQVVQK50bruqSM
VAPID_EMAIL=hello@waveza.co.za
```

### Step 3: Verify Installation

Restart your Flask app:

```bash
python app.py
```

Check the console for:
```
✅ Service Worker registered successfully
🔔 Setting up push notifications...
```

### Step 4: Test PWA Installation

#### On Android/Chrome:
1. Open https://your-domain.com
2. Click the "Install" button in the address bar
3. Select "Install" in the prompt
4. App will be added to your home screen

#### On iOS (16.4+):
1. Open https://your-domain.com in Safari
2. Tap Share → Add to Home Screen
3. Name your app and tap Add
4. Open the app from home screen

#### On Desktop:
1. Open Chrome/Edge
2. Click "Install" button in address bar
3. App opens in standalone window
4. Accessible from Start Menu or Applications

---

## 📱 Key Files

### 1. **manifest.json** (`/static/manifest.json`)
- PWA metadata and branding
- App icons and screenshots
- Start URL and display mode
- Theme colors
- Shortcuts and share target

### 2. **service-worker.js** (`/static/service-worker.js`)
- Network request interception
- Cache management (3 strategies)
- Push event handling
- Offline fallback
- Background sync hooks
- Periodic sync hooks

### 3. **pwa-manager.js** (`/static/js/pwa-manager.js`)
- Service Worker registration
- Push notification setup
- Install prompt handling
- Update notification display
- VAPID key conversion
- Permission requests

### 4. **offline.html** (`/templates/offline.html`)
- Beautiful offline fallback page
- Instructions for users
- Styling and animations
- Automatic reconnection detection

### 5. **base.html** Updates
- PWA meta tags (theme-color, apple-mobile-web-app-capable, etc.)
- Manifest link
- Apple touch icons
- Preconnect directives

### 6. **app.py** Updates
- `/api/vapid-public-key` - Get VAPID public key for client
- `/subscribe` - Save push subscription
- `/notify` - Send test notification
- `/offline` - Offline page
- `/api/notifications` - Get user notifications
- `/api/track-install` - Track PWA installations

---

## 🔔 Push Notification Usage

### Sending Notifications to a User

```python
from app import send_push_notification

# Get user
user = User.query.filter_by(username='john').first()

if user and user.push_subscription:
    subscription_info = json.loads(user.push_subscription)
    
    send_push_notification(
        subscription_info=subscription_info,
        message_title="New Poem Published! 📝",
        message_body="Check out 'Midnight Dreams' by Sarah",
        image_url="/static/img/poems/midnight.jpg",
        action_url="/poem/123/midnight-dreams"
    )
```

### Broadcasting Notifications to Multiple Users

```python
# Notify all users interested in a category
interested_users = User.query.filter(
    User.preferred_categories.contains('romance')
).filter(User.push_subscription.isnot(None)).all()

for user in interested_users:
    subscription_info = json.loads(user.push_subscription)
    send_push_notification(
        subscription_info=subscription_info,
        message_title="New Romance Poetry 💕",
        message_body="New poems in your favorite category",
        action_url="/category/romance"
    )
```

### Notification Actions

Users will see "Open" and "Dismiss" buttons in the notification. Customize by editing the service worker:

```javascript
// In service-worker.js, modifyactions array:
actions: [
    { action: 'open', title: 'Open' },
    { action: 'close', title: 'Dismiss' },
    { action: 'reply', title: 'Reply' }  // Can add more
]
```

---

## 🎨 Caching Strategy

The service worker implements three caching strategies:

### 1. **Cache-First** (Static Assets)
- Used for: CSS, JavaScript, Images
- Falls back to: Network if cache miss
- Best for: Rarely-changing assets

### 2. **Network-First** (HTML Pages & APIs)
- Used for: HTML documents, API calls
- Falls back to: Cache if network fails
- Offline fallback: Shows offline.html

### 3. **Stale-While-Revalidate** (Images)
- Used for: Poem images, user avatars
- Returns: Cached version immediately
- Updates: Cache in background

---

## 🔐 Security Considerations

### VAPID Keys
- **Never commit** VAPID keys to git
- Always use `.env` for secrets
- Regenerate keys if compromised
- Store safely in production

### Push Subscriptions
- Validate subscriptions before storing
- Clean up expired subscriptions
- Only send to authenticated users
- Log suspicious subscription attempts

### Service Worker
- No access to sensitive user data
- All operations are anonymous
- Cannot access private cookies (HttpOnly)
- Cannot make authenticated requests

---

## 📊 Testing & Debugging

### Check Service Worker Status
```javascript
// In browser console
navigator.serviceWorker.getRegistrations().then(regs => {
    regs.forEach(reg => {
        console.log('SW State:', reg.active.state);
        console.log('Scope:', reg.scope);
    });
});
```

### Test Push Notifications
1. Go to `/notify` endpoint (requires login)
2. Check browser notification
3. Click notification to test deep linking

### Check Cache Contents
```javascript
// In browser console
caches.keys().then(names => {
    names.forEach(name => {
        caches.open(name).then(cache => {
            cache.keys().then(reqs => {
                console.log(`Cache: ${name}`);
                reqs.forEach(req => console.log(`  - ${req.url}`));
            });
        });
    });
});
```

### View Registered Shortcuts
```javascript
// In browser console
if ('shortcuts' in navigator) {
    console.log('PWA Shortcuts:', navigator.shortcuts);
}
```

### Monitor Service Worker Updates
```javascript
// Built into pwa-manager.js, checks every 60 seconds
// Manual check:
navigator.serviceWorker.ready.then(reg => {
    reg.update();
});
```

---

## 📱 iOS-Specific Notes

### Supported Features
✅ Installation via "Add to Home Screen"
✅ App icon and splash screen
✅ Standalone display mode
✅ Status bar styling
✅ Theme color

### Limited Features (iOS Limitations)
❌ Push notifications (Apple doesn't support Web Push on PWAs)
❌ Background sync
❌ Periodic sync
❌ Service worker persistence (clears cache on app update)

### iOS Optimization
```html
<!-- Already in base.html -->
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="apple-touch-icon" href="/static/img/NEW/icons/android-chrome-512x512.png">
```

---

## 🔄 Update Strategy

### Auto-Update Detection
- Service Worker checks every 60 seconds
- Shows banner when update available
- User can click "Update Now" to reload

### Clean Installation
1. User installs PWA
2. Tracked via `/api/track-install`
3. Base cache created on first install
4. Updates shown on subsequent visits

---

## 📈 Monitoring & Analytics

### Track Installations
Check logs for:
```
📱 PWA installed by [username]
📱 PWA installed by anonymous user
```

### Monitor Push Delivery
```python
# In app.py logs
✅ Push notification sent: [title]
❌ Web push failed: [error details]
```

### Check Subscription Status
```sql
-- Query database
SELECT username, push_subscription FROM user 
WHERE push_subscription IS NOT NULL;
```

---

## 🐛 Troubleshooting

### "Install button not appearing"
- Check: Site must be HTTPS (except localhost)
- Check: manifest.json is valid JSON
- Check: Icons exist and are accessible
- Check: Service Worker registers successfully

### "Push notifications not working"
- Verify VAPID_PRIVATE_KEY is set in .env
- Check user has granted notification permission
- Verify subscription is saved in database
- Test with `/notify` endpoint

### "App won't go offline"
- Check service worker installation
- Verify cache names match
- Check browser cache is not full
- Test in incognito window

### "Updates not showing"
- Manual update: `navigator.serviceWorker.ready.then(r => r.update())`
- Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
- Clear service worker: DevTools > Application > Clear storage

---

## 🚀 Production Deployment

### Pre-Deployment Checklist
- [ ] HTTPS enabled
- [ ] VAPID keys set in production .env
- [ ] manifest.json valid and accessible
- [ ] Service Worker caching tested
- [ ] Icons uploaded and accessible
- [ ] offline.html rendering correctly
- [ ] Database migrations run
- [ ] Push subscription table has adequate space

### Production Monitoring
```python
# Log service worker registration errors
# Log push notification failures
# Monitor subscription count growth
# Track offline usage patterns
```

---

## 📚 Browser Support

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| PWA Installation | ✅ | ✅ | ⚠️ iOS 16.4+ | ✅ |
| Service Worker | ✅ | ✅ | ✅ | ✅ |
| Push Notifications | ✅ | ✅ | ❌ | ✅ |
| Offline Support | ✅ | ✅ | ✅ | ✅ |
| Background Sync | ✅ | ❌ | ❌ | ✅ |
| Periodic Sync | ✅ | ❌ | ❌ | ✅ |

---

## 📞 Support & Resources

- [MDN Web Docs - PWA](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [Web Push Protocol](https://datatracker.ietf.org/doc/html/draft-thomson-webpush-protocol)
- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Web App Manifest](https://www.w3.org/TR/appmanifest/)

---

## Version History

- **v1.0** - Initial PWA implementation
  - Service Worker with intelligent caching
  - Push notification support
  - Offline fallback page
  - Installation tracking
  - Update detection

---

**Last Updated:** March 8, 2026  
**Maintainer:** NATEK Softwares  
**Status:** Production Ready
