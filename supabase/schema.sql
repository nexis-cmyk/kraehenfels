-- Krähenfels live audio review
-- The client only uses the publishable key. Row-level security keeps each
-- signed-in review private to its owner.

create table if not exists public.audio_ratings (
  user_id uuid not null references auth.users(id) on delete cascade,
  cue_id text not null,
  rating smallint not null check (rating in (-1, 1)),
  client text not null default 'unknown',
  app_version text,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now()),
  primary key (user_id, cue_id)
);

create index if not exists audio_ratings_cue_id_idx
  on public.audio_ratings (cue_id);

alter table public.audio_ratings enable row level security;

drop policy if exists "audio_ratings_select_own" on public.audio_ratings;
create policy "audio_ratings_select_own"
  on public.audio_ratings for select to authenticated
  using ((select auth.uid()) = user_id);

drop policy if exists "audio_ratings_insert_own" on public.audio_ratings;
create policy "audio_ratings_insert_own"
  on public.audio_ratings for insert to authenticated
  with check ((select auth.uid()) = user_id);

drop policy if exists "audio_ratings_update_own" on public.audio_ratings;
create policy "audio_ratings_update_own"
  on public.audio_ratings for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

drop policy if exists "audio_ratings_delete_own" on public.audio_ratings;
create policy "audio_ratings_delete_own"
  on public.audio_ratings for delete to authenticated
  using ((select auth.uid()) = user_id);

create or replace function public.set_audio_ratings_updated_at()
returns trigger
language plpgsql
security invoker
set search_path = public
as $$
begin
  new.updated_at = timezone('utc', now());
  return new;
end;
$$;

drop trigger if exists audio_ratings_set_updated_at on public.audio_ratings;
create trigger audio_ratings_set_updated_at
before update on public.audio_ratings
for each row execute function public.set_audio_ratings_updated_at();

do $$
begin
  if not exists (
    select 1
    from pg_publication_tables
    where pubname = 'supabase_realtime'
      and schemaname = 'public'
      and tablename = 'audio_ratings'
  ) then
    alter publication supabase_realtime add table public.audio_ratings;
  end if;
end
$$;
