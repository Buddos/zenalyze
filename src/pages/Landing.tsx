import React from 'react'
import { Link } from 'react-router-dom'
import { Brain, Heart, Zap, TrendingUp, ArrowRight, CheckCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'

const Landing: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-hero">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-sm border-b border-zen-sage-light sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-calm rounded-lg flex items-center justify-center">
                  <Brain className="w-5 h-5 text-white" />
                </div>
                <span className="text-2xl font-serif font-bold text-gradient-calm">
                  Zenalyze
                </span>
              </div>
            </div>
            
            <div className="flex items-center space-x-6">
              <Link to="/login" className="text-zen-text hover:text-zen-sage transition-colors">
                Sign In
              </Link>
              <Link to="/signup">
                <Button className="bg-zen-sage hover:bg-zen-sage-dark">
                  Get Started
                  <ArrowRight className="ml-2 w-4 h-4" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-serif font-bold text-zen-text mb-6">
            Find Your <span className="text-gradient-calm">Inner Peace</span>
          </h1>
          <p className="text-xl text-zen-text-muted max-w-3xl mx-auto mb-10">
            Zenalyze helps you track your meditation journey, analyze wellness patterns, 
            and achieve mindfulness through data-driven insights.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/signup">
              <Button size="lg" className="bg-zen-sage hover:bg-zen-sage-dark px-8 py-6 text-lg">
                Start Free Trial
              </Button>
            </Link>
            <Link to="/login">
              <Button size="lg" variant="outline" className="px-8 py-6 text-lg border-zen-sage text-zen-sage">
                Sign In
              </Button>
            </Link>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-20">
          <div className="bg-white p-6 rounded-2xl shadow-card hover:shadow-hover transition-shadow">
            <div className="flex items-center justify-center w-12 h-12 bg-zen-sage-light rounded-xl mb-4">
              <Brain className="w-6 h-6 text-zen-sage" />
            </div>
            <h3 className="text-2xl font-bold text-zen-text mb-2">10K+</h3>
            <p className="text-zen-text-muted">Active Meditators</p>
          </div>
          
          <div className="bg-white p-6 rounded-2xl shadow-card hover:shadow-hover transition-shadow">
            <div className="flex items-center justify-center w-12 h-12 bg-zen-coral-light rounded-xl mb-4">
              <Heart className="w-6 h-6 text-zen-coral" />
            </div>
            <h3 className="text-2xl font-bold text-zen-text mb-2">85%</h3>
            <p className="text-zen-text-muted">Stress Reduction</p>
          </div>
          
          <div className="bg-white p-6 rounded-2xl shadow-card hover:shadow-hover transition-shadow">
            <div className="flex items-center justify-center w-12 h-12 bg-zen-lavender rounded-xl mb-4">
              <Zap className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-2xl font-bold text-zen-text mb-2">30 Days</h3>
            <p className="text-zen-text-muted">Average Streak</p>
          </div>
          
          <div className="bg-white p-6 rounded-2xl shadow-card hover:shadow-hover transition-shadow">
            <div className="flex items-center justify-center w-12 h-12 bg-zen-sky rounded-xl mb-4">
              <TrendingUp className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-2xl font-bold text-zen-text mb-2">4.9/5</h3>
            <p className="text-zen-text-muted">User Rating</p>
          </div>
        </div>

        {/* Features */}
        <div className="mb-20">
          <h2 className="text-3xl font-serif font-bold text-center text-zen-text mb-12">
            Transform Your Wellness Journey
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-gradient-card p-8 rounded-2xl shadow-card">
              <div className="animate-breathe mb-6">
                <div className="w-16 h-16 bg-gradient-calm rounded-2xl flex items-center justify-center">
                  <Brain className="w-8 h-8 text-white" />
                </div>
              </div>
              <h3 className="text-xl font-bold text-zen-text mb-3">Mindful Analytics</h3>
              <p className="text-zen-text-muted">
                Track your meditation patterns, mood changes, and progress with beautiful visualizations.
              </p>
            </div>
            
            <div className="bg-gradient-card p-8 rounded-2xl shadow-card">
              <div className="animate-float mb-6">
                <div className="w-16 h-16 bg-gradient-mood-calm rounded-2xl flex items-center justify-center">
                  <Heart className="w-8 h-8 text-white" />
                </div>
              </div>
              <h3 className="text-xl font-bold text-zen-text mb-3">Guided Sessions</h3>
              <p className="text-zen-text-muted">
                Access hundreds of guided meditations for stress, sleep, focus, and emotional balance.
              </p>
            </div>
            
            <div className="bg-gradient-card p-8 rounded-2xl shadow-card">
              <div className="animate-pulse-gentle mb-6">
                <div className="w-16 h-16 bg-gradient-mood-happy rounded-2xl flex items-center justify-center">
                  <TrendingUp className="w-8 h-8 text-white" />
                </div>
              </div>
              <h3 className="text-xl font-bold text-zen-text mb-3">Progress Tracking</h3>
              <p className="text-zen-text-muted">
                Set goals, track streaks, and celebrate milestones in your mindfulness journey.
              </p>
            </div>
          </div>
        </div>

        {/* Benefits */}
        <div className="bg-white rounded-3xl p-12 shadow-card mb-20">
          <h2 className="text-3xl font-serif font-bold text-center text-zen-text mb-12">
            Why Choose Zenalyze?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {[
              "Personalized meditation recommendations",
              "Mood tracking with AI insights",
              "Community support groups",
              "Professional therapy sessions",
              "Emergency resources",
              "Daily wellness exercises"
            ].map((benefit, index) => (
              <div key={index} className="flex items-start space-x-3">
                <CheckCircle className="w-6 h-6 text-zen-sage flex-shrink-0 mt-1" />
                <span className="text-zen-text">{benefit}</span>
              </div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="bg-gradient-calm rounded-3xl p-12 text-center shadow-card">
          <h2 className="text-3xl font-serif font-bold text-white mb-4">
            Start Your Mindfulness Journey Today
          </h2>
          <p className="text-white/90 mb-8 max-w-2xl mx-auto">
            Join thousands who have found peace and clarity through Zenalyze. 
            No credit card required for the 14-day free trial.
          </p>
          <Link to="/signup">
            <Button size="lg" className="bg-white text-zen-sage hover:bg-zen-cream px-10 py-6 text-lg">
              Begin Free Trial
            </Button>
          </Link>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-zen-sage-light py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-6 md:mb-0">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-calm rounded-lg flex items-center justify-center">
                  <Brain className="w-5 h-5 text-white" />
                </div>
                <span className="text-2xl font-serif font-bold text-gradient-calm">
                  Zenalyze
                </span>
              </div>
              <p className="text-zen-text-muted mt-2">
                Mindfulness meets analytics
              </p>
            </div>
            
            <div className="flex flex-col md:flex-row items-center space-y-4 md:space-y-0 md:space-x-6">
              <Link to="/login" className="text-zen-text hover:text-zen-sage">
                Sign In
              </Link>
              <Link to="/signup" className="text-zen-text hover:text-zen-sage">
                Sign Up
              </Link>
              <a href="#" className="text-zen-text hover:text-zen-sage">
                Privacy Policy
              </a>
              <a href="#" className="text-zen-text hover:text-zen-sage">
                Terms of Service
              </a>
            </div>
          </div>
          
          <div className="text-center mt-8 pt-8 border-t border-zen-sage-light">
            <p className="text-zen-text-muted">
              © {new Date().getFullYear()} Zenalyze. All rights reserved.
            </p>
            <p className="text-zen-text-muted text-sm mt-1">
              Made with ❤️ for better mental health
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Landing
