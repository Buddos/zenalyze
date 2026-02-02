import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { Heart, Sparkles, Shield } from "lucide-react";

const Hero = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-hero">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 left-10 w-72 h-72 bg-zen-sage-light/40 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-zen-lavender/30 rounded-full blur-3xl animate-float" style={{ animationDelay: "2s" }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-zen-sky/20 rounded-full blur-3xl animate-breathe" />
      </div>

      <div className="container relative z-10 px-4 py-20 text-center">
        <div className="animate-fade-in-up">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 mb-8 rounded-full bg-zen-sage-light/50 border border-zen-sage/20">
            <Sparkles className="w-4 h-4 text-zen-sage" />
            <span className="text-sm font-medium text-zen-sage-dark">AI-Powered Mental Wellness</span>
          </div>

          {/* Main heading */}
          <h1 className="font-serif text-5xl md:text-7xl lg:text-8xl font-semibold tracking-tight mb-6 text-foreground">
            Your Mind
            <br />
            <span className="text-gradient-calm">Deserves Peace</span>
          </h1>

          {/* Subheading */}
          <p className="max-w-2xl mx-auto text-lg md:text-xl text-muted-foreground mb-10 leading-relaxed">
            Zenalyze is your compassionate AI companion for mental wellness. 
            Track your moods, practice mindfulness, and access support whenever you need it.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
            <Link to="/signup">
              <Button variant="hero" size="xl">
                Start Your Journey
              </Button>
            </Link>
            <Link to="/login">
              <Button variant="outline" size="xl">
                Sign In
              </Button>
            </Link>
          </div>

          {/* Trust indicators */}
          <div className="flex flex-wrap items-center justify-center gap-8 text-muted-foreground">
            <div className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-zen-sage" />
              <span className="text-sm">Private & Secure</span>
            </div>
            <div className="flex items-center gap-2">
              <Heart className="w-5 h-5 text-zen-coral" />
              <span className="text-sm">Evidence-Based</span>
            </div>
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-zen-lavender" />
              <span className="text-sm">AI-Enhanced</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
