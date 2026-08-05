import { defineConfig } from 'vite'
import { resolve } from 'path'
import autoprefixer from 'autoprefixer'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
    publicDir: resolve(__dirname, 'public'),
    plugins: [tailwindcss()],

    root: resolve('./src'),
    base: '/assets/',
    server: {
        host: 'localhost',
        port: 3000,
        open: false,
        watch: {
            usePolling: true,
            interval: 100,
            disableGlobbing: false,
            ignored: [
                '**/node_modules/**',
                '**/dist/**',
                '**/venv/**',
                '**/static/**',
                '**/src_compiled/**',
                '**/assets/**',
            ],
        },
    },
    resolve: {
        extensions: ['.js', '.ts', '.css', 'ico'],
        alias: {
            '@': resolve(__dirname, 'src'),
        },
    },
    css: {
        extract: true,
        postcss: {
            plugins: [autoprefixer()],
        },
    },
    build: {
        outDir: resolve('./src_compiled'),
        assetsDir: '',
        manifest: true,
        sourcemap: true,
        target: 'es2015',
        emptyOutDir: true,
        rollupOptions: {
            input: {
                main: resolve('./src/js/main.js'),
                css: resolve('./src/css/styles.css'),
            },
            output: {
                entryFileNames: `[name].js`,
                chunkFileNames: `chunks/[name]-[hash].js`,
                assetFileNames: ({ name }) => {
                    if (name.endsWith('.css')) return 'css/[name][extname]'
                    if (
                        name.endsWith('.png') ||
                        name.endsWith('.jpg') ||
                        name.endsWith('.gif') ||
                        name.endsWith('.svg')
                    )
                        return 'images/[name][extname]'
                    if (
                        name.endsWith('.woff') ||
                        name.endsWith('.woff2') ||
                        name.endsWith('.ttf') ||
                        name.endsWith('.otf') ||
                        name.endsWith('.eot')
                    )
                        return 'fonts/[name][extname]'
                    return '[name][extname]'
                },
            },
        },
    },
})