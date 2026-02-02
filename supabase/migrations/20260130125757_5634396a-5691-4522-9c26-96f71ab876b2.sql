-- Create profiles table for user data
CREATE TABLE public.profiles (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
  display_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create mood_entries table
CREATE TABLE public.mood_entries (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  mood_score INTEGER NOT NULL CHECK (mood_score >= 1 AND mood_score <= 5),
  mood_label TEXT NOT NULL,
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create exercises table
CREATE TABLE public.exercises (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  category TEXT NOT NULL, -- 'meditation', 'breathing', 'cbt'
  duration_minutes INTEGER NOT NULL DEFAULT 5,
  difficulty TEXT NOT NULL DEFAULT 'beginner',
  instructions TEXT[],
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create user_exercise_sessions table
CREATE TABLE public.user_exercise_sessions (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  exercise_id UUID NOT NULL REFERENCES public.exercises(id) ON DELETE CASCADE,
  completed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  duration_seconds INTEGER,
  notes TEXT
);

-- Create ai_chat_sessions table
CREATE TABLE public.ai_chat_sessions (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  messages JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create therapists table
CREATE TABLE public.therapists (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  specialization TEXT NOT NULL,
  bio TEXT,
  avatar_url TEXT,
  available_slots JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create therapy_sessions table
CREATE TABLE public.therapy_sessions (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  therapist_id UUID NOT NULL REFERENCES public.therapists(id) ON DELETE CASCADE,
  scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
  status TEXT NOT NULL DEFAULT 'scheduled', -- 'scheduled', 'completed', 'cancelled'
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create crisis_resources table
CREATE TABLE public.crisis_resources (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  phone_number TEXT,
  website_url TEXT,
  country TEXT NOT NULL DEFAULT 'Global',
  available_24_7 BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mood_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.exercises ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_exercise_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.therapists ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.therapy_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.crisis_resources ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Users can view their own profile"
  ON public.profiles FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own profile"
  ON public.profiles FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own profile"
  ON public.profiles FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Mood entries policies
CREATE POLICY "Users can view their own mood entries"
  ON public.mood_entries FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own mood entries"
  ON public.mood_entries FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own mood entries"
  ON public.mood_entries FOR DELETE
  USING (auth.uid() = user_id);

-- Exercises policies (public read)
CREATE POLICY "Anyone can view exercises"
  ON public.exercises FOR SELECT
  USING (true);

-- User exercise sessions policies
CREATE POLICY "Users can view their own exercise sessions"
  ON public.user_exercise_sessions FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own exercise sessions"
  ON public.user_exercise_sessions FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- AI chat sessions policies
CREATE POLICY "Users can view their own chat sessions"
  ON public.ai_chat_sessions FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own chat sessions"
  ON public.ai_chat_sessions FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own chat sessions"
  ON public.ai_chat_sessions FOR UPDATE
  USING (auth.uid() = user_id);

-- Therapists policies (public read)
CREATE POLICY "Anyone can view therapists"
  ON public.therapists FOR SELECT
  USING (true);

-- Therapy sessions policies
CREATE POLICY "Users can view their own therapy sessions"
  ON public.therapy_sessions FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own therapy sessions"
  ON public.therapy_sessions FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own therapy sessions"
  ON public.therapy_sessions FOR UPDATE
  USING (auth.uid() = user_id);

-- Crisis resources policies (public read)
CREATE POLICY "Anyone can view crisis resources"
  ON public.crisis_resources FOR SELECT
  USING (true);

-- Create trigger function for updating timestamps
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SET search_path = public;

-- Create triggers for updated_at
CREATE TRIGGER update_profiles_updated_at
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_ai_chat_sessions_updated_at
  BEFORE UPDATE ON public.ai_chat_sessions
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- Create trigger to auto-create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (user_id)
  VALUES (NEW.id);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- Insert default exercises
INSERT INTO public.exercises (title, description, category, duration_minutes, difficulty, instructions) VALUES
('Deep Breathing', 'A simple breathing exercise to calm your mind and reduce stress.', 'breathing', 5, 'beginner', ARRAY['Find a comfortable position', 'Breathe in slowly for 4 seconds', 'Hold for 4 seconds', 'Exhale slowly for 4 seconds', 'Repeat 5-10 times']),
('Body Scan Meditation', 'A mindfulness practice to increase body awareness and relaxation.', 'meditation', 10, 'beginner', ARRAY['Lie down comfortably', 'Close your eyes', 'Focus on your toes, notice any sensations', 'Slowly move attention up through your body', 'End at the top of your head']),
('4-7-8 Breathing', 'A breathing technique that promotes relaxation and sleep.', 'breathing', 5, 'beginner', ARRAY['Exhale completely', 'Inhale through nose for 4 seconds', 'Hold breath for 7 seconds', 'Exhale through mouth for 8 seconds', 'Repeat 3-4 times']),
('Loving-Kindness Meditation', 'A meditation to cultivate compassion for yourself and others.', 'meditation', 15, 'intermediate', ARRAY['Sit comfortably and close your eyes', 'Think of yourself and repeat: May I be happy, may I be healthy', 'Think of a loved one and extend the same wishes', 'Extend to acquaintances, then to all beings']),
('Cognitive Restructuring', 'A CBT technique to challenge negative thought patterns.', 'cbt', 10, 'intermediate', ARRAY['Identify a negative thought', 'Ask: What evidence supports this?', 'Ask: What evidence contradicts this?', 'Create a balanced, realistic thought', 'Notice how your feelings change']),
('Grounding Exercise', 'A technique to help you feel present and reduce anxiety.', 'cbt', 5, 'beginner', ARRAY['Name 5 things you can see', 'Name 4 things you can touch', 'Name 3 things you can hear', 'Name 2 things you can smell', 'Name 1 thing you can taste']);

-- Insert default crisis resources
INSERT INTO public.crisis_resources (name, description, phone_number, website_url, country, available_24_7) VALUES
('National Suicide Prevention Lifeline', 'Free, confidential support for people in distress', '988', 'https://988lifeline.org', 'USA', true),
('Crisis Text Line', 'Text-based crisis support', 'Text HOME to 741741', 'https://www.crisistextline.org', 'USA', true),
('SAMHSA National Helpline', 'Treatment referral service for mental health and substance use', '1-800-662-4357', 'https://www.samhsa.gov/find-help/national-helpline', 'USA', true),
('International Association for Suicide Prevention', 'Global network of crisis centers', NULL, 'https://www.iasp.info/resources/Crisis_Centres/', 'Global', true),
('Samaritans', 'Emotional support for anyone in distress', '116 123', 'https://www.samaritans.org', 'UK', true),
('Lifeline Australia', 'Crisis support and suicide prevention', '13 11 14', 'https://www.lifeline.org.au', 'Australia', true);