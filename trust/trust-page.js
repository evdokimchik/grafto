(function () {
  const LANG_KEY = 'grafto_lang';
  const LANG_MANUAL_KEY = 'grafto_lang_manual';

  function browserLang() {
    const langs = navigator.languages && navigator.languages.length
      ? navigator.languages
      : [navigator.language || 'en'];
    try {
      const intlLocale = Intl.DateTimeFormat().resolvedOptions().locale;
      if (intlLocale) langs.push(intlLocale);
    } catch (e) {}
    return langs.some(l => /^(ru|be|uk|kk|ky)/i.test(l || '')) ? 'ru' : 'en';
  }

  function detectLang() {
    const params = new URLSearchParams(window.location.search);
    const urlLang = params.get('lang');
    if (urlLang === 'ru' || urlLang === 'en') return urlLang;
    return browserLang();
  }

  function setLang(lang) {
    document.documentElement.lang = lang;
    document.querySelectorAll('[data-lang]').forEach(el => {
      el.style.display = el.getAttribute('data-lang') === lang ? '' : 'none';
    });
    document.querySelectorAll('[data-lang-switch]').forEach(el => {
      el.classList.toggle('active', el.getAttribute('data-lang-switch') === lang);
    });
  }

  const lang = detectLang();
  setLang(lang);
  document.querySelectorAll('[data-lang-switch]').forEach(link => {
    link.addEventListener('click', () => {
      const next = link.getAttribute('data-lang-switch');
      try {
        localStorage.setItem(LANG_KEY, next);
        localStorage.setItem(LANG_MANUAL_KEY, '1');
      } catch (e) {}
    });
  });
})();
