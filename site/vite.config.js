import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 让打包产物可以直接双击 index.html 打开(file://):
// 1) base './' 用相对路径;2) 输出 IIFE 并去掉 type="module" / crossorigin(浏览器不允许 file:// 加载模块脚本)。
// 路由使用哈希模式,所以刷新、直达 #/admin/... 都不依赖服务器。
const openFromDisk = () => ({
  name: 'open-from-disk',
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
  plugins: [vue(), openFromDisk()],
  build: {
    rollupOptions: { output: { format: 'iife', inlineDynamicImports: true } },
  },
})
