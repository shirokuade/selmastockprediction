# Selma Stock Prediction - Frontend

Modern Next.js frontend for AI-powered Indonesian stock prediction platform.

## Features

- 🎨 **Modern UI**: Built with Next.js 14, React, and Tailwind CSS
- 📊 **Interactive Charts**: Real-time prediction visualizations with Recharts
- ⚙️ **User Settings**: Customizable stock preferences and prediction parameters
- 📱 **Responsive Design**: Works perfectly on desktop and mobile devices
- 🚀 **Fast Performance**: Optimized with Next.js App Router and server-side rendering
- 🔄 **Real-time Data**: Live stock prices and AI predictions
- 🎯 **Easy Deployment**: Ready for Netlify deployment

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Date**: date-fns

## Prerequisites

- Node.js 18+ or npm 9+
- Backend API running (see ../backend/README.md)

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Setup Environment Variables

```bash
cp .env.local.example .env.local
```

Edit `.env.local`:

```env
# API URL - Local development
NEXT_PUBLIC_API_URL=http://localhost:8000

# App Configuration
NEXT_PUBLIC_APP_NAME=Selma Stock Prediction
NEXT_PUBLIC_DEFAULT_STOCK=BBCA
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Development

### Available Scripts

```bash
# Development server
npm run dev

# Type checking
npm run type-check

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

### Project Structure

```
frontend/
├── src/
│   ├── app/                # Next.js App Router pages
│   │   ├── layout.tsx      # Root layout
│   │   ├── page.tsx        # Home/Dashboard page
│   │   ├── settings/       # Settings page
│   │   └── globals.css     # Global styles
│   ├── components/         # React components
│   │   ├── ui/             # Reusable UI components
│   │   ├── Layout.tsx      # Main layout component
│   │   ├── PredictionChart.tsx
│   │   └── StockSelector.tsx
│   ├── lib/                # Utilities
│   │   ├── api.ts          # API client
│   │   └── utils.ts        # Helper functions
│   └── types/              # TypeScript types
│       └── index.ts
├── public/                 # Static files
├── package.json            # Dependencies
├── tsconfig.json          # TypeScript config
├── tailwind.config.js     # Tailwind config
└── next.config.js         # Next.js config
```

## Pages

### Dashboard (/)

The main page where users can:
- Select Indonesian stocks (BBCA, BMDR, TLKM, etc.)
- View current stock prices and information
- Generate AI-powered price predictions
- See prediction charts and trend analysis
- Review detailed daily forecasts

### Settings (/settings)

Configuration page where users can:
- Set default stock preference
- Configure prediction time horizon (3-30 days)
- Manage notification preferences
- View app information

## Components

### UI Components

- **Button**: Reusable button with variants and loading states
- **Card**: Container component for content sections
- **Loading**: Loading spinner with customizable size
- **Alert**: Alert messages (info, success, warning, error)

### Feature Components

- **Layout**: Main app layout with header and navigation
- **StockSelector**: Dropdown for selecting Indonesian stocks
- **PredictionChart**: Interactive line chart for price predictions

## API Integration

The frontend communicates with the backend through REST APIs:

```typescript
// Import API client
import { stockApi, predictionApi, settingsApi } from '@/lib/api';

// Get stock information
const stockInfo = await stockApi.getStockInfo('BBCA');

// Generate prediction
const prediction = await predictionApi.predict('BBCA', 5);

// Save settings
await settingsApi.saveSettings({
  default_stock: 'BBCA',
  prediction_days: 5,
  notification_enabled: false,
});
```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | http://localhost:8000 | Yes |
| `NEXT_PUBLIC_APP_NAME` | Application name | Selma Stock Prediction | No |
| `NEXT_PUBLIC_DEFAULT_STOCK` | Default stock symbol | BBCA | No |

## Building for Production

```bash
# Build the application
npm run build

# Test production build locally
npm start
```

## Deployment

### Deploy to Netlify

#### Option 1: Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Build and deploy
npm run build
netlify deploy --prod
```

#### Option 2: GitHub Integration

1. Push code to GitHub
2. Go to [Netlify](https://app.netlify.com/)
3. Click "New site from Git"
4. Select your repository
5. Configure build settings:
   - **Build command**: `npm run build`
   - **Publish directory**: `.next`
6. Add environment variables in Netlify dashboard
7. Deploy!

### Environment Variables for Netlify

In Netlify dashboard, add:

```
NEXT_PUBLIC_API_URL=https://your-backend-api.com
NEXT_PUBLIC_APP_NAME=Selma Stock Prediction
NEXT_PUBLIC_DEFAULT_STOCK=BBCA
```

### Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel
```

## Styling

### Tailwind CSS

The project uses Tailwind CSS for styling. Custom theme configuration is in `tailwind.config.js`:

```javascript
// Custom colors
primary: {
  50: '#f0f9ff',
  600: '#0284c7',
  // ...
},
success: '#10b981',
danger: '#ef4444',
warning: '#f59e0b',
```

### Custom Utilities

Helper functions in `src/lib/utils.ts`:

- `formatCurrency(value)`: Format as Indonesian Rupiah
- `formatPercentage(value)`: Format percentage with sign
- `formatDate(date)`: Format date
- `formatDateTime(date)`: Format date and time
- `getTrendColor(trend)`: Get color for trend indicator
- `cn(...)`: Combine class names

## Troubleshooting

### API Connection Issues

If frontend can't connect to backend:

1. **Check backend is running**: Visit http://localhost:8000/health
2. **Verify API URL**: Check `.env.local` has correct `NEXT_PUBLIC_API_URL`
3. **CORS issues**: Ensure backend allows requests from frontend URL

### Build Errors

```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Rebuild
npm run build
```

### Type Errors

```bash
# Run type checking
npm run type-check

# Fix common issues
# - Check imports
# - Verify TypeScript version compatibility
# - Ensure all dependencies are installed
```

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile browsers: iOS Safari 12+, Chrome Android

## Performance

- **Lighthouse Score**: 95+ for Performance, Accessibility, Best Practices, SEO
- **Bundle Size**: Optimized with Next.js automatic code splitting
- **Load Time**: < 2s on 3G networks

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open pull request

## License

MIT License - see LICENSE file

## Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Documentation: See main README.md

---

Built with ❤️ using Next.js and Tailwind CSS
