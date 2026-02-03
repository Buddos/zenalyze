import { createClient } from '@supabase/supabase-js';
import type { Database } from './types';

// Fallback values for development
const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL || 'https://dummy.supabase.co';
const SUPABASE_PUBLISHABLE_KEY = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY || 'dummy-key';

console.log('Supabase URL:', SUPABASE_URL ? 'Set' : 'Not set');

export const supabase = createClient<Database>(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, {
  auth: {
    storage: localStorage,
    persistSession: true,
    autoRefreshToken: true,
  }
});
