// 页内锚点跳转。哈希路由下 href="#xxx" 会被当成路由,所以统一拦截后手动滚动。
export function jump(e) {
  e.preventDefault()
  const id = e.currentTarget.getAttribute('href')?.slice(1)
  const el = id && document.getElementById(id)
  if (el) el.scrollIntoView({ behavior: 'smooth' })
  else scrollTo({ top: 0, behavior: 'smooth' })
}
