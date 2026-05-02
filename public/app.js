/* ─── NAV SCROLL ─── */
const nav = document.getElementById('nav');
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 20);
}, { passive: true });

/* ─── MOBILE NAV ─── */
const navToggle = document.getElementById('navToggle');
const navLinks  = document.getElementById('navLinks');
navToggle.addEventListener('click', () => {
  const open = navLinks.classList.toggle('open');
  navToggle.setAttribute('aria-expanded', String(open));
});
navLinks.querySelectorAll('a').forEach(a => {
  a.addEventListener('click', () => {
    navLinks.classList.remove('open');
    navToggle.setAttribute('aria-expanded', 'false');
  });
});

/* ─── HERO PARTICLE CANVAS ─── */
(function () {
  const canvas = document.getElementById('heroCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let W, H, nodes = [], animId;

  function resize() {
    W = canvas.width  = canvas.offsetWidth;
    H = canvas.height = canvas.offsetHeight;
  }
  window.addEventListener('resize', () => { resize(); init(); }, { passive: true });

  function rand(min, max) { return Math.random() * (max - min) + min; }

  function init() {
    nodes = Array.from({ length: 60 }, () => ({
      x:  rand(0, W), y:  rand(0, H),
      vx: rand(-0.3, 0.3), vy: rand(-0.3, 0.3),
      r:  rand(1, 2.5),
    }));
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    // connections
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[i].x - nodes[j].x;
        const dy = nodes[i].y - nodes[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 140) {
          ctx.beginPath();
          ctx.moveTo(nodes[i].x, nodes[i].y);
          ctx.lineTo(nodes[j].x, nodes[j].y);
          ctx.strokeStyle = `rgba(124,58,237,${0.15 * (1 - dist / 140)})`;
          ctx.lineWidth = 0.8;
          ctx.stroke();
        }
      }
    }
    // dots
    nodes.forEach(n => {
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(124,58,237,0.5)';
      ctx.fill();
      n.x += n.vx; n.y += n.vy;
      if (n.x < 0 || n.x > W) n.vx *= -1;
      if (n.y < 0 || n.y > H) n.vy *= -1;
    });
    animId = requestAnimationFrame(draw);
  }

  resize();
  init();
  draw();
})();

/* ─── INTERSECTION OBSERVER – fade in cards ─── */
const observer = new IntersectionObserver(
  (entries) => entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.style.opacity = '1';
      e.target.style.transform = 'translateY(0)';
      observer.unobserve(e.target);
    }
  }),
  { threshold: 0.08 }
);

document.querySelectorAll('.product-card, .solution-card, .testimonial-card, .how-step').forEach((el, i) => {
  el.style.opacity    = '0';
  el.style.transform  = 'translateY(24px)';
  el.style.transition = `opacity 0.5s ease ${i * 0.05}s, transform 0.5s ease ${i * 0.05}s`;
  observer.observe(el);
});

/* ─── CONTACT FORM (demo submit) ─── */
const form    = document.getElementById('contactForm');
const success = document.getElementById('formSuccess');
if (form) {
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    // basic validation
    const required = form.querySelectorAll('[required]');
    let valid = true;
    required.forEach(input => {
      if (!input.value.trim()) {
        valid = false;
        input.style.borderColor = '#f43f5e';
        input.addEventListener('input', () => { input.style.borderColor = ''; }, { once: true });
      }
    });
    if (!valid) return;
    const btn = form.querySelector('button[type="submit"]');
    btn.textContent = 'Sending…';
    btn.disabled = true;
    // simulate async
    setTimeout(() => {
      success.classList.add('visible');
      form.reset();
      btn.textContent = 'Send Message';
      btn.disabled = false;
      setTimeout(() => success.classList.remove('visible'), 6000);
    }, 1200);
  });
}
