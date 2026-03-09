import axios from 'axios';

// Detect if running in a native app (Capacitor/Tauri)
export const isNativeApp = (): boolean => {
  return !!(window as any).Capacitor || !!(window as any).__TAURI__;
};

// Get the appropriate API base URL
export const getApiBaseUrl = (): string => {
  if (isNativeApp()) {
    // In native apps, connect to local bundled backend
    return 'http://localhost:5000';
  } else {
    // In web browsers, use the current origin or configured API URL
    return process.env.REACT_APP_API_URL || 'http://localhost:5000';
  }
};

// Configure axios with the correct base URL
axios.defaults.baseURL = getApiBaseUrl();
axios.defaults.withCredentials = true;

// Export configured axios instance
export default axios;