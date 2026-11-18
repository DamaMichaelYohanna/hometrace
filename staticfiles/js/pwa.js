/**
 * Progressive Web Application (PWA) Manager for Hometrace
 */

let deferredInstallPrompt = null;

// 1. Register Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/sw.js')
      .then((reg) => {
        console.log('[Hometrace PWA] Service Worker registered with scope:', reg.scope);
      })
      .catch((err) => {
        console.error('[Hometrace PWA] Service Worker registration failed:', err);
      });
  });
}

// 2. Intercept BeforeInstallPrompt for custom install experience
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredInstallPrompt = e;
  console.log('[Hometrace PWA] App install prompt captured');

  // Show installation banner & buttons if available
  const installBanner = document.getElementById('pwa-install-banner');
  const installButtons = document.querySelectorAll('.pwa-install-trigger');

  if (installBanner) {
    installBanner.classList.remove('hidden');
    installBanner.classList.add('pwa-banner-slide');
  }

  installButtons.forEach(btn => {
    btn.classList.remove('hidden');
  });
});

// 3. Trigger installation prompt on user click
window.triggerPwaInstall = async function() {
  if (!deferredInstallPrompt) {
    if (window.showToast) {
      window.showToast('To install Hometrace: Tap browser menu (⋮ or Share) and select "Add to Home Screen".', 'info');
    }
    return;
  }

  deferredInstallPrompt.prompt();
  const choiceResult = await deferredInstallPrompt.userChoice;
  console.log('[Hometrace PWA] User install choice:', choiceResult.outcome);

  if (choiceResult.outcome === 'accepted') {
    const banner = document.getElementById('pwa-install-banner');
    if (banner) banner.remove();
  }
  deferredInstallPrompt = null;
};

// 4. Handle successful installation
window.addEventListener('appinstalled', () => {
  console.log('[Hometrace PWA] App successfully installed on device');
  const banner = document.getElementById('pwa-install-banner');
  if (banner) banner.remove();
  if (window.showToast) {
    window.showToast('Hometrace has been successfully installed!', 'success');
  }
});

// 5. Network Connectivity Listeners
window.addEventListener('offline', () => {
  if (window.showToast) {
    window.showToast('You are currently offline. Viewing cached resources.', 'error');
  }
  const offlineIndicator = document.getElementById('offline-indicator');
  if (offlineIndicator) offlineIndicator.classList.remove('hidden');
});

window.addEventListener('online', () => {
  if (window.showToast) {
    window.showToast('Internet connection restored.', 'success');
  }
  const offlineIndicator = document.getElementById('offline-indicator');
  if (offlineIndicator) offlineIndicator.classList.add('hidden');
});
