/**
 * ScorAI — API Client
 * Centralized client for all backend API calls.
 * All pages use this to connect to the FastAPI backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: "Erreur serveur" }));
    throw new Error(err.detail || err.message || `Erreur ${res.status}`);
  }
  return res.json();
}

// ============================================================
// Auth
// ============================================================
export const api = {
  signup: (data: { phone_number: string; display_name: string; favorite_team_id?: number; favorite_team_name?: string; referral_code?: string }) =>
    request<{ user_id: string; referral_code: string; message: string }>("/auth/signup", { method: "POST", body: JSON.stringify(data) }),

  getUser: (userId: string) =>
    request<Record<string, unknown>>(`/auth/user/${userId}`),

  submitKYC: (data: { user_id: string; full_name: string; date_of_birth: string; national_id_number: string }) =>
    request<{ kyc_id: string; status: string; message: string }>("/auth/kyc", { method: "POST", body: JSON.stringify(data) }),

  // ============================================================
  // Wallet
  // ============================================================
  getBalance: (userId: string) =>
    request<{
      user_id: string;
      virtual_balance_fcfa: number;
      confirmed_balance_fcfa: number;
      pending_settlement_fcfa: number;
      total_saved_fcfa: number;
      current_streak_days: number;
      longest_streak_days: number;
    }>(`/wallet/balance/${userId}`),

  getHistory: (userId: string) =>
    request<Array<{
      id: string;
      amount_fcfa: number;
      trigger_event: string;
      status: string;
      created_at: string;
    }>>(`/wallet/history/${userId}`),

  getBatchStatus: (userId: string) =>
    request<Record<string, unknown>>(`/wallet/batch-status/${userId}`),

  // ============================================================
  // Triggers
  // ============================================================
  createTrigger: (data: { user_id: string; team_id: number; team_name: string; event_type: string; amount_fcfa: number }) =>
    request<Record<string, unknown>>("/triggers/create", { method: "POST", body: JSON.stringify(data) }),

  getMyTriggers: (userId: string) =>
    request<Array<{
      id: string;
      team_id: number;
      team_name: string;
      event_type: string;
      amount_fcfa: number;
      status: string;
      times_triggered: number;
      total_saved_fcfa: number;
    }>>(`/triggers/mine/${userId}`),

  getTeams: () =>
    request<Array<{ id: number; name: string; league: string; country: string }>>("/triggers/teams"),

  pauseTrigger: (triggerId: string, userId: string) =>
    request<Record<string, unknown>>(`/triggers/pause/${triggerId}?user_id=${userId}`, { method: "PUT" }),

  deleteTrigger: (triggerId: string, userId: string) =>
    request<Record<string, unknown>>(`/triggers/${triggerId}?user_id=${userId}`, { method: "DELETE" }),

  // ============================================================
  // Score
  // ============================================================
  getScore: (userId: string) =>
    request<{
      user_id: string;
      trust_score: number;
      tier: string;
      tier_label: string;
      max_loan_fcfa: number;
      explanations: Array<{
        feature: string;
        impact: number;
        direction: string;
        description: string;
      }>;
    }>(`/score/${userId}`),

  // ============================================================
  // Loans
  // ============================================================
  applyForLoan: (data: { user_id: string; amount_fcfa: number }) =>
    request<{
      approved: boolean;
      loan_id?: string;
      amount_fcfa?: number;
      total_due?: number;
      interest_fcfa?: number;
      reason?: string;
      message?: string;
    }>("/loans/apply", { method: "POST", body: JSON.stringify(data) }),

  getLoanStatus: (loanId: string) =>
    request<Record<string, unknown>>(`/loans/status/${loanId}`),

  getUserLoans: (userId: string) =>
    request<Array<Record<string, unknown>>>(`/loans/user/${userId}`),

  repayLoan: (data: { loan_id: string; amount_fcfa: number }) =>
    request<Record<string, unknown>>("/loans/repay", { method: "POST", body: JSON.stringify(data) }),

  // ============================================================
  // Analytics
  // ============================================================
  getDashboard: () =>
    request<Record<string, unknown>>("/analytics/dashboard"),

  getLeaderboard: () =>
    request<Array<{
      rank: number;
      display_name: string;
      team: string;
      total_saved_fcfa: number;
      streak_days: number;
    }>>("/analytics/leaderboard"),
};
