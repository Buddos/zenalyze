import { useState, useEffect } from "react";
import DashboardLayout from "@/components/dashboard/DashboardLayout";
import { Button } from "@/components/ui/button";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";
import { Phone, Globe, Clock, AlertTriangle, Heart } from "lucide-react";
import type { Tables } from "@/integrations/supabase/types";

type CrisisResource = Tables<"crisis_resources">;

const Emergency = () => {
  const [resources, setResources] = useState<CrisisResource[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    fetchResources();
  }, []);

  const fetchResources = async () => {
    try {
      const { data, error } = await supabase
        .from("crisis_resources")
        .select("*")
        .order("country");

      if (error) throw error;
      setResources(data || []);
    } catch (error: any) {
      toast({
        title: "Failed to load resources",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
        {/* Emergency Banner */}
        <div className="bg-destructive/10 border border-destructive/30 rounded-2xl p-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-destructive flex items-center justify-center flex-shrink-0">
              <AlertTriangle className="w-6 h-6 text-destructive-foreground" />
            </div>
            <div>
              <h1 className="font-serif text-2xl font-semibold text-foreground mb-2">
                If you're in immediate danger
              </h1>
              <p className="text-muted-foreground mb-4">
                Please call emergency services (911 in the US) or go to your nearest emergency room.
              </p>
              <Button 
                variant="destructive" 
                size="lg"
                onClick={() => window.open("tel:911")}
              >
                <Phone className="w-4 h-4 mr-2" />
                Call Emergency Services
              </Button>
            </div>
          </div>
        </div>

        {/* Support Message */}
        <div className="bg-zen-coral-light border border-zen-coral/20 rounded-2xl p-6 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-zen-coral flex items-center justify-center flex-shrink-0">
            <Heart className="w-6 h-6 text-foreground" />
          </div>
          <div>
            <h3 className="font-medium text-foreground mb-1">You're not alone</h3>
            <p className="text-sm text-muted-foreground">
              It takes courage to reach out for help. These resources are here to support you 24/7.
            </p>
          </div>
        </div>

        {/* Crisis Resources */}
        <div className="space-y-4">
          <h2 className="font-serif text-xl font-semibold text-foreground">
            Crisis Helplines
          </h2>

          {loading ? (
            <div className="text-center py-12 text-muted-foreground">
              Loading resources...
            </div>
          ) : (
            <div className="space-y-3">
              {resources.map((resource) => (
                <div
                  key={resource.id}
                  className="bg-card border border-border rounded-xl p-5 hover:shadow-soft transition-shadow"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-medium text-foreground">{resource.name}</h3>
                        <span className="text-xs px-2 py-0.5 rounded-full bg-muted">
                          {resource.country}
                        </span>
                        {resource.available_24_7 && (
                          <span className="text-xs px-2 py-0.5 rounded-full bg-zen-sage-light text-zen-sage-dark flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            24/7
                          </span>
                        )}
                      </div>
                      {resource.description && (
                        <p className="text-sm text-muted-foreground mb-3">
                          {resource.description}
                        </p>
                      )}
                      <div className="flex flex-wrap items-center gap-3">
                        {resource.phone_number && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              const phoneNumber = resource.phone_number?.replace(/\D/g, "");
                              if (phoneNumber) window.open(`tel:${phoneNumber}`);
                            }}
                          >
                            <Phone className="w-4 h-4 mr-2" />
                            {resource.phone_number}
                          </Button>
                        )}
                        {resource.website_url && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => window.open(resource.website_url!, "_blank")}
                          >
                            <Globe className="w-4 h-4 mr-2" />
                            Visit Website
                          </Button>
                        )}
                      </div>
                    </div>
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

export default Emergency;
