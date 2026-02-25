"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { useSession } from "@/lib/session";

// Fallback mock data when backend is unreachable or no user session
const FALLBACK = {
    wallet: { virtual_balance_fcfa: 47500, confirmed_balance_fcfa: 35000, pending_settlement_fcfa: 12500, total_saved_fcfa: 127000, current_streak_days: 34 },
    score: { trust_score: 562, tier_label: "Confirmé", max_loan_fcfa: 15000 },
    triggers: [
        { id: "1", team_name: "Arsenal", event_type: "WIN", amount_fcfa: 1000, times_triggered: 12, total_saved_fcfa: 12000, status: "ACTIVE" },
    ],
    history: [
        { trigger_event: "Arsenal WIN vs Chelsea", amount_fcfa: 1000, created_at: "Aujourd'hui" },
        { trigger_event: "Arsenal GOAL (Saka)", amount_fcfa: 500, created_at: "Aujourd'hui" },
    ],
};

export default function DashboardPage() {
    const { session } = useSession();
    const [loading, setLoading] = useState(true);
    const [wallet, setWallet] = useState(FALLBACK.wallet);
    const [score, setScore] = useState(FALLBACK.score);
    const [triggers, setTriggers] = useState(FALLBACK.triggers);
    const [history, setHistory] = useState(FALLBACK.history);
    const [displayName, setDisplayName] = useState("Utilisateur");
    const [referralCode, setReferralCode] = useState("SCORAI42");
    const [animBalance, setAnimBalance] = useState(0);

    useEffect(() => {
        const load = async () => {
            if (!session.userId) { setLoading(false); return; }
            setDisplayName(session.displayName || "Utilisateur");
            setReferralCode(session.referralCode || "SCORAI42");
            try {
                const [w, s, t, h] = await Promise.all([
                    api.getBalance(session.userId),
                    api.getScore(session.userId).catch(() => FALLBACK.score),
                    api.getMyTriggers(session.userId).catch(() => FALLBACK.triggers),
                    api.getHistory(session.userId).catch(() => FALLBACK.history),
                ]);
                setWallet(w as typeof wallet);
                setScore(s as typeof score);
                setTriggers(t as typeof triggers);
                setHistory(h as typeof history);
            } catch {
                // Fallback already set
            }
            setLoading(false);
        };
        load();
    }, [session.userId]);

    // Animated counter
    useEffect(() => {
        const target = wallet.virtual_balance_fcfa;
        let cur = 0;
        const step = target / 35;
        const t = setInterval(() => {
            cur += step;
            if (cur >= target) { setAnimBalance(target); clearInterval(t); }
            else setAnimBalance(Math.floor(cur));
        }, 20);
        return () => clearInterval(t);
    }, [wallet.virtual_balance_fcfa]);

    if (loading) {
        return (
            <main className="container" style={{ paddingTop: "4rem", textAlign: "center" }}>
                <div className="animate-fade-in text-dim" style={{ fontSize: "1.1rem" }}>Chargement...</div>
            </main>
        );
    }

    return (
        <main className="container" style={{ paddingBottom: "7rem", paddingTop: "1.75rem" }}>
            {/* Header */}
            <div className="flex-between animate-fade-in" style={{ marginBottom: "1.75rem" }}>
                <div>
                    <p className="text-dim" style={{ fontSize: "0.85rem", fontWeight: 500 }}>Bonjour,</p>
                    <h2 style={{ fontSize: "1.6rem" }}>{displayName} 👋</h2>
                </div>
                <div className="stat-pill" style={{ background: "rgba(245,158,11,0.1)", color: "var(--scorai-gold)" }}>
                    🔥 {wallet.current_streak_days}j
                </div>
            </div>

            {/* Balance Card */}
            <div className="hero-glass animate-scale-in" style={{ padding: "2rem 1.75rem", textAlign: "center", marginBottom: "1rem" }}>
                <p className="text-dim" style={{ fontSize: "0.85rem", fontWeight: 500, marginBottom: "0.5rem" }}>Solde Virtuel</p>
                <div style={{ fontSize: "3.25rem", fontWeight: 800, letterSpacing: "-0.04em", lineHeight: 1 }}>
                    {animBalance.toLocaleString("fr-FR")}
                </div>
                <div className="text-light" style={{ fontWeight: 600, fontSize: "1rem", marginTop: "0.15rem" }}>FCFA</div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "0.5rem", marginTop: "1.75rem", paddingTop: "1.25rem", borderTop: "1px solid rgba(0,0,0,0.05)" }}>
                    <div>
                        <div className="text-dim" style={{ fontSize: "0.7rem", fontWeight: 500 }}>Confirmé</div>
                        <div className="text-emerald" style={{ fontWeight: 700, fontSize: "1rem" }}>{wallet.confirmed_balance_fcfa.toLocaleString()}</div>
                    </div>
                    <div>
                        <div className="text-dim" style={{ fontSize: "0.7rem", fontWeight: 500 }}>En attente</div>
                        <div className="text-gold" style={{ fontWeight: 700, fontSize: "1rem" }}>{wallet.pending_settlement_fcfa.toLocaleString()}</div>
                    </div>
                    <div>
                        <div className="text-dim" style={{ fontSize: "0.7rem", fontWeight: 500 }}>Total</div>
                        <div style={{ fontWeight: 700, fontSize: "1rem" }}>{wallet.total_saved_fcfa.toLocaleString()}</div>
                    </div>
                </div>
            </div>

            {/* Trust Score */}
            <div className="card animate-slide-up stagger-1" style={{ marginBottom: "1rem" }}>
                <div className="flex-between">
                    <div>
                        <p className="text-dim" style={{ fontSize: "0.8rem", fontWeight: 500 }}>ScorAI Trust Index</p>
                        <div style={{ display: "flex", alignItems: "baseline", gap: "0.35rem", marginTop: "0.2rem" }}>
                            <span style={{ fontSize: "2rem", fontWeight: 800 }}>{score.trust_score}</span>
                            <span className="text-light" style={{ fontSize: "0.85rem" }}>/ 1000</span>
                        </div>
                    </div>
                    <div className="stat-pill" style={{ background: "rgba(16,185,129,0.1)", color: "var(--scorai-emerald)" }}>
                        {score.tier_label}
                    </div>
                </div>
                <div className="progress-bar" style={{ marginTop: "1rem" }}>
                    <div className="fill fill-emerald" style={{ width: `${(score.trust_score / 1000) * 100}%` }} />
                </div>
                <Link href="/credit" className="btn btn-primary" style={{ width: "100%", marginTop: "1rem", padding: "0.85rem" }}>
                    💳 Options de crédit
                </Link>
            </div>

            {/* Active Triggers */}
            <div className="animate-slide-up stagger-2" style={{ marginBottom: "1.25rem" }}>
                <div className="flex-between" style={{ marginBottom: "0.75rem" }}>
                    <h3>Triggers actifs</h3>
                    <Link href="/triggers" className="text-blue" style={{ fontSize: "0.85rem", fontWeight: 600, textDecoration: "none" }}>Gérer →</Link>
                </div>
                <div className="grid-2">
                    {triggers.slice(0, 4).map(t => (
                        <div key={t.id} className="card" style={{ padding: "1rem" }}>
                            <div className="flex-between" style={{ marginBottom: "0.5rem" }}>
                                <span style={{ fontWeight: 600, fontSize: "0.9rem" }}>{t.team_name}</span>
                                <div style={{ width: "8px", height: "8px", borderRadius: "50%", background: t.status === "ACTIVE" ? "var(--scorai-emerald)" : "var(--scorai-text-light)" }} />
                            </div>
                            <div className="text-dim" style={{ fontSize: "0.8rem" }}>{t.event_type}</div>
                            <div style={{ fontWeight: 700, marginTop: "0.35rem" }}>{t.amount_fcfa.toLocaleString()} <span className="text-dim" style={{ fontWeight: 500, fontSize: "0.75rem" }}>FCFA</span></div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Recent Activity */}
            <div className="animate-slide-up stagger-3">
                <h3 style={{ marginBottom: "0.75rem" }}>Activité récente</h3>
                <div className="stack" style={{ gap: "0.4rem" }}>
                    {history.slice(0, 5).map((r, i) => (
                        <div key={i} className="selectable-item" style={{ cursor: "default", padding: "0.85rem 1rem" }}>
                            <div style={{ flex: 1 }}>
                                <div style={{ fontWeight: 600, fontSize: "0.9rem" }}>{r.trigger_event}</div>
                                <div className="text-dim" style={{ fontSize: "0.75rem", marginTop: "0.1rem" }}>{r.created_at}</div>
                            </div>
                            <span className="text-emerald" style={{ fontWeight: 700, fontSize: "0.95rem" }}>+{r.amount_fcfa.toLocaleString()}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Referral */}
            <div className="card animate-slide-up stagger-4" style={{ marginTop: "1.25rem", textAlign: "center" }}>
                <p style={{ fontWeight: 600, marginBottom: "0.5rem" }}>🎁 Invite tes amis</p>
                <p className="text-dim" style={{ fontSize: "0.85rem", marginBottom: "0.75rem" }}>Gagnez 500 FCFA chacun!</p>
                <div style={{ padding: "0.65rem 1rem", background: "#f1f5f9", borderRadius: "var(--scorai-radius-sm)", fontFamily: "monospace", fontSize: "1.1rem", fontWeight: 700, letterSpacing: "2px" }}>
                    {referralCode}
                </div>
            </div>
        </main>
    );
}
