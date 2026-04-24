import type { Config } from 'tailwindcss'
const config: Config = {
  content: ['./app/**/*.{js,ts,jsx,tsx}','./components/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        bg:       '#FFFFFF',
        subtle:   '#F7F6F3',
        raised:   '#EFEEE8',
        border:   '#E5E3DC',
        border2:  '#CFCDC5',
        text:     '#0F1117',
        text2:    '#48484F',
        muted:    '#96969E',
        accent:   '#1A3A5C',
        gold:     '#B8821E',
        green:    '#1A6644',
        red:      '#B83232',
      },
      fontFamily: {
        display: ['Playfair Display','Georgia','serif'],
        body:    ['Inter','-apple-system','sans-serif'],
        mono:    ['JetBrains Mono','monospace'],
      },
    },
  },
  plugins: [],
}
export default config
