const CACHE_VERSION = 'waveza-v1';
const RUNTIME_CACHE = 'waveza-runtime-v1';
const IMAGE_CACHE = 'waveza-images-v1';
const OFFLINE_URL = '/offline';

// Files to cache on install
const PRECACHE_URLS = [
    '/',
    '/offline',
    '/static/css/style.css',
    '/static/css/auth.css',
    '/static/css/modern.css',
    '/static/css/modern-components.css',
    '/static/js/main.js',
    '/static/lib/animate/animate.min.css',
    '/static/lib/owlcarousel/assets/owl.carousel.min.css',
    '/static/img/NEW/icons/android-chrome-512x512.png',
    '/static/manifest.json'
];

// Install event - cache critical files
self.addEventListener('install', event => {
    console.log('Service Worker installing...');
    event.waitUntil(
        caches.open(CACHE_VERSION)
            .then(cache => {
                console.log('Caching critical files');
                return cache.addAll(PRECACHE_URLS);
            })
            .then(() => self.skipWaiting())
            .catch(err => console.error('Install error:', err))
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('Service Worker activating...');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_VERSION && 
                        cacheName !== RUNTIME_CACHE && 
                        cacheName !== IMAGE_CACHE) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch event - intelligent caching strategy
self.addEventListener('fetch', event => {
    const url = new URL(event.request.url);
    
    // Skip cross-origin requests
    if (url.origin !== location.origin) {
        return;
    }
    
    // Handle API requests
    if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/subscribe') || url.pathname.startsWith('/notify')) {
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    if (response && response.status === 200) {
                        const clonedResponse = response.clone();
                        caches.open(RUNTIME_CACHE).then(cache => {
                            cache.put(event.request, clonedResponse);
                        });
                    }
                    return response;
                })
                .catch(() => caches.match(event.request))
        );
        return;
    }
    
    // Handle image requests - cache-first strategy
    if (event.request.destination === 'image') {
        event.respondWith(
            caches.match(event.request)
                .then(response => {
                    if (response) {
                        return response;
                    }
                    return fetch(event.request).then(response => {
                        if (!response || response.status !== 200 || response.type === 'error') {
                            return response;
                        }
                        const clonedResponse = response.clone();
                        caches.open(IMAGE_CACHE).then(cache => {
                            cache.put(event.request, clonedResponse);
                        });
                        return response;
                    });
                })
                .catch(() => {
                    // Return a placeholder if image fails to load
                    return caches.match('/static/img/NEW/icons/android-chrome-512x512.png');
                })
        );
        return;
    }
    
    // Handle stylesheet and script requests - cache-first
    if (event.request.destination === 'style' || event.request.destination === 'script') {
        event.respondWith(
            caches.match(event.request)
                .then(response => {
                    return response || fetch(event.request).then(response => {
                        if (!response || response.status !== 200) {
                            return response;
                        }
                        const clonedResponse = response.clone();
                        caches.open(RUNTIME_CACHE).then(cache => {
                            cache.put(event.request, clonedResponse);
                        });
                        return response;
                    });
                })
                .catch(() => {
                    console.error('Failed to fetch resource:', event.request.url);
                })
        );
        return;
    }
    
    // Default strategy: network-first for HTML documents
    event.respondWith(
        fetch(event.request)
            .then(response => {
                if (!response || response.status !== 200 || response.type === 'error') {
                    return response;
                }
                const clonedResponse = response.clone();
                caches.open(RUNTIME_CACHE).then(cache => {
                    cache.put(event.request, clonedResponse);
                });
                return response;
            })
            .catch(() => {
                // Return cached version or offline page
                return caches.match(event.request)
                    .then(response => response || caches.match(OFFLINE_URL));
            })
    );
});

// Push notification event
self.addEventListener('push', event => {
    console.log('Push notification received:', event);
    
    let data = {};
    if (event.data) {
        try {
            data = event.data.json();
        } catch (e) {
            data = {
                title: 'WaveZA Notification',
                body: event.data.text()
            };
        }
    }
    
    const options = {
        body: data.body || 'You have a new notification from WaveZA',
        icon: '/static/img/NEW/icons/android-chrome-512x512.png',
        badge: '/static/img/NEW/icons/android-chrome-512x512.png',
        tag: data.tag || 'notification',
        requireInteraction: false,
        data: {
            url: data.url || '/',
            timestamp: Date.now()
        },
        actions: [
            {
                action: 'open',
                title: 'Open'
            },
            {
                action: 'close',
                title: 'Dismiss'
            }
        ]
    };
    
    // Add vibration pattern if available
    if ('vibrate' in options) {
        options.vibrate = [200, 100, 200];
    }
    
    event.waitUntil(
        self.registration.showNotification(data.title || 'WaveZA', options)
    );
});

// Notification click event
self.addEventListener('notificationclick', event => {
    console.log('Notification clicked:', event);
    event.notification.close();
    
    if (event.action === 'close') {
        return;
    }
    
    const urlToOpen = event.notification.data.url || '/';
    
    event.waitUntil(
        clients.matchAll({
            type: 'window',
            includeUncontrolled: true
        }).then(clientList => {
            // Check if app is already open
            for (let client of clientList) {
                if (client.url === urlToOpen && 'focus' in client) {
                    return client.focus();
                }
            }
            // If not open, open new window
            if (clients.openWindow) {
                return clients.openWindow(urlToOpen);
            }
        })
    );
});

// Notification close event
self.addEventListener('notificationclose', event => {
    console.log('Notification closed');
});

// Background sync (for future use - syncing data when back online)
self.addEventListener('sync', event => {
    console.log('Background sync triggered:', event.tag);
    if (event.tag === 'sync-poems') {
        event.waitUntil(
            fetch('/api/sync')
                .then(response => response.json())
                .catch(err => console.error('Sync error:', err))
        );
    }
});

// Periodic sync (for checking new notifications - requires permission)
self.addEventListener('periodicsync', event => {
    console.log('Periodic sync triggered:', event.tag);
    if (event.tag === 'check-notifications') {
        event.waitUntil(
            fetch('/api/notifications')
                .then(response => response.json())
                .then(data => {
                    if (data.new_notifications && data.new_notifications.length > 0) {
                        // Show notification for new activity
                        let notification = data.new_notifications[0];
                        self.registration.showNotification(notification.title, {
                            body: notification.body,
                            icon: '/static/img/NEW/icons/android-chrome-512x512.png',
                            tag: 'activity-notification'
                        });
                    }
                })
                .catch(err => console.error('Periodic sync error:', err))
        );
    }
});
