import { SUPABASE_CONFIG } from "./supabase-config.js";

const SUPABASE_JS_URL = "https://esm.sh/@supabase/supabase-js@2.57.4";

function redirectURL() {
  return `${window.location.origin}${window.location.pathname}`;
}

export class SupabaseSync {
  constructor(onChange) {
    this.onChange = onChange;
    this.client = null;
    this.session = null;
    this.ratings = {};
    this.status = "starting";
    this.error = "";
    this.channel = null;
    this.authSubscription = null;
  }

  snapshot() {
    return {
      status: this.status,
      error: this.error,
      session: this.session,
      ratings: { ...this.ratings },
      online: navigator.onLine,
    };
  }

  emit() {
    this.onChange(this.snapshot());
  }

  async init() {
    try {
      const { createClient } = await import(SUPABASE_JS_URL);
      this.client = createClient(SUPABASE_CONFIG.url, SUPABASE_CONFIG.publishableKey, {
        auth: {
          persistSession: true,
          autoRefreshToken: true,
          detectSessionInUrl: true,
        },
      });

      const { data, error } = await this.client.auth.getSession();
      if (error) throw error;
      this.session = data.session;
      this.status = this.session ? "connected" : "signed-out";
      this.error = "";
      const authState = this.client.auth.onAuthStateChange((_event, session) => {
        this.session = session;
        this.status = session ? "connected" : "signed-out";
        this.error = "";
        this.subscribeToRatings();
        this.emit();
        if (session) void this.refreshRatings();
      });
      this.authSubscription = authState?.data?.subscription || authState?.subscription || authState;
      this.subscribeToRatings();
      await this.refreshRatings();
      this.emit();
    } catch (error) {
      this.status = "unavailable";
      this.error = error?.message || "Supabase ist gerade nicht erreichbar.";
      this.emit();
    }
  }

  subscribeToRatings() {
    if (!this.client || !this.session) {
      if (this.channel) void this.client?.removeChannel(this.channel);
      this.channel = null;
      return;
    }
    if (this.channel) void this.client.removeChannel(this.channel);
    this.channel = this.client
      .channel(`audio-ratings-${this.session.user.id}`)
      .on(
        "postgres_changes",
        {
          event: "*",
          schema: "public",
          table: "audio_ratings",
          filter: `user_id=eq.${this.session.user.id}`,
        },
        (payload) => {
          const row = payload.eventType === "DELETE" ? payload.old : payload.new;
          if (!row?.cue_id) return;
          if (payload.eventType === "DELETE") delete this.ratings[row.cue_id];
          else this.ratings[row.cue_id] = Number(row.rating);
          this.emit();
        },
      )
      .subscribe();
  }

  async refreshRatings() {
    if (!this.client || !this.session) {
      this.ratings = {};
      this.emit();
      return this.ratings;
    }
    const { data, error } = await this.client
      .from("audio_ratings")
      .select("cue_id,rating")
      .order("updated_at", { ascending: false });
    if (error) {
      this.status = "error";
      this.error = error.message;
      this.emit();
      return this.ratings;
    }
    this.ratings = Object.fromEntries((data || []).map((row) => [row.cue_id, Number(row.rating)]));
    this.status = "connected";
    this.error = "";
    this.emit();
    return this.ratings;
  }

  async pushLocalRatings(localRatings, remoteRatings = this.ratings) {
    if (!this.client || !this.session) return;
    const pending = Object.entries(localRatings).filter(([cueID]) => remoteRatings[cueID] == null);
    for (const [cueID, rating] of pending) await this.setRating(cueID, rating);
  }

  async setRating(cueID, rating, appVersion = "3.3.0") {
    this.ratings[cueID] = Number(rating);
    this.emit();
    if (!this.client || !this.session) return false;
    const { error } = await this.client.from("audio_ratings").upsert(
      {
        user_id: this.session.user.id,
        cue_id: cueID,
        rating: Number(rating),
        client: "web",
        app_version: appVersion,
      },
      { onConflict: "user_id,cue_id" },
    );
    if (error) {
      this.status = "error";
      this.error = error.message;
      this.emit();
      return false;
    }
    return true;
  }

  async clearRatings() {
    this.ratings = {};
    this.emit();
    if (!this.client || !this.session) return false;
    const { error } = await this.client.from("audio_ratings").delete().eq("user_id", this.session.user.id);
    if (error) {
      this.status = "error";
      this.error = error.message;
      this.emit();
      return false;
    }
    return true;
  }

  async signInWithGoogle() {
    if (!this.client) {
      this.error = "Die Cloud-Verbindung ist noch nicht bereit.";
      this.status = "error";
      this.emit();
      return;
    }
    const { error } = await this.client.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: redirectURL() },
    });
    if (error) {
      this.status = "error";
      this.error = error.message;
      this.emit();
    }
  }

  async signOut() {
    if (!this.client) return;
    const { error } = await this.client.auth.signOut();
    if (error) {
      this.status = "error";
      this.error = error.message;
      this.emit();
    }
  }

  dispose() {
    this.authSubscription?.unsubscribe?.();
    if (this.client && this.channel) void this.client.removeChannel(this.channel);
    this.channel = null;
  }
}
