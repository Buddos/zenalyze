import { useState, useEffect } from "react";
import DashboardLayout from "@/components/dashboard/DashboardLayout";
import MoodPicker from "@/components/dashboard/MoodPicker";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/hooks/use-toast";
import { format } from "date-fns";
import { Plus, Calendar } from "lucide-react";
import type { Tables } from "@/integrations/supabase/types";

type MoodEntry = Tables<"mood_entries">;

const moodEmojis: Record<number, string> = {
  5: "😊",
  4: "😌",
  3: "😐",
  2: "😔",
  1: "😰",
};

const Mood = () => {
  const [entries, setEntries] = useState<MoodEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [selectedMood, setSelectedMood] = useState<{ emoji: string; label: string; value: number } | null>(null);
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);
  const { user } = useAuth();
  const { toast } = useToast();

  useEffect(() => {
    if (user) fetchEntries();
  }, [user]);

  const fetchEntries = async () => {
    try {
      const { data, error } = await supabase
        .from("mood_entries")
        .select("*")
        .eq("user_id", user!.id)
        .order("created_at", { ascending: false });

      if (error) throw error;
      setEntries(data || []);
    } catch (error: any) {
      toast({
        title: "Failed to load entries",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

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
        description: "Your mood has been recorded.",
      });

      setSelectedMood(null);
      setNotes("");
      setShowForm(false);
      fetchEntries();
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
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-serif text-3xl font-semibold text-foreground mb-2">
              Mood Journal
            </h1>
            <p className="text-muted-foreground">
              Track your emotional patterns over time
            </p>
          </div>
          <Button variant="hero" onClick={() => setShowForm(!showForm)}>
            <Plus className="w-4 h-4 mr-2" />
            Log Mood
          </Button>
        </div>

        {/* New Entry Form */}
        {showForm && (
          <div className="bg-card border border-border rounded-2xl p-8 shadow-soft animate-scale-in">
            <h2 className="font-serif text-xl font-semibold text-foreground mb-6 text-center">
              How are you feeling right now?
            </h2>
            <MoodPicker
              onSelect={setSelectedMood}
              selectedMood={selectedMood?.value}
            />
            {selectedMood && (
              <div className="mt-6 space-y-4 animate-fade-in">
                <Textarea
                  placeholder="What's on your mind? (optional)"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="min-h-[100px] resize-none"
                />
                <div className="flex gap-3">
                  <Button variant="outline" onClick={() => setShowForm(false)} className="flex-1">
                    Cancel
                  </Button>
                  <Button variant="hero" onClick={handleSaveMood} disabled={saving} className="flex-1">
                    {saving ? "Saving..." : "Save Entry"}
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Entries List */}
        <div className="space-y-4">
          <h2 className="font-serif text-xl font-semibold text-foreground flex items-center gap-2">
            <Calendar className="w-5 h-5 text-primary" />
            Your History
          </h2>

          {loading ? (
            <div className="text-center py-12 text-muted-foreground">Loading...</div>
          ) : entries.length === 0 ? (
            <div className="text-center py-12 bg-card border border-border rounded-2xl">
              <p className="text-muted-foreground mb-4">No mood entries yet</p>
              <Button variant="calm" onClick={() => setShowForm(true)}>
                Log your first mood
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {entries.map((entry) => (
                <div
                  key={entry.id}
                  className="bg-card border border-border rounded-xl p-5 flex items-start gap-4 hover:shadow-soft transition-shadow"
                >
                  <span className="text-4xl">{moodEmojis[entry.mood_score] || "😐"}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-foreground">{entry.mood_label}</span>
                      <span className="text-sm text-muted-foreground">
                        {format(new Date(entry.created_at), "MMM d, yyyy 'at' h:mm a")}
                      </span>
                    </div>
                    {entry.notes && (
                      <p className="text-muted-foreground text-sm">{entry.notes}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Mood;
