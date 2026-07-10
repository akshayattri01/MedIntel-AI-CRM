export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#101828',
        brand: { 50: '#eff6ff', 500: '#3b82f6', 600: '#2563eb', 700: '#1d4ed8' }
      },
      boxShadow: { soft: '0 16px 45px rgba(15, 23, 42, 0.08)' }
    }
  },
  plugins: []
};
