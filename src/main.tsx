import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// Error boundary for production
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Zenalyze App Error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gradient-hero flex items-center justify-center p-6">
          <div className="bg-white shadow-card rounded-xl p-8 max-w-md text-center">
            <div className="text-6xl mb-4">😔</div>
            <h1 className="text-2xl font-serif font-bold text-zen-sage mb-2">
              Something went wrong
            </h1>
            <p className="text-zen-text-muted mb-6">
              We apologize for the inconvenience. Please refresh the page or try again later.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="bg-zen-sage text-white px-6 py-2 rounded-lg hover:bg-zen-sage-dark transition-colors"
            >
              Refresh Page
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

const rootElement = document.getElementById('root')
if (!rootElement) {
  throw new Error('Root element not found')
}

// Remove loading spinner when app is ready
const loadingSpinner = document.querySelector('#root > div')
if (loadingSpinner) {
  loadingSpinner.remove()
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
)
