"use client";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { useSession } from "@/lib/session";

const TEAM_LOGOS: Record<string, string> = { Arsenal: "🔴", "Man City": "🔵", PSG: "🔵🔴", "Real Madrid": "⚪", Liverpool: "🔴", "Coton Sport": "🟢", "Canon Ydé": "🟡", Barcelona: "🔴🔵", Bayern: "🔴" };

interface LeaderboardEntry {
    rank: number;
    display_name: string;
    team: string;
    total_saved_fcfa: number;
    streak_days: number;
}

const FALLBACK: LeaderboardEntry[] = [
    { rank: 1, display_name: "Patrice M.", team: "Arsenal", total_saved_fcfa: 285000, streak_days: 67 },
    { rank: 2, display_name: "Marie A.", team: "PSG", total_saved_fcfa: 231500, streak_days: 45 },
    { rank: 3, display_name: "Samuel E.", team: "Barcelona", total_saved_fcfa: 198000, streak_days: 52 },
    { rank: 4, display_name: "Cédric N.", team: "Real Madrid", total_saved_fcfa: 175000, streak_days: 38 },
    { rank: 5, display_name: "Jean-Pierre K.", team: "Arsenal", total_saved_fcfa: 127000, streak_days: 34 },
];

export default function LeaderboardPage() {
    const { session } = useSession();
    const [entries, setEntries] = useState<LeaderboardEntry[]>(FALLBACK);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const load = async () => {
            try {
                const data = await api.getLeaderboard();
                if (data.length > 0) setEntries(data);
            } catch {
                // Use fallback
            }
            setLoading(false);
        };
        load();
    }, []);

    const top3 = entries.slice(0, 3);
    const rest = entries.slice(3);

    const isSelf = (name: string) => {
        if (!session.displayName) return false;
        return name.toLowerCase().includes(session.displayName.toLowerCase().slice(0, 4));
    };

    if (loading) {
        return <main className="container" style={{ paddingTop: "4rem", textAlign: "center" }}><div className="animate-fade-in text-dim">Chargement...</div></main>;
    }

    return (
        <main className="container" style={{ paddingBottom: "7rem", paddingTop: "1.75rem" }}>
            <h1 style={{ marginBottom: "0.25rem" }}>Classement</h1>
            <p className="text-dim" style={{ marginBottom: "1.75rem" }}>Les meilleurs épargnants ScorAI.</p>

            {/* Podium */}
            {top3.length >= 3 && (
                <div className="hero-glass animate-scale-in" style={{ display: "flex", alignItems: "flex-end", justifyContent: "center", padding: "2rem 1rem 0", marginBottom: "1.75rem", gap: "0.5rem", overflow: "hidden" }}>
                    {/* 2nd */}
                    <div style={{ flex: 1, textAlign: "center" }}>
                        <div style={{ fontSize: "1.75rem", marginBottom: "0.35rem" }}>🥈</div>
                        <div style={{ fontWeight: 600, fontSize: "0.8rem" }}>{top3[1].display_name}</div>
                        <div className="text-dim" style={{ fontSize: "0.65rem", marginBottom: "0.5rem" }}>{top3[1].team}</div>
                        <div style={{ background: "rgba(0,0,0,0.03)", borderRadius: "10px 10px 0 0", padding: "0.75rem 0.5rem", height: "75px", display: "flex", flexDirection: "column", justifyContent: "flex-end", alignItems: "center" }}>
                            <div style={{ fontWeight: 700, fontSize: "0.85rem" }}>{(top3[1].total_saved_fcfa / 1000).toFixed(0)}k</div>
                            <div className="text-dim" style={{ fontSize: "0.6rem" }}>FCFA</div>
                        </div>
                    </div>
                    {/* 1st */}
                    <div style={{ flex: 1.15, textAlign: "center" }}>
                        <div className="animate-float" style={{ fontSize: "2rem", marginBottom: "0.35rem" }}>👑</div>
                        <div style={{ fontWeight: 700, fontSize: "0.9rem" }}>{top3[0].display_name}</div>
                        <div className="text-dim" style={{ fontSize: "0.7rem", marginBottom: "0.5rem" }}>{top3[0].team}</div>
                        <div style={{ background: "rgba(245,158,11,0.1)", borderRadius: "12px 12px 0 0", padding: "0.75rem 0.5rem", height: "100px", display: "flex", flexDirection: "column", justifyContent: "flex-end", alignItems: "center" }}>
                            <div className="text-gold" style={{ fontWeight: 800, fontSize: "1.05rem" }}>{(top3[0].total_saved_fcfa / 1000).toFixed(0)}k</div>
                            <div className="text-dim" style={{ fontSize: "0.6rem" }}>FCFA</div>
                            <div className="stat-pill" style={{ background: "rgba(245,158,11,0.15)", color: "var(--scorai-gold)", marginTop: "0.35rem", fontSize: "0.6rem" }}>🔥 {top3[0].streak_days}j</div>
                        </div>
                    </div>
                    {/* 3rd */}
                    <div style={{ flex: 1, textAlign: "center" }}>
                        <div style={{ fontSize: "1.75rem", marginBottom: "0.35rem" }}>🥉</div>
                        <div style={{ fontWeight: 600, fontSize: "0.8rem" }}>{top3[2].display_name}</div>
                        <div className="text-dim" style={{ fontSize: "0.65rem", marginBottom: "0.5rem" }}>{top3[2].team}</div>
                        <div style={{ background: "rgba(0,0,0,0.03)", borderRadius: "10px 10px 0 0", padding: "0.75rem 0.5rem", height: "60px", display: "flex", flexDirection: "column", justifyContent: "flex-end", alignItems: "center" }}>
                            <div style={{ fontWeight: 700, fontSize: "0.85rem" }}>{(top3[2].total_saved_fcfa / 1000).toFixed(0)}k</div>
                            <div className="text-dim" style={{ fontSize: "0.6rem" }}>FCFA</div>
                        </div>
                    </div>
                </div>
            )}

            {/* List */}
            <div className="stack" style={{ gap: "0.4rem" }}>
                {rest.map((user, i) => {
                    const self = isSelf(user.display_name);
                    return (
                        <div key={user.rank} className={`selectable-item animate-slide-up ${self ? "selected" : ""}`}
                            style={{ animationDelay: `${i * 0.05}s`, cursor: "default", padding: "0.85rem 1rem" }}>
                            <div style={{ width: "28px", fontWeight: 700, fontSize: "0.95rem", color: self ? "var(--scorai-primary)" : "var(--scorai-text-light)" }}>
                                {user.rank}
                            </div>
                            <span style={{ fontSize: "1.15rem", marginRight: "-0.25rem" }}>{TEAM_LOGOS[user.team] || "⚽"}</span>
                            <div style={{ flex: 1 }}>
                                <div style={{ fontWeight: 600, fontSize: "0.9rem" }}>
                                    {user.display_name} {self && <span className="text-blue">(Toi)</span>}
                                </div>
                                <div className="text-dim" style={{ fontSize: "0.75rem" }}>{user.team} · 🔥 {user.streak_days}j</div>
                            </div>
                            <div style={{ textAlign: "right" }}>
                                <div style={{ fontWeight: 700, fontSize: "0.9rem", color: self ? "var(--scorai-blue)" : "var(--scorai-primary)" }}>
                                    {user.total_saved_fcfa.toLocaleString()}
                                </div>
                                <div className="text-dim" style={{ fontSize: "0.65rem" }}>FCFA</div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </main>
    );
}
