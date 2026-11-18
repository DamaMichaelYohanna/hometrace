/**
 * Hometrace Main Application Client JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Menu Drawer Toggle
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const mobileMenuDrawer = document.getElementById('mobile-menu-drawer');
  if (mobileMenuBtn && mobileMenuDrawer) {
    mobileMenuBtn.addEventListener('click', () => {
      mobileMenuDrawer.classList.toggle('hidden');
    });
  }

  // 2. User Dropdown Toggle
  const userMenuBtn = document.getElementById('user-menu-btn');
  const userMenuDropdown = document.getElementById('user-menu-dropdown');
  if (userMenuBtn && userMenuDropdown) {
    userMenuBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      userMenuDropdown.classList.toggle('hidden');
    });
    document.addEventListener('click', (e) => {
      if (!userMenuDropdown.contains(e.target) && !userMenuBtn.contains(e.target)) {
        userMenuDropdown.classList.add('hidden');
      }
    });
  }

  // 3. Password Visibility Toggle
  document.querySelectorAll('.password-toggle-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-target');
      const input = document.getElementById(targetId);
      if (input) {
        const isPassword = input.getAttribute('type') === 'password';
        input.setAttribute('type', isPassword ? 'text' : 'password');
        btn.innerHTML = isPassword ? `
          <svg class="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18"/></svg>
        ` : `
          <svg class="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
        `;
      }
    });
  });

  // 4. AJAX Favorite Toggle Handlers
  document.querySelectorAll('.favorite-toggle-btn').forEach(button => {
    button.addEventListener('click', async (e) => {
      e.preventDefault();
      e.stopPropagation();

      const propertyId = button.getAttribute('data-property-id');
      if (!propertyId) return;

      try {
        const response = await fetch(`/favorites/toggle/${propertyId}/?format=json`, {
          method: 'GET',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json',
          }
        });

        if (response.redirected) {
          window.location.href = response.url;
          return;
        }

        const data = await response.json();
        const icon = button.querySelector('.fav-icon');

        if (data.saved) {
          button.classList.add('text-rose-500', 'bg-rose-50');
          button.classList.remove('text-slate-400');
          if (icon) icon.setAttribute('fill', 'currentColor');
          showToast(data.message, 'success');
        } else {
          button.classList.remove('text-rose-500', 'bg-rose-50');
          button.classList.add('text-slate-400');
          if (icon) icon.setAttribute('fill', 'none');
          showToast(data.message, 'info');
        }

        // Update badge counts in nav
        const badges = document.querySelectorAll('.favorites-count-badge');
        badges.forEach(b => {
          b.textContent = data.total_favorites;
          b.classList.toggle('hidden', data.total_favorites === 0);
        });
      } catch (err) {
        console.error('Error toggling favorite:', err);
      }
    });
  });

  // 5. Purpose selector dependency for rental frequency
  const purposeSelector = document.getElementById('purpose-selector');
  const frequencyGroup = document.getElementById('rental-frequency-group');
  if (purposeSelector && frequencyGroup) {
    const updateFrequencyVisibility = () => {
      if (purposeSelector.value === 'for_rent') {
        frequencyGroup.classList.remove('hidden');
      } else {
        frequencyGroup.classList.add('hidden');
      }
    };
    purposeSelector.addEventListener('change', updateFrequencyVisibility);
    updateFrequencyVisibility();
  }

  // 6. Role selector change helper in Registration
  const roleSelector = document.getElementById('role-selector');
  const agencyGroup = document.getElementById('agency-name-group');
  if (roleSelector && agencyGroup) {
    const updateAgencyVisibility = () => {
      if (roleSelector.value === 'agent') {
        agencyGroup.classList.remove('hidden');
      } else {
        agencyGroup.classList.add('hidden');
      }
    };
    roleSelector.addEventListener('change', updateAgencyVisibility);
    updateAgencyVisibility();
  }

  // 7. Toast helper function
  window.showToast = function(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'fixed bottom-5 right-5 z-50 flex flex-col space-y-3 pointer-events-none';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    const colorClasses = type === 'success' 
      ? 'bg-emerald-600 text-white' 
      : type === 'error' 
      ? 'bg-rose-600 text-white' 
      : 'bg-slate-900 text-white';

    toast.className = `${colorClasses} pointer-events-auto px-5 py-3 rounded-xl shadow-lg flex items-center space-x-3 text-sm font-medium transition-all duration-300 transform translate-y-3 opacity-0`;
    toast.innerHTML = `
      <span>${message}</span>
    `;

    container.appendChild(toast);
    requestAnimationFrame(() => {
      toast.classList.remove('translate-y-3', 'opacity-0');
    });

    setTimeout(() => {
      toast.classList.add('opacity-0', 'translate-y-2');
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  };
});
