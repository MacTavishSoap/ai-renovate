import { reduce } from './data'

const SHOW = 0.14

const countTo = (el, to) => {
  if (reduce) return (el.textContent = to)
  const from = parseInt(el.textContent, 10) || 0
  if (from === to) return
  if (el._raf) cancelAnimationFrame(el._raf)
  const t0 = performance.now()
  const step = (t) => {
    const p = Math.min(1, (t - t0) / 900)
    el.textContent = Math.round(from + (to - from) * (1 - Math.pow(1 - p, 3)))
    if (p < 1) el._raf = requestAnimationFrame(step)
  }
  el._raf = requestAnimationFrame(step)
}

const snapRy = (el, ry) => {
  if (el.style.getPropertyValue('--ry') === ry) return
  el.style.transition = 'none'
  el.style.setProperty('--ry', ry)
  void el.offsetWidth
  el.style.transition = ''
}

export function bindMotion() {
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      const el = entry.target
      const top = entry.boundingClientRect.top
      const prev = el._top
      el._top = top
      const goingUp = prev !== undefined && top > prev + 1
      const visible = el.classList.contains('pickets')
        ? entry.isIntersecting
        : entry.intersectionRatio >= SHOW

      if (visible) {
        if (el.classList.contains('in')) return
        if (el.classList.contains('reveal')) snapRy(el, goingUp ? '-24px' : '24px')
        el.classList.add('in')
        if (el.classList.contains('pickets') && !reduce) {
          clearTimeout(el._live)
          el._live = setTimeout(() => el.classList.add('live'), 1400)
        }
        el.querySelectorAll('[data-count]').forEach((n) => countTo(n, +n.dataset.count))
      } else {
        if (!el.classList.contains('in')) return
        if (el.classList.contains('reveal')) el.style.setProperty('--ry', goingUp ? '24px' : '-24px')
        clearTimeout(el._live)
        el.classList.remove('in', 'live')
        if (el.classList.contains('pickets')) {
          ;[...el.children].forEach((b) => (b.style.transform = ''))
        }
        el.querySelectorAll('[data-count]').forEach((n) => countTo(n, 0))
      }
    })
  }, { threshold: [0, SHOW] })

  document.querySelectorAll('.reveal, .pickets').forEach((el) => io.observe(el))
  return () => io.disconnect()
}
