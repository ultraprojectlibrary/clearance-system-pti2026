/* PTI Clearance — sidebar controller */
(function () {
  'use strict';

  var wrapper  = null;
  var sidebar  = null;
  var backdrop = null;

  function isMobile() { return window.innerWidth <= 991; }

  function openMobileSidebar() {
    if (!wrapper) return;
    wrapper.classList.add('close_icon');
    if (backdrop) backdrop.classList.add('show');
    document.body.style.overflow = 'hidden';
  }

  function closeMobileSidebar() {
    if (!wrapper) return;
    wrapper.classList.remove('close_icon');
    if (backdrop) backdrop.classList.remove('show');
    document.body.style.overflow = '';
  }

  function init() {
    wrapper  = document.getElementById('pageWrapper');
    sidebar  = document.querySelector('.page-sidebar');

    /* inject mobile backdrop */
    backdrop = document.createElement('div');
    backdrop.className = 'sidebar-backdrop';
    document.body.appendChild(backdrop);

    /* backdrop click closes sidebar on mobile */
    backdrop.addEventListener('click', closeMobileSidebar);

    /* close on resize from mobile -> desktop */
    window.addEventListener('resize', function () {
      if (!isMobile()) closeMobileSidebar();
    });

    /* active nav link */
    var links = document.querySelectorAll('.sidebar-link');
    links.forEach(function (link) {
      var href = link.getAttribute('href');
      if (href && href !== '#' && href.indexOf('javascript') === -1) {
        if (window.location.pathname === href || window.location.href === href) {
          link.classList.add('active');
          var li = link.closest('.sidebar-list');
          if (li) li.classList.add('active');
        }
      }
    });

    /* profile dropdown */
    var profileNav = document.querySelector('.profile-nav.custom-dropdown');
    if (profileNav) {
      var userWrap = profileNav.querySelector('.user-wrap');
      var menu     = profileNav.querySelector('.custom-menu');
      if (userWrap && menu) {
        userWrap.addEventListener('click', function (e) {
          e.stopPropagation();
          menu.classList.toggle('show');
        });
        document.addEventListener('click', function () {
          menu.classList.remove('show');
        });
      }
    }

    /* fullscreen */
    var fsBtn = document.querySelector('.full-screen');
    if (fsBtn) {
      fsBtn.addEventListener('click', function (e) {
        e.preventDefault();
        if (!document.fullscreenElement) {
          document.documentElement.requestFullscreen && document.documentElement.requestFullscreen();
        } else {
          document.exitFullscreen && document.exitFullscreen();
        }
      });
    }
  }

  /* ── Hamburger: event delegation on document ─────────────────
     Using delegation means we never have to find the button at
     init-time, and it works regardless of what else the page renders.
  ──────────────────────────────────────────────────────────────── */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.hamburger-btn');
    if (!btn) return;
    e.preventDefault();
    if (!wrapper) wrapper = document.getElementById('pageWrapper');
    if (!wrapper) return;
    if (isMobile()) {
      wrapper.classList.contains('close_icon') ? closeMobileSidebar() : openMobileSidebar();
    } else {
      wrapper.classList.toggle('close_icon');
    }
  });

  /* Run init after DOM is ready */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
