export type RoundId = "R32" | "R16" | "QF" | "SF" | "F";

export type Slot =
  | {
      slot_type: "team";
      team_id: string;
      source_match_id?: never;
      label?: string;
    }
  | {
      slot_type: "winner_of";
      source_match_id: string;
      team_id?: never;
      label?: string;
    }
  | {
      slot_type: "empty";
      team_id?: never;
      source_match_id?: never;
      label?: string;
    };

export interface Team {
  team_id: string;
  display_name: string;
  short_name: string;
  rating: number;
  rating_source: string;
  flag_mode: string;
  flag_value: string;
  fifa_code?: string;
  iso_alpha2?: string;
  iso_alpha3?: string;
  confederation?: string;
  notes?: string;
}

export interface Round {
  round_id: RoundId;
  display_name: string;
  display_order: number;
}

export interface Match {
  match_id: string;
  round_id: RoundId;
  slot_a: Slot;
  slot_b: Slot;
  feeds_to_match_id: string | null;
  feeds_to_slot: "A" | "B" | null;
  display_order: number;
}

export interface TournamentData {
  schema_version: string;
  tournament: {
    tournament_id: string;
    display_name: string;
    stage: string;
    starts_at_round: RoundId;
    generated_at: string;
    data_version: string;
    data_note?: string;
  };
  sources: Array<{
    source_id: string;
    display_name: string;
    source_type: string;
    url: string;
    license_note?: string;
    retrieval_method?: string;
    notes?: string;
  }>;
  teams: Team[];
  rounds: Round[];
  matches: Match[];
  models: {
    default_model_id: string;
    available_models: Array<{
      model_id: string;
      display_name: string;
      model_version: string;
      probability_method: string;
      is_available: boolean;
    }>;
    rating_source: string;
    rating_snapshot_date: string;
    rating_snapshot_kind: string;
  };
}

export type SelectionSource = "model" | "user_override" | "official_lock" | "unresolved";

export interface UserOverride {
  match_id: string;
  winner_team_id: string;
}

export interface RuntimeMatch {
  match_id: string;
  round_id: RoundId;
  team_a_id: string | null;
  team_b_id: string | null;
  selected_model_id: string;
  probability_a: number | null;
  probability_b: number | null;
  winner_team_id: string | null;
  selection_source: SelectionSource;
  is_locked: boolean;
  is_overridden: boolean;
}

export interface ForecastResult {
  selected_model_id: string;
  matches: RuntimeMatch[];
  matchesById: Map<string, RuntimeMatch>;
  appliedOverrides: UserOverride[];
  ignoredOverrides: UserOverride[];
}

export interface ChampionProbability {
  team_id: string;
  champion_probability: number;
  final_probability: number;
  semifinal_probability: number;
  quarterfinal_probability: number;
  round_of_16_probability: number;
  selected_model_id: string;
}
