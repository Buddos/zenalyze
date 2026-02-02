import { useState, useEffect } from "react";
import DashboardLayout from "@/components/dashboard/DashboardLayout";
import { Button } from "@/components/ui/button";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/hooks/use-toast";
import { Calendar, Video, User, Star, Clock } from "lucide-react";
import type { Tables } from "@/integrations/supabase/types";

type Therapist = Tables<"therapists">;

const Therapy = () => {
  const [therapists, setTherapists] = useState<Therapist[]>([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();
  const { toast } = useToast();

  useEffect(() => {
    fetchTherapists();
  }, []);

  const fetchTherapists = async () => {
    try {
      const { data, error } = await supabase
        .from("therapists")
        .select("*")
        .order("name");

      if (error) throw error;
      setTherapists(data || []);
    } catch (error: any) {
      toast({
        title: "Failed to load therapists",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleBook = (therapist: Therapist) => {
    toast({
      title: "Coming soon!",
      description: `Booking with ${therapist.name} will be available soon.`,
    });
  };

  return (
    <DashboardLayout>
      <div className="max-w-5xl mx-auto space-y-8 animate-fade-in">
        {/* Header */}
        <div>
          <h1 className="font-serif text-3xl font-semibold text-foreground mb-2">
            Teletherapy
          </h1>
          <p className="text-muted-foreground">
            Connect with licensed therapists for video sessions
          </p>
        </div>

        {/* Info Banner */}
        <div className="bg-zen-sage-light/50 border border-zen-sage/20 rounded-2xl p-6 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-zen-sage flex items-center justify-center flex-shrink-0">
            <Video className="w-6 h-6 text-primary-foreground" />
          </div>
          <div>
            <h3 className="font-medium text-foreground mb-1">Video Sessions</h3>
            <p className="text-sm text-muted-foreground">
              Book a private video call with a licensed therapist from the comfort of your home.
            </p>
          </div>
        </div>

        {/* Therapist List */}
        <div className="space-y-4">
          <h2 className="font-serif text-xl font-semibold text-foreground">
            Available Therapists
          </h2>

          {loading ? (
            <div className="text-center py-12 text-muted-foreground">
              Loading therapists...
            </div>
          ) : therapists.length === 0 ? (
            <div className="text-center py-12 bg-card border border-border rounded-2xl">
              <User className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground mb-2">No therapists available yet</p>
              <p className="text-sm text-muted-foreground">
                Check back soon for available therapists.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {therapists.map((therapist) => (
                <div
                  key={therapist.id}
                  className="bg-card border border-border rounded-xl p-6 hover:shadow-soft transition-shadow"
                >
                  <div className="flex gap-4 mb-4">
                    <div className="w-16 h-16 rounded-xl bg-zen-lavender flex items-center justify-center flex-shrink-0">
                      <User className="w-8 h-8 text-foreground" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-serif text-lg font-semibold text-foreground">
                        {therapist.name}
                      </h3>
                      <p className="text-sm text-primary">{therapist.specialization}</p>
                    </div>
                  </div>

                  {therapist.bio && (
                    <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                      {therapist.bio}
                    </p>
                  )}

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1 text-sm text-muted-foreground">
                      <Clock className="w-4 h-4" />
                      <span>50 min sessions</span>
                    </div>
                    <Button variant="calm" size="sm" onClick={() => handleBook(therapist)}>
                      <Calendar className="w-4 h-4 mr-2" />
                      Book Session
                    </Button>
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

export default Therapy;
