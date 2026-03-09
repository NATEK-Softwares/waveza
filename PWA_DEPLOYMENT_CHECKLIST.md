# PWA Deployment Checklist

Use this checklist to ensure your WaveZA PWA is properly configured and ready for production.

---

## 🔍 Pre-Deployment Verification

### Environment & Security

- [ ] VAPID keys generated and stored in `.env`
- [ ] `VAPID_PRIVATE_KEY` NOT in version control (check `.gitignore`)
- [ ] `SECRET_KEY` is long and secure (30+ characters)
- [ ] `DEBUG=False` in production
- [ ] HTTPS certificate valid and installed
- [ ] Certificate not self-signed (for production domains)
- [ ] Domain has proper DNS A/AAAA records

### Database

- [ ] Database migrations applied
- [ ] `User` table has `push_subscription` column
- [ ] `Notification` table exists (if using notifications)
- [ ] Database backups configured
- [ ] Sufficient disk space for push subscriptions

### Application Files

- [ ] `manifest.json` valid (test at [JSON Lint](https://jsonlint.com/))
- [ ] `service-worker.js` has no syntax errors
- [ ] `pwa-manager.js` present and linked in `base.html`
- [ ] `offline.html` renders without errors
- [ ] All icons present and accessible
- [ ] Static files served correctly

### Meta Tags in base.html

- [ ] `<meta name="viewport">` present
- [ ] `<meta name="theme-color">` present  
- [ ] `<link rel="manifest">` pointing to manifest.json
- [ ] `<link rel="icon">` present
- [ ] `<link rel="apple-touch-icon">` present
- [ ] PWA meta tags added:
  - [ ] `apple-mobile-web-app-capable`
  - [ ] `apple-mobile-web-app-status-bar-style`
  - [ ] `msapplication-TileColor`

---

## 🚀 Deployment Steps

### 1. Generate VAPID Keys (If Not Done)

```bash
npm install -g web-push
web-push generate-vapid-keys
```

Output should show:
```
Public Key: BC...
Private Key: 4y...
```

### 2. Configure Environment

Edit `.env` in production:
```env
VAPID_PUBLIC_KEY=BC...
VAPID_PRIVATE_KEY=4y...
VAPID_EMAIL=your@email.com
SECRET_KEY=very_long_secure_key_min_32_chars
DEBUG=False
```

### 3. Deploy Code

```bash
git add .
git commit -m "feat: PWA implementation with push notifications"
git push origin main

# On server:
git pull origin main
python -m pip install -r requirements.txt
flask db upgrade
python app.py
```

### 4. Verify Service Worker

```bash
curl https://your-domain.com/static/service-worker.js | head -20
```

Should return JavaScript without errors.

### 5. Test Push Notifications

1. Login to app
2. Visit `https://your-domain.com/notify`
3. Should receive browser notification
4. If failed, check server logs

### 6. Test Installation

| Platform | Steps | Expected |
|----------|-------|----------|
| **Chrome** | Open app, click install icon | Install prompt appears |
| **Android (Chrome)** | Open app → Install prompt appears | App on home screen |
| **iOS (Safari)** | Open app → Share → Add to Home Screen | App on home screen |
| **Edge** | Open app → Install icon appears | App instalable |

---

## 📋 Post-Deployment Verification

### Manifest Validation

- [ ] Visit `https://your-domain.com/static/manifest.json`
- [ ] JSON displays without errors
- [ ] Contains all required fields:
  - [ ] `name`
  - [ ] `short_name`
  - [ ] `start_url`
  - [ ] `display`
  - [ ] `icons`

### Service Worker Installation

Check in browser DevTools → Application → Service Workers:

- [ ] Service Worker shows "activated and running"
- [ ] Scope is "/"
- [ ] No errors in console

```javascript
// In browser console:
navigator.serviceWorker.getRegistrations().then(r => 
    console.log('SW State:', r[0]?.active?.state)
);
// Should output: "activated"
```

### Cache Inspection

DevTools → Application → Cache Storage:

- [ ] `waveza-v1` cache exists with files
- [ ] `waveza-runtime-v1` cache exists
- [ ] `waveza-images-v1` cache exists

### Push Notification Testing

1. Login to app
2. Visit `https://your-domain.com/notify`
3. Notify endpoint returns JSON with `{success: true}`
4. Browser notification appears in 2-3 seconds
5. Clicking notification opens correct URL

Troubleshooting if it fails:
```javascript
// Check notification permission
Notification.permission  // Should be "granted"

// Check subscription exists
navigator.serviceWorker.ready.then(r =>
    r.pushManager.getSubscription().then(s => console.log(s))
);
```

### Offline Testing

1. DevTools → Network → Offline checkbox
2. Reload page
3. App still loads (from cache)
4. Navigate around app
5. All previously visited pages work
6. Images display from cache
7. Uncheck Offline
8. Page still works
9. New content loads when available

---

## 🔐 Security Verification

### VAPID Keys

- [ ] Private key NOT visible in source code
- [ ] Private key NOT in logs
- [ ] Private key NOT in git history
- [ ] .env file in .gitignore
- [ ] Private key rotated every 90 days (recommended)

### HTTPS

```bash
curl -I https://your-domain.com 
```

Should show:
```
HTTP/2 200
Strict-Transport-Security: max-age=31536000
X-Content-Type-Options: nosniff
```

### Content Security Policy

Optional but recommended:
```
Content-Security-Policy: default-src 'self'; script-src 'self' 'wasm-unsafe-eval';
```

---

## 📊 Monitoring Setup

### Application Logs

Set up monitoring for:

```
✅ Service Worker registered successfully
❌ Service Worker registration failed
✅ Push notification sent
❌ Web push failed
📱 PWA installed
```

### Database Monitoring

Create dashboard for:

```sql
-- Active push subscriptions
SELECT COUNT(*) FROM user WHERE push_subscription IS NOT NULL;

-- New installations this week
SELECT COUNT(*) FROM user 
WHERE push_subscription IS NOT NULL 
AND created_at > NOW() - INTERVAL '7 days';

-- Failed push attempts (if you add logging)
SELECT COUNT(*) FROM push_logs WHERE status = 'failed' 
AND timestamp > NOW() - INTERVAL '24 hours';
```

### Performance Monitoring

Check Lighthouse PWA score:
1. Open DevTools → Lighthouse
2. Run PWA audit
3. Score should be 85+
4. Issues listed and fixed

---

## 🧪 Testing Scenarios

### Test 1: New User Installation
- [ ] New user visits app
- [ ] Install prompt appears (may be delayed)
- [ ] User clicks install
- [ ] App appears on home screen
- [ ] Notification permission requested
- [ ] User grants permission
- [ ] Subscription saved to database

### Test 2: Existing User
- [ ] Existing user visits (already installed)
- [ ] No install prompt
- [ ] Already has notification permission
- [ ] Subscription already in database
- [ ] Can receive notifications

### Test 3: Offline Usage
- [ ] Turn offline (DevTools)
- [ ] Previously visited pages load from cache
- [ ] Images load from cache
- [ ] Styles load from cache
- [ ] Try to go to new page → offline.html shown
- [ ] Turn online
- [ ] Page loads from network
- [ ] New pages available again

### Test 4: Notification Reception
- [ ] User receives push notification
- [ ] Notification shows with icon, title, body
- [ ] Click notification opens correct URL
- [ ] Dismiss button works
- [ ] Notification closes properly

### Test 5: App Update
- [ ] Update app code
- [ ] Deploy new version
- [ ] Existing users see update banner
- [ ] User clicks "Update Now"
- [ ] App page reloads with new version
- [ ] New features available

---

## 🚨 Rollback Plan

If PWA implementation causes issues:

### Quick Disable
1. Comment out PWA script in `base.html`:
   ```html
   <!-- <script src="{{ url_for('static', filename='js/pwa-manager.js') }}"></script> -->
   ```
2. Restart app
3. Service Worker will eventually uninstall

### Full Rollback
```bash
git revert <commit-hash>
git push origin main
```

### Restore Previous Version
```bash
git checkout main~1 app.py
git checkout main~1 static/
git checkout main~1 templates/
```

---

## 📋 Final Checklist

### Before Going Live

- [ ] All tests passing locally
- [ ] No console errors in DevTools
- [ ] HTTPS working (not self-signed)
- [ ] Manifest.json valid
- [ ] Service Worker installing
- [ ] Notifications working
- [ ] Offline mode tested
- [ ] Installation tested on 2+ devices
- [ ] Icons displaying correctly
- [ ] Splash screens working
- [ ] Lighthouse PWA score 85+
- [ ] Performance acceptable
- [ ] No security warnings
- [ ] Backups created
- [ ] Monitoring set up
- [ ] Team trained on new endpoints
- [ ] Documentation updated
- [ ] Rollback plan documented

### 3 Days After Deployment

- [ ] Monitor users installing PWA
- [ ] Check push notification delivery rates
- [ ] Monitor error logs
- [ ] Get user feedback
- [ ] No reported issues
- [ ] Installation numbers growing

### 1 Week After Deployment

- [ ] Installation metrics reviewed
- [ ] Notification engagement measured
- [ ] Performance stable
- [ ] No regressions reported
- [ ] User feedback positive
- [ ] Cache hit rates checked

---

## 📞 Rollback Contacts

Keep these ready:

- **DevOps Lead:** [Name, Phone]
- **Database Admin:** [Name, Phone]
- **Security Officer:** [Name, Phone]
- **Product Manager:** [Name, Phone]

---

## ✅ Completion

Mark when you've completed each section:

- [ ] Pre-Deployment Verification
- [ ] Deployment Steps
- [ ] Post-Deployment Verification
- [ ] Security Verification
- [ ] Monitoring Setup
- [ ] Testing Scenarios
- [ ] Final Checklist

**Deployment Date:** ___________  
**Deployed By:** ___________  
**Verified By:** ___________  

---

## 📚 Related Documentation

- [PWA Setup Guide](PWA_SETUP_GUIDE.md)
- [PWA Quick Reference](PWA_QUICK_REFERENCE.md)
- [Implementation Summary](PWA_IMPLEMENTATION_SUMMARY.md)

---

**Version:** 1.0  
**Last Updated:** March 8, 2026  
**Status:** Ready for Deployment
