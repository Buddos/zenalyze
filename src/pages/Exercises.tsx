import { useState, useEffect } from "react";
import DashboardLayout from "@/components/dashboard/DashboardLayout";
import { Button } from "@/components/ui/button";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/hooks/use-toast";
import { Wind, Brain, Heart, Clock, Play, CheckCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Tables } from "@/integrations/supabase/types";

type Exercise = Tables<"exercises">;

const categoryIcons: Record<string, typeof Wind> = {
  breathing: Wind,
  meditation: Brain,
  cbt: Heart,
};

const categoryColors: Record<string, string> = {
  breathing: "from-zen-sky to-zen-sage",
  meditation: "from-zen-lavender to-zen-sage",
  cbt: "from-zen-coral to-zen-lavender",
};

const Exercises = () => {
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeExercise, setActiveExercise] = useState<Exercise | null>(null);
  const [filter, setFilter] = useState<string>("all");
  const { user } = useAuth();
  const { toast } = useToast();

  useEffect(() => {
    fetchExercises();
  }, []);

  const fetchExercises = async () => {
    try {
      const { data, error } = await supabase
        .from("exercises")
        .select("*")
        .order("created_at");

      if (error) throw error;
      setExercises(data || []);
    } catch (error: any) {
      toast({
        title: "Failed to load exercises",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = async (exercise: Exercise) => {
    if (!user) return;

    try {
      const { error } = await supabase.from("user_exercise_sessions").insert({
        user_id: user.id,
        exercise_id: exercise.id,
        duration_seconds: exercise.duration_minutes * 60,
      });

      if (error) throw error;

      toast({
        title: "Exercise completed!",
        description: "Great job taking care of your mental health.",
      });

      setActiveExercise(null);
    } catch (error: any) {
      toast({
        title: "Failed to log session",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  const filteredExercises = filter === "all" 
    ? exercises 
    : exercises.filter(e => e.category === filter);

  const categories = ["all", "breathing", "meditation", "cbt"];

  return (
    <DashboardLayout>
      <div className="max-w-5xl mx-auto space-y-8 animate-fade-in">
        {/* Header */}
        <div>
          <h1 className="font-serif text-3xl font-semibold text-foreground mb-2">
            Mental Health Exercises
          </h1>
          <p className="text-muted-foreground">
            Practice mindfulness, breathing, and CBT techniques
          </p>
        </div>

        {/* Category Filter */}
        <div className="flex gap-2 flex-wrap">
          {categories.map((cat) => (
            <Button
              key={cat}
              variant={filter === cat ? "default" : "outline"}
              size="sm"
              onClick={() => setFilter(cat)}
              className="capitalize"
            >
              {cat === "cbt" ? "CBT" : cat}
            </Button>
          ))}
        </div>

        {/* Active Exercise Player */}
        {activeExercise && (
          <div className="bg-card border border-border rounded-2xl p-8 shadow-card animate-scale-in">
            <div className="text-center mb-8">
              <h2 className="font-serif text-2xl font-semibold text-foreground mb-2">
                {activeExercise.title}
              </h2>
              <p className="text-muted-foreground">{activeExercise.description}</p>
            </div>

            {/* Instructions */}
            <div className="bg-muted/50 rounded-xl p-6 mb-8">
              <h3 className="font-medium text-foreground mb-4">Instructions:</h3>
              <ol className="space-y-3">
                {activeExercise.instructions?.map((step, idx) => (
                  <li key={idx} className="flex gap-3 text-muted-foreground">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/10 text-primary text-sm flex items-center justify-center font-medium">
                      {idx + 1}
                    </span>
                    {step}
                  </li>
                ))}
              </ol>
            </div>

            <div className="flex gap-3">
              <Button variant="outline" onClick={() => setActiveExercise(null)} className="flex-1">
                Cancel
              </Button>
              <Button variant="hero" onClick={() => handleComplete(activeExercise)} className="flex-1">
                <CheckCircle className="w-4 h-4 mr-2" />
                Mark Complete
              </Button>
            </div>
          </div>
        )}

        {/* Exercise Grid */}
        {!activeExercise && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {loading ? (
              <div className="col-span-full text-center py-12 text-muted-foreground">
                Loading exercises...
              </div>
            ) : filteredExercises.length === 0 ? (
              <div className="col-span-full text-center py-12 text-muted-foreground">
                No exercises found
              </div>
            ) : (
              filteredExercises.map((exercise) => {
                const Icon = categoryIcons[exercise.category] || Wind;
                const gradient = categoryColors[exercise.category] || "from-zen-sage to-zen-sky";
                
                return (
                  <div
                    key={exercise.id}
                    className="group bg-card border border-border rounded-xl p-6 hover:shadow-card transition-all cursor-pointer"
                    onClick={() => setActiveExercise(exercise)}
                  >
                    <div className={cn(
                      "w-12 h-12 rounded-xl bg-gradient-to-br flex items-center justify-center mb-4 group-hover:scale-110 transition-transform",
                      gradient
                    )}>
                      <Icon className="w-6 h-6 text-primary-foreground" />
                    </div>
                    
                    <h3 className="font-serif text-lg font-semibold text-foreground mb-2">
                      {exercise.title}
                    </h3>
                    <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                      {exercise.description}
                    </p>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1 text-sm text-muted-foreground">
                        <Clock className="w-4 h-4" />
                        {exercise.duration_minutes} min
                      </div>
                      <span className="text-xs px-2 py-1 rounded-full bg-muted capitalize">
                        {exercise.difficulty}
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default Exercises;
