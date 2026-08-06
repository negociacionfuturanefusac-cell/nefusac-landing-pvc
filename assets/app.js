/* NEFUSAC — lo minimo indispensable en el cliente (~2 KB).
 *
 * El resto salio del JavaScript: la entrada progresiva es CSS
 * (animation-timeline: view()), la descarga del catalogo es un <a download>,
 * el marquee y el parallax son CSS. Queda solo lo que no tiene equivalente
 * declarativo:
 *   1. arrancar los videos 2 y 3 al entrar en pantalla (preload="none")
 *   2. la cuenta ascendente de los indicadores
 *   3. armar el mensaje de WhatsApp del formulario
 * Nada de esto oculta contenido: sin JS la pagina se lee completa y las
 * cifras ya vienen escritas en el HTML.
 */
(function () {
  'use strict';

  /* 1 · videos diferidos ------------------------------------------------ */
  var diferidos = document.querySelectorAll('video[data-diferido]');
  if (diferidos.length && 'IntersectionObserver' in window) {
    var ov = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        var v = e.target;
        if (e.isIntersecting) {
          v.muted = true;
          if (!v.dataset.listo) { v.dataset.listo = '1'; v.load(); }
          v.play().catch(function () {});
        } else if (!v.paused) {
          v.pause();
        }
      });
    }, { threshold: 0.2 });
    diferidos.forEach(function (v) { ov.observe(v); });
  }

  /* el video del hero: algunos navegadores descartan el atributo muted */
  var hero = document.querySelector('video[data-hero]');
  if (hero) {
    hero.muted = true;
    hero.play().catch(function () {});
  }

  /* 2 · indicadores ------------------------------------------------------ */
  var cifras = document.querySelectorAll('[data-count]');
  if (cifras.length && 'IntersectionObserver' in window &&
      !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var oc = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        oc.unobserve(e.target);
        var fin = parseInt(e.target.getAttribute('data-count'), 10);
        var t0 = performance.now();
        (function paso(t) {
          var p = Math.min((t - t0) / 1600, 1);
          e.target.textContent = Math.round(fin * (1 - Math.pow(1 - p, 3)));
          if (p < 1) requestAnimationFrame(paso);
        })(t0);
      });
    }, { threshold: 0.5 });
    cifras.forEach(function (c) { oc.observe(c); });
  }

  /* 3 · formulario -> WhatsApp ------------------------------------------ */
  var form = document.querySelector('[data-form-cotiza]');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var f = new FormData(form);
      var l = function (k, v) { return v ? k + ': ' + v + '\n' : ''; };
      var msg = 'Hola NEFUSAC, quiero una cotización.\n' +
        l('Nombre', f.get('nombre')) + l('Correo', f.get('correo')) +
        l('Teléfono', f.get('telefono')) + l('Proyecto', f.get('proyecto')) +
        l('Mensaje', f.get('mensaje'));
      window.open('https://wa.me/51981124794?text=' + encodeURIComponent(msg.trim()) +
        '&utm_source=web&utm_medium=form&utm_content=formulario', '_blank', 'noopener');
      var ok = form.querySelector('[data-form-ok]');
      if (ok) { ok.hidden = false; }
    });
  }
})();
