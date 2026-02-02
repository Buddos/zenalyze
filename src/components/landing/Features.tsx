import { Brain, MessageCircle, Calendar, Wind, Phone, BookOpen } from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "AI Mood Analysis",
    description: "Track your emotional patterns with intelligent insights that help you understand your mental health journey.",
    gradient: "from-zen-sage to-zen-sky",
  },
  {
    icon: MessageCircle,
    title: "AI Chat Therapist",
    description: "Have meaningful conversations with our empathetic AI companion, available 24/7 for support.",
    gradient: "from-zen-lavender to-zen-coral",
  },
  {
    icon: Wind,
    title: "Guided Exercises",
    description: "Access meditation, breathing exercises, and CBT techniques designed by mental health experts.",
    gradient: "from-zen-sky to-zen-sage",
  },
  {
    icon: Calendar,
    title: "Teletherapy Booking",
    description: "Connect with licensed therapists for video sessions when you need professional support.",
    gradient: "from-zen-coral to-zen-lavender",
  },
  {
    icon: BookOpen,
    title: "Mood Journal",
    description: "Document your thoughts and feelings in a private, secure space with AI-powered reflections.",
    gradient: "from-zen-sage to-zen-coral",
  },
  {
    icon: Phone,
    title: "Crisis Resources",
    description: "Quick access to emergency helplines and crisis support when you need immediate help.",
    gradient: "from-zen-lavender to-zen-sage",
  },
];

const Features = () => {
  return (
    <section className="py-24 bg-background">
      <div className="container px-4">
        <div className="text-center mb-16 animate-fade-in">
          <h2 className="font-serif text-4xl md:text-5xl font-semibold mb-4 text-foreground">
            Everything You Need for
            <br />
            <span className="text-primary">Mental Wellness</span>
          </h2>
          <p className="max-w-2xl mx-auto text-lg text-muted-foreground">
            A comprehensive toolkit designed to support your mental health journey with care and compassion.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <div
              key={feature.title}
              className="group p-8 rounded-2xl bg-card border border-border hover:border-primary/30 transition-all duration-300 hover:shadow-card animate-fade-in-up"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                <feature.icon className="w-7 h-7 text-primary-foreground" />
              </div>
              <h3 className="font-serif text-xl font-semibold mb-3 text-foreground">
                {feature.title}
              </h3>
              <p className="text-muted-foreground leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;
