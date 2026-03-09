/**
 * WaveZA PWA Manager
 * Handles service worker registration, push notifications, and PWA installation
 */

// Initialize PWA on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPWA);
} else {
    initPWA();
}

async function initPWA() {
    console.log('🌊 WaveZA PWA Manager initializing...');
    
    // Register service worker
    if ('serviceWorker' in navigator) {
        try {
            const registration = await navigator.serviceWorker.register('/static/service-worker.js', {
                scope: '/',
                updateViaCache: 'none'
            });
            console.log('✅ Service Worker registered successfully');
            
            // Check for updates periodically
            setInterval(() => {
                registration.update();
            }, 60000); // Check every 60 seconds
            
            // Listen for new service worker
            registration.addEventListener('updatefound', () => {
                const newWorker = registration.installing;
                if (newWorker) {
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            showUpdateNotification();
                        }
                    });
                }
            });
            
            // Setup push notifications
            if ('PushManager' in window) {
                setupPushNotifications(registration);
            }
        } catch (error) {
            console.error('❌ Service Worker registration failed:', error);
        }
    } else {
        console.warn('⚠️ Service Workers not supported in this browser');
    }
    
    // Handle install prompt
    setupInstallPrompt();
    
    // Setup notification permission button
    setupNotificationPrompt();
}

/**
 * Setup service worker update notification
 */
function showUpdateNotification() {
    console.log('📦 New app version available');
    
    const updateBanner = document.createElement('div');
    updateBanner.id = 'pwa-update-banner';
    updateBanner.innerHTML = `
        <style>
            #pwa-update-banner {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 16px 20px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                z-index: 9999;
                display: flex;
                align-items: center;
                gap: 12px;
                animation: slideInUp 0.3s ease-out;
                max-width: 300px;
            }
            
            @keyframes slideInUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            #pwa-update-banner button {
                background: white;
                color: #667eea;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                cursor: pointer;
                font-weight: 600;
                font-size: 12px;
                transition: all 0.2s ease;
            }
            
            #pwa-update-banner button:hover {
                transform: scale(1.05);
            }
            
            #pwa-update-banner .close-btn {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                padding: 4px 8px;
                font-size: 18px;
                cursor: pointer;
                border: none;
                margin-left: auto;
            }
            
            @media (max-width: 600px) {
                #pwa-update-banner {
                    right: 10px;
                    left: 10px;
                    max-width: none;
                }
            }
        </style>
        <div style="flex: 1;">
            <strong>✨ New version available!</strong>
            <p style="margin: 4px 0 0 0; font-size: 12px; opacity: 0.9;">Update to get the latest features and improvements.</p>
        </div>
        <button onclick="location.reload()">Update Now</button>
        <button class="close-btn" onclick="this.parentElement.remove()">×</button>
    `;
    document.body.appendChild(updateBanner);
}

/**
 * Setup PWA installation prompt
 */
let deferredPrompt = null;

window.addEventListener('beforeinstallprompt', (e) => {
    console.log('📲 Install prompt available');
    e.preventDefault();
    deferredPrompt = e;
    
    // Show install button/prompt
    showInstallPrompt();
});

window.addEventListener('appinstalled', () => {
    console.log('✅ App installed successfully');
    deferredPrompt = null;
    
    // Track installation
    if ('navigator' in window && 'sendBeacon' in navigator) {
        navigator.sendBeacon('/api/track-install', JSON.stringify({ installed: true }));
    }
});

function showInstallPrompt() {
    // Create install banner
    const installBanner = document.createElement('div');
    installBanner.id = 'pwa-install-banner';
    installBanner.innerHTML = `
        <style>
            #pwa-install-banner {
                position: fixed;
                bottom: 20px;
                left: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 16px 20px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                z-index: 9999;
                display: flex;
                align-items: center;
                gap: 12px;
                animation: slideInUp 0.3s ease-out;
                max-width: 300px;
            }
            
            @keyframes slideInUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            #pwa-install-banner button {
                background: white;
                color: #667eea;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                cursor: pointer;
                font-weight: 600;
                font-size: 12px;
                transition: all 0.2s ease;
            }
            
            #pwa-install-banner button:hover {
                transform: scale(1.05);
            }
            
            #pwa-install-banner .close-btn {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                padding: 4px 8px;
                font-size: 18px;
                cursor: pointer;
                border: none;
                margin-left: auto;
            }
            
            @media (max-width: 600px) {
                #pwa-install-banner {
                    left: 10px;
                    right: 10px;
                    max-width: none;
                    bottom: 70px;
                }
            }
        </style>
        <div style="flex: 1;">
            <strong>📱 Install WaveZA</strong>
            <p style="margin: 4px 0 0 0; font-size: 12px; opacity: 0.9;">Add our app to your home screen for quick access.</p>
        </div>
        <button id="install-btn">Install</button>
        <button class="close-btn" onclick="this.parentElement.remove()">×</button>
    `;
    
    document.body.appendChild(installBanner);
    
    // Setup install button
    document.getElementById('install-btn').addEventListener('click', async () => {
        if (deferredPrompt) {
            deferredPrompt.prompt();
            const { outcome } = await deferredPrompt.userChoice;
            console.log(`User response to install prompt: ${outcome}`);
            deferredPrompt = null;
            installBanner.remove();
        }
    });
}

function setupInstallPrompt() {
    // Check if app is already installed
    const isInstalled = 
        window.matchMedia('(display-mode: standalone)').matches ||
        document.referrer.includes('android-app://') ||
        navigator.standalone === true;
    
    if (isInstalled) {
        console.log('✅ App is already installed');
    }
}

/**
 * Setup push notifications
 */
async function setupPushNotifications(registration) {
    console.log('🔔 Setting up push notifications...');
    
    try {
        // Check if user already has a subscription
        const subscription = await registration.pushManager.getSubscription();
        
        if (subscription) {
            console.log('✅ User already subscribed to push notifications');
            sendSubscriptionToServer(subscription);
        } else {
            // Check notification permission
            const permission = Notification.permission;
            if (permission === 'granted') {
                subscribeToPushNotifications(registration);
            } else if (permission === 'default') {
                console.log('⏳ Waiting for notification permission...');
            }
        }
    } catch (error) {
        console.error('❌ Push notification setup error:', error);
    }
}

async function subscribeToPushNotifications(registration) {
    try {
        console.log('📡 Subscribing to push notifications...');
        
        // Get VAPID public key from server
        const response = await fetch('/api/vapid-public-key');
        const data = await response.json();
        const vapidPublicKey = data.vapidPublicKey;
        
        // Convert base64 to Uint8Array
        const convertedVapidKey = urlBase64ToUint8Array(vapidPublicKey);
        
        const subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: convertedVapidKey
        });
        
        console.log('✅ Subscribed to push notifications');
        console.log('📋 Subscription:', subscription.toJSON());
        
        // Send subscription to server
        await sendSubscriptionToServer(subscription);
    } catch (error) {
        console.error('❌ Failed to subscribe to push notifications:', error);
    }
}

async function sendSubscriptionToServer(subscription) {
    try {
        const response = await fetch('/subscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(subscription.toJSON())
        });
        
        if (response.ok) {
            console.log('✅ Subscription sent to server');
        } else {
            console.error('❌ Failed to send subscription to server:', response.statusText);
        }
    } catch (error) {
        console.error('❌ Error sending subscription to server:', error);
    }
}

/**
 * Setup notification permission button
 */
function setupNotificationPrompt() {
    // Check if we should show notification permission button
    if ('Notification' in window && Notification.permission === 'default') {
        // Find or create notification permission button
        const notificationBtn = document.querySelector('[data-pwa-notify-btn]');
        
        if (notificationBtn) {
            notificationBtn.addEventListener('click', () => {
                requestNotificationPermission();
            });
        }
    }
}

async function requestNotificationPermission() {
    try {
        const permission = await Notification.requestPermission();
        console.log('Notification permission:', permission);
        
        if (permission === 'granted' && 'serviceWorker' in navigator) {
            const registration = await navigator.serviceWorker.ready;
            subscribeToPushNotifications(registration);
        }
    } catch (error) {
        console.error('Error requesting notification permission:', error);
    }
}

/**
 * Helper function to convert VAPID key
 */
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');
    
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    
    return outputArray;
}

/**
 * Listen for online/offline events
 */
window.addEventListener('online', () => {
    console.log('🌐 Back online');
    showOnlineNotification();
});

window.addEventListener('offline', () => {
    console.log('📴 Going offline');
});

function showOnlineNotification() {
    // Optional: Show a subtle notification that we're back online
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('WaveZA', {
            body: 'You are back online!',
            icon: '/static/img/NEW/icons/android-chrome-512x512.png',
            tag: 'online-notification'
        });
    }
}

/**
 * Export for testing
 */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initPWA,
        subscribeToPushNotifications,
        requestNotificationPermission
    };
}
