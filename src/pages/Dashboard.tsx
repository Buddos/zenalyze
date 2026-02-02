import { useState } from "react";
import DashboardLayout from "@/components/dashboard/DashboardLayout";
import MoodPicker from "@/components/dashboard/MoodPicker";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/hooks/use-toast";
import { Brain, TrendingUp, Calendar, Sparkles } from "lucide-react";

const Dashboard = () => {
  const [selectedMood, setSelectedMood] = useState<{ emoji: string; label: string; value: number } | null>(null);
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);
  const { user } = useAuth();
  const { toast } = useToast();

  const handleSaveMood = async () => {
    if (!selectedMood || !user) return;

    setSaving(true);
    try {
      const { error } = await supabase.from("mood_entries").insert({
        user_id: user.id,
        mood_score: selectedMood.value,
        mood_label: selectedMood.label,
        notes: notes || null,
      });

      if (error) throw error;

      toast({
        title: "Mood logged!",
        description: "Your mood has been recorded. Keep tracking!",
      });

      setSelectedMood(null);
      setNotes("");
    } catch (error: any) {
      toast({
        title: "Failed to save",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
        {/* Header */}
        <div>
          <h1 className="font-serif text-3xl font-semibold text-foreground mb-2">
            Welcome back 👋
          </h1>
          <p className="text-muted-foreground">
            How are you feeling today? Take a moment to check in with yourself.
          </p>
        </div>

        {/* Mood Check-in Card */}
        <div className="bg-card border border-border rounded-2xl p-8 shadow-soft">
          <div className="text-center mb-8">
            <h2 className="font-serif text-2xl font-semibold text-foreground mb-2">
              Daily Check-in
            </h2>
            <p className="text-muted-foreground">
              Select the emoji that best represents your current mood
            </p>
          </div>

          <MoodPicker
            onSelect={setSelectedMood}
            selectedMood={selectedMood?.value}
          />

          {selectedMood && (
            <div className="mt-8 space-y-4 animate-fade-in">
              <Textarea
                placeholder="What's on your mind? (optional)"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="min-h-[100px] resize-none"
              />
              <Button
                variant="hero"
                size="lg"
                onClick={handleSaveMood}
                disabled={saving}
                className="w-full"
              >
                {saving ? "Saving..." : "Log My Mood"}
              </Button>
            </div>
          )}
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-card border border-border rounded-xl p-6 flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-zen-sage-light flex items-center justify-center">
              <Calendar className="w-6 h-6 text-zen-sage" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-foreground">0</p>
              <p className="text-sm text-muted-foreground">Day Streak</p>
            </div>
          </div>

          <div className="bg-card border border-border rounded-xl p-6 flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-zen-lavender flex items-center justify-center">
              <Brain className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-foreground">0</p>
              <p className="text-sm text-muted-foreground">Mood Entries</p>
            </div>
          </div>

          <div className="bg-card border border-border rounded-xl p-6 flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-zen-coral-light flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-zen-coral" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-foreground">0</p>
              <p className="text-sm text-muted-foreground">Exercises Done</p>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Dashboard;
