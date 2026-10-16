import { cpSync, createReadStream, existsSync, statSync } from 'node:fs'
import { extname, join, normalize } from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const FRONTEND = fileURLToPath(new URL('../frontend', import.meta.url))
const PANORAMAS = join(FRONTEND, 'public', 'panoramas')

// 与 frontend 共用同一份全景图与 manifest(项目里已适配好的 3D / 全景素材),
// 不在 site/ 里再复制一份 21MB 的图片:开发时转发 /panoramas,打包时复制进 dist。
const sharePanoramas = () => {
  let outDir = 'dist'
  const types = { '.jpg': 'image/jpeg', '.png': 'image/png', '.json': 'application/json' }
  return {
    name: 'share-panoramas',
    configResolved: (c) => { outDir = join(c.root, c.build.outDir) },
    configureServer(server) {
      server.middlewares.use('/panoramas', (req, res, next) => {
        const rel = decodeURIComponent((req.url || '/').split('?')[0])
        const file = normalize(join(PANORAMAS, rel))
        if (!file.startsWith(PANORAMAS) || !existsSync(file) || !statSync(file).isFile()) return next()
        res.setHeader('Content-Type', types[extname(file)] || 'application/octet-stream')
        createReadStream(file).pipe(res)
      })
    },
    closeBundle() {
      if (existsSync(PANORAMAS)) cpSync(PANORAMAS, join(outDir, 'panoramas'), { recursive: true })
    },
  }
}

// 打包产物用相对路径 + 非 module 脚本,配合哈希路由,可部署在任意静态服务器上。
const classicScript = () => ({
  name: 'classic-script',
  apply: 'build',
  transformIndexHtml: {
    order: 'post',
    handler: (html) => html
      .replace(/<script type="module" crossorigin/g, '<script defer')
      .replace(/<link rel="stylesheet" crossorigin/g, '<link rel="stylesheet"'),
  },
})

export default defineConfig({
  base: './',
  plugins: [vue(), sharePanoramas(), classicScript()],
  resolve: {
    alias: { '@frontend': join(FRONTEND, 'src') },
  },
  server: {
    // 允许读取上一级的 frontend/src/api/pano.js
    fs: { allow: ['..'] },
  },
  build: {
    rollupOptions: { output: { format: 'iife', inlineDynamicImports: true } },
  },
})
