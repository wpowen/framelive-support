/* Local visual presentation: no storage, uploads, tracking or third-party requests. */
(() => {
  'use strict';
  const stage = document.querySelector('[data-motion-stage]');
  const toggle = document.querySelector('[data-motion-toggle]');
  if (!stage || !toggle) return;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  let requested = !reduce.matches && !(navigator.connection && navigator.connection.saveData);
  let visible = true;
  const sync = () => {
    const active = requested && visible && !document.hidden && !reduce.matches;
    stage.dataset.motion = active ? 'playing' : 'paused';
    const label = requested && !reduce.matches ? toggle.dataset.pause : toggle.dataset.play;
    toggle.setAttribute('aria-pressed', String(requested && !reduce.matches));
    toggle.setAttribute('aria-label', label);
    toggle.querySelector('[data-motion-text]').textContent = label;
    toggle.querySelector('path').setAttribute('d', requested && !reduce.matches ? 'M9 5v14M15 5v14' : 'M8 5l11 7-11 7z');
    toggle.hidden = reduce.matches;
  };
  stage.classList.add('motion-ready');
  toggle.addEventListener('click', () => { requested = !requested; sync(); });
  document.addEventListener('visibilitychange', sync);
  reduce.addEventListener('change', () => { if (reduce.matches) requested = false; sync(); });
  if ('IntersectionObserver' in window) new IntersectionObserver(entries => {
    visible = entries.some(entry => entry.isIntersecting); sync();
  }, { threshold: 0.1 }).observe(stage);
  sync();
})();
