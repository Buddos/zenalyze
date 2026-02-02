import { Link } from "react-router-dom";
import { Leaf, Heart } from "lucide-react";

const Footer = () => {
  return (
    <footer className="py-12 bg-muted/50 border-t border-border">
      <div className="container px-4">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
              <Leaf className="w-4 h-4 text-primary-foreground" />
            </div>
            <span className="font-serif text-lg font-semibold text-foreground">Zenalyze</span>
          </Link>

          <p className="text-sm text-muted-foreground flex items-center gap-1">
            Made with <Heart className="w-4 h-4 text-zen-coral" /> for your mental wellness
          </p>

          <div className="flex items-center gap-6 text-sm text-muted-foreground">
            <Link to="/dashboard/emergency" className="hover:text-foreground transition-colors">
              Crisis Support
            </Link>
            <span className="text-border">|</span>
            <span>© 2024 Zenalyze</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
