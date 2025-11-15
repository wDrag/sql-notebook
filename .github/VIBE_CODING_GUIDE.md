# Vibe Coding Guide - Carpital Client

A guide to prompt AI coding agents efficiently for maximum productivity in this Next.js/React codebase.

## 🎯 Core Prompting Principles

### 1. **Be Specific, Not Verbose**

❌ "Can you help me create a component that displays user data with some styling?"
✅ "Create `UserCard` in `src/components/ui/` using Radix Card + Tailwind, displays name, email, avatar"

### 2. **Reference Existing Patterns**

❌ "Add a new API endpoint for users"
✅ "Add `/users` endpoint to `src/apis/client.ts` following the singleton pattern like existing methods"

### 3. **State Your Constraints**

❌ "Make a dashboard page"
✅ "Create `/dashboard/analytics` page as Server Component, fetch data with TanStack Query, use existing Card components"

## ⚡ Quick Commands for Common Tasks

### API & Data Fetching

```
"Add REST endpoint GET /api/trading/symbols in client.ts"
"Create useSymbols query hook in src/hooks/queries/ returning Symbol[]"
"Add socket listener for 'price-update' in trading namespace"
"Connect GraphQL endpoint /graphql/markets, add to graphql-client.ts"
```

### Components

```
"Create PriceCard in src/components/ui/ - Radix Card, shows price + 24h change with green/red color"
"Add TradingButton to ui/ - extends Button component, loading state with Skeleton"
"Update AppSidebar - add 'Analytics' route to /dashboard/analytics with ChartBar icon"
```

### Pages & Routing

```
"Create /dashboard/portfolio page - Server Component, grid of PortfolioCard components"
"Add client page /trading/live with TradingView chart using CarpitalDataFeed"
"Update layout.tsx - add Toaster component from sonner"
```

### State & Forms

```
"Create Jotai atom for selected symbol in src/atoms/trading.ts"
"Add mutation hook useCreateOrder in src/hooks/mutations/ with axios POST"
"Create OrderForm with react-hook-form + zod schema, fields: symbol, quantity, price"
```

### Styling & Animation

```
"Add fade-in animation to Card using tailwindcss-animate"
"Style error state - red border, red text, shake animation"
"Make layout responsive - sidebar collapses on mobile, hamburger menu"
```

## 🚀 Advanced Vibe Coding Patterns

### Multi-Step Feature Requests

```
"Create portfolio feature:
1. Add /api/portfolio endpoint to client.ts
2. Create usePortfolio query hook
3. Build PortfolioTable component with holdings data
4. Add /dashboard/portfolio page
5. Update AppSidebar with Portfolio link"
```

### Socket.IO Integration

```
"Setup trading socket:
1. Get socket from getSocket('/trading')
2. Connect on mount
3. Subscribe to 'ticker-update' with { symbol: 'BTC/USD' }
4. Update price state on message
5. Cleanup on unmount"
```

### TradingView Chart Setup

```
"Add TradingView chart to /trading page:
1. Import charting_library (don't modify vendor files)
2. Use CarpitalDataFeed with BTC/USD symbols
3. Initialize with dark theme
4. Add loading skeleton
5. Handle cleanup"
```

## 🎨 Component Patterns

### Radix UI + Tailwind Pattern

```
"Create AlertDialog component:
- Use @radix-ui/react-alert-dialog
- Trigger: red Button variant
- Title: bold text-lg
- Description: text-muted-foreground
- Actions: Cancel (outline) + Confirm (destructive)"
```

### Server Component → Client Component Pattern

```
"Dashboard page pattern:
- Server Component fetches initial data
- Pass to client PortfolioChart component
- Chart uses TanStack Query for updates
- Show Skeleton while loading"
```

## 🔧 Debugging Prompts

### Common Issues

```
"Fix hydration error in layout.tsx - suppressHydrationWarning needed where?"
"Socket not connecting - check ENV.SOCKET_URL and namespace format"
"Build error in client.ts - fix import path to use @/ alias"
"Chart not loading - verify TradingView library bundle imports"
```

### Error Investigation

```
"Check why useSymbols query fails - log axios request, check ENV.API_URL"
"Debug socket disconnection - add logger.log in socket.ts connection handlers"
"Fix type error in datafeed.ts - check LibrarySymbolInfo interface"
```

## 📋 Code Review Prompts

### Quality Checks

```
"Review component for issues: Server vs Client, proper error handling, loading states, types"
"Check API integration: ENV constants used? Error handling? TypeScript types?"
"Verify styling: Tailwind only? No inline styles? Responsive classes? Theme-aware?"
"Audit socket usage: Cleanup in useEffect? Error handlers? Reconnection logic?"
```

### Refactoring

```
"Extract repeated card styling to Card variant in ui/card.tsx"
"Move price formatting logic to src/lib/utils/common.ts"
"Combine duplicate socket listeners into custom hook useSocketChannel"
"Split large dashboard page into smaller components"
```

## 🎯 Domain-Specific Prompts

### Trading Features

```
"Add order placement:
- OrderForm with symbol dropdown, quantity input, price input
- useCreateOrder mutation hook
- POST to /api/orders with validation
- Show toast on success/error
- Disable form while submitting"
```

### Real-Time Data

```
"Setup live price ticker:
- Get socket from getSocket('/market')
- Subscribe to 'prices' channel
- Update Jotai atom with price map
- Display in PriceTicker component with color animation on change"
```

### Chart Integration

```
"Customize TradingView datafeed:
- Update symbols in helpers.ts getAllSymbols()
- Modify streaming.ts subscribeOnStream to use socket
- Add volume data to bars
- Enable compare mode"
```

## 💡 Pro Tips

### Efficiency Hacks

1. **Batch related changes**: "Add API + hook + component in one go"
2. **Reference similar code**: "Like PriceCard but for OrderHistory"
3. **Specify file locations**: Always include full paths
4. **Use existing utilities**: "Use formatTime from common.ts"
5. **Follow conventions**: "Match existing mutation hook pattern"

### What NOT to Say

❌ "Make it better" (too vague)
❌ "Add some tests" (not specific enough)
❌ "Fix the styling" (which styles? where?)
❌ "Create a function" (for what? where?)
❌ "Update the component" (which component? what changes?)

### What TO Say

✅ "Refactor PriceCard to accept variant prop: 'compact' | 'detailed'"
✅ "Add error boundary to dashboard page, show fallback UI with retry button"
✅ "Extract socket connection logic from TradingChart to useSocket() hook"
✅ "Add loading skeleton to PortfolioTable matching Card skeleton style"
✅ "Update formatPrice in common.ts to handle crypto decimal places (8 digits)"

## 🛠️ Terminal Commands via Prompts

```
"Run dev server and check for build errors"
"Install @radix-ui/react-select with pnpm"
"Format all files with prettier"
"Check type errors in src/components/ui/"
"Run lint and fix auto-fixable issues"
```

## 📚 Learning from Codebase

### Exploration Prompts

```
"Show me how socket.ts handles namespace switching"
"Explain the datafeed pattern in trading-chart/datafeed.ts"
"What's the query invalidation strategy in mutations?"
"How does AppSidebar routing work?"
"Where are theme colors defined?"
```

## 🎬 Example Workflows

### Feature: Live Order Book

```
Prompt:
"Create live order book feature:

1. API:
   - Add GET /api/orderbook/:symbol to client.ts
   - Returns { bids: [], asks: [] }

2. Socket:
   - Connect to '/trading' namespace
   - Subscribe to 'orderbook-update' with symbol
   - Handle { bids, asks, timestamp }

3. State:
   - Create orderBookAtom in src/atoms/trading.ts
   - Type: { bids: Order[], asks: Order[] }

4. Component: src/components/trading/OrderBook.tsx
   - Client component with socket subscription
   - Split view: bids (green) left, asks (red) right
   - Display price, quantity, total columns
   - Use Skeleton while loading
   - Animate row updates with GSAP

5. Integration:
   - Add to /trading/[symbol] page
   - Position below TradingView chart
   - Responsive: stack on mobile

Follow existing patterns, use ENV constants, add proper types."
```

### Feature: Portfolio Analytics

```
Prompt:
"Build portfolio analytics dashboard:

1. Data layer:
   - usePortfolio() query hook - GET /api/portfolio
   - usePortfolioHistory() - GET /api/portfolio/history?period=30d
   - Returns { holdings, totalValue, change24h, history }

2. Components:
   - PortfolioSummary: total value, 24h change, allocation pie chart
   - HoldingsTable: symbol, quantity, value, change columns
   - PerformanceChart: line chart with history data

3. Page: /dashboard/portfolio
   - Server Component with initial data
   - Client components for interactive charts
   - Update every 10s with TanStack Query refetch

4. Navigation:
   - Add to AppSidebar with Wallet icon
   - Active state styling

Use existing Card, Table patterns. Add loading skeletons. Handle empty state."
```

## 🎓 Context Clues for Better Results

Always mention:

- **Component type**: "Client Component" or "Server Component"
- **Data source**: "TanStack Query", "Jotai atom", "props", "socket"
- **Styling approach**: "Radix + Tailwind", "existing Card pattern"
- **Integration points**: "Add to AppSidebar", "use in dashboard page"
- **Error handling**: "Show toast on error", "display error boundary"

## 🚦 Quality Checklist Prompts

Before committing, ask:

```
"Verify this feature meets standards:
- TypeScript types defined and exported?
- ENV constants used (no hardcoded URLs)?
- Error handling in API calls?
- Loading states with Skeleton?
- Socket cleanup in useEffect?
- Tailwind classes only (no inline styles)?
- Responsive on mobile?
- Theme colors (not hardcoded hex)?
- pnpm used (not npm/yarn)?
- Files in correct directories?"
```

---

**Remember:** The more context and specificity you provide, the better the AI can vibe with your codebase patterns and deliver exactly what you need. Happy vibing! 🚀
