"use client";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { useSession } from "@/lib/session";

const TEAMS_LOCAL = [
    { id: 42, name: "Arsenal", logo: "🔴" },
    { id: 50, name: "Man City", logo: "🔵" },
    { id: 85, name: "PSG", logo: "🔵🔴" },
    { id: 541, name: "Real Madrid", logo: "⚪" },
    { id: 40, name: "Liverpool", logo: "🔴" },
    { id: 838, name: "Coton Sport", logo: "🟢" },
];

const EVENTS = [
    { type: "WIN", label: "Victoire", icon: "🏆" },
    { type: "GOAL", label: "But marqué", icon: "⚽" },
    { type: "CLEAN_SHEET", label: "Clean Sheet", icon: "🧤" },
    { type: "DRAW", label: "Match nul", icon: "🤝" },
];

const EVENT_LABELS: Record<string, string> = { WIN: "Victoire", GOAL: "But marqué", CLEAN_SHEET: "Clean Sheet", DRAW: "Match nul" };
const TEAM_LOGOS: Record<string, string> = { Arsenal: "🔴", "Man City": "🔵", PSG: "🔵🔴", "Real Madrid": "⚪", Liverpool: "🔴", "Coton Sport": "🟢", "Canon Ydé": "🟡", Barcelona: "🔴🔵" };

interface Trigger {
    id: string;
    team_name: string;
    event_type: string;
    amount_fcfa: number;
    times_triggered: number;
    total_saved_fcfa: number;
    status: string;
}

const DEMO_TRIGGERS: Trigger[] = [
    { id: "demo1", team_name: "Arsenal", event_type: "WIN", amount_fcfa: 1000, times_triggered: 12, total_saved_fcfa: 12000, status: "ACTIVE" },
    { id: "demo2", team_name: "Arsenal", event_type: "GOAL", amount_fcfa: 500, times_triggered: 28, total_saved_fcfa: 14000, status: "ACTIVE" },
];

export default function TriggersPage() {
    const { session } = useSession();
    const [triggers, setTriggers] = useState<Trigger[]>(DEMO_TRIGGERS);
    const [loading, setLoading] = useState(true);
    const [showCreate, setShowCreate] = useState(false);
    const [newTeam, setNewTeam] = useState<typeof TEAMS_LOCAL[0] | null>(null);
    const [newEvent, setNewEvent] = useState("WIN");
    const [newAmount, setNewAmount] = useState(1000);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        const load = async () => {
            if (session.userId) {
                try {
                    const data = await api.getMyTriggers(session.userId);
                    if (Array.isArray(data) && data.length > 0) setTriggers(data as Trigger[]);
                } catch { /* keep demo triggers */ }
            }
            setLoading(false);
        };
        load();
    }, [session.userId]);

    const totalSaved = triggers.reduce((s, t) => s + (t.total_saved_fcfa || 0), 0);
    const totalTriggered = triggers.reduce((s, t) => s + (t.times_triggered || 0), 0);
    const activeCount = triggers.filter(t => t.status === "ACTIVE").length;

    const addTrigger = async () => {
        if (!newTeam) return;
        setSaving(true);

        const newTrigger: Trigger = {
            id: "t_" + Date.now(),
            team_name: newTeam.name,
            event_type: newEvent,
            amount_fcfa: newAmount,
            times_triggered: 0,
            total_saved_fcfa: 0,
            status: "ACTIVE",
        };

        // Try backend, but always add locally
        if (session.userId) {
            try {
                const created = await api.createTrigger({
                    user_id: session.userId,
                    team_id: newTeam.id,
                    team_name: newTeam.name,
                    event_type: newEvent,
                    amount_fcfa: newAmount,
                });
                if (created && typeof created === "object" && "id" in created) {
                    newTrigger.id = (created as Record<string, string>).id;
                }
            } catch { /* use local */ }
        }

        setTriggers([...triggers, newTrigger]);
        setShowCreate(false);
        setNewTeam(null);
        setSaving(false);
    };

    const togglePause = async (t: Trigger) => {
        // Toggle locally immediately
        setTriggers(triggers.map(tr =>
            tr.id === t.id ? { ...tr, status: tr.status === "ACTIVE" ? "PAUSED" : "ACTIVE" } : tr
        ));
        // Try backend
        if (session.userId) {
            api.pauseTrigger(t.id, session.userId).catch(() => { });
        }
    };

    if (loading) {
        return <main className="container" style={{ paddingTop: "4rem", textAlign: "center" }}><div className="animate-fade-in text-dim">Chargement...</div></main>;
    }

    return (
        <main className="container" style={{ paddingBottom: "7rem", paddingTop: "1.75rem" }}>
            <div className="flex-between" style={{ marginBottom: "1.75rem" }}>
                <div>
                    <h1 style={{ marginBottom: "0.25rem" }}>Triggers</h1>
                    <p className="text-dim" style={{ fontSize: "0.9rem" }}>Automatise ton épargne.</p>
                </div>
                <button className="btn btn-primary" onClick={() => setShowCreate(!showCreate)} style={{ padding: "0.6rem 1.15rem", fontSize: "0.9rem" }}>
                    {showCreate ? "✕ Fermer" : "+ Nouveau"}
                </button>
            </div>

            {/* Stats */}
            <div className="grid-3 animate-fade-in" style={{ marginBottom: "1.5rem" }}>
                <div className="card" style={{ textAlign: "center", padding: "0.85rem 0.5rem" }}>
                    <div style={{ fontSize: "1.35rem", fontWeight: 800 }}>{activeCount}</div>
                    <div className="text-dim" style={{ fontSize: "0.65rem" }}>Actifs</div>
                </div>
                <div className="card" style={{ textAlign: "center", padding: "0.85rem 0.5rem" }}>
                    <div className="text-emerald" style={{ fontSize: "1.35rem", fontWeight: 800 }}>{totalSaved.toLocaleString()}</div>
                    <div className="text-dim" style={{ fontSize: "0.65rem" }}>FCFA épargnés</div>
                </div>
                <div className="card" style={{ textAlign: "center", padding: "0.85rem 0.5rem" }}>
                    <div className="text-gold" style={{ fontSize: "1.35rem", fontWeight: 800 }}>{totalTriggered}x</div>
                    <div className="text-dim" style={{ fontSize: "0.65rem" }}>Déclenchés</div>
                </div>
            </div>

            {/* Create Form — ALWAYS available */}
            {showCreate && (
                <div className="hero-glass animate-scale-in" style={{ padding: "1.5rem", marginBottom: "1.5rem" }}>
                    <h3 style={{ marginBottom: "1rem" }}>Nouveau trigger</h3>
                    <label className="text-dim" style={{ fontSize: "0.8rem", fontWeight: 600, display: "block", marginBottom: "0.4rem" }}>Équipe</label>
                    <div className="grid-3" style={{ marginBottom: "1rem" }}>
                        {TEAMS_LOCAL.map(t => (
                            <div key={t.id} className={`selectable-item ${newTeam?.id === t.id ? "selected" : ""}`} onClick={() => setNewTeam(t)}
                                style={{ flexDirection: "column", padding: "0.75rem 0.5rem", textAlign: "center", gap: "0.2rem" }}>
                                <span style={{ fontSize: "1.25rem" }}>{t.logo}</span>
                                <span style={{ fontSize: "0.7rem", fontWeight: 600 }}>{t.name}</span>
                            </div>
                        ))}
                    </div>
                    <label className="text-dim" style={{ fontSize: "0.8rem", fontWeight: 600, display: "block", marginBottom: "0.4rem" }}>Événement</label>
                    <div className="grid-2" style={{ marginBottom: "1rem" }}>
                        {EVENTS.map(ev => (
                            <div key={ev.type} className={`selectable-item ${newEvent === ev.type ? "selected" : ""}`} onClick={() => setNewEvent(ev.type)}
                                style={{ justifyContent: "center", gap: "0.35rem", padding: "0.75rem" }}>
                                <span>{ev.icon}</span>
                                <span style={{ fontSize: "0.8rem", fontWeight: 500 }}>{ev.label}</span>
                            </div>
                        ))}
                    </div>
                    <label className="text-dim" style={{ fontSize: "0.8rem", fontWeight: 600, display: "block", marginBottom: "0.4rem" }}>Montant</label>
                    <div style={{ textAlign: "center", marginBottom: "0.75rem" }}>
                        <span style={{ fontSize: "2rem", fontWeight: 800 }}>{newAmount.toLocaleString()}</span>
                        <span className="text-dim"> FCFA</span>
                    </div>
                    <input type="range" min={500} max={5000} step={500} value={newAmount} onChange={e => setNewAmount(Number(e.target.value))} style={{ marginBottom: "1rem" }} />
                    <div style={{ display: "flex", gap: "0.65rem" }}>
                        <button className="btn btn-outline" onClick={() => setShowCreate(false)} style={{ flex: 1, padding: "0.85rem" }}>Annuler</button>
                        <button className="btn btn-primary" onClick={addTrigger} disabled={!newTeam || saving}
                            style={{ flex: 1, padding: "0.85rem", opacity: !newTeam || saving ? 0.4 : 1 }}>
                            {saving ? "Création..." : "✓ Activer"}
                        </button>
                    </div>
                </div>
            )}

            {/* Trigger List */}
            <div className="stack" style={{ gap: "0.5rem" }}>
                {triggers.map((t, i) => (
                    <div key={t.id} className="card animate-slide-up" style={{ animationDelay: `${i * 0.06}s`, padding: "1.15rem" }}>
                        <div className="flex-between" style={{ marginBottom: "0.6rem" }}>
                            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
                                <span style={{ fontSize: "1.25rem" }}>{TEAM_LOGOS[t.team_name] || "⚽"}</span>
                                <div>
                                    <span style={{ fontWeight: 600, fontSize: "0.95rem" }}>{t.team_name}</span>
                                    <span className="stat-pill" style={{
                                        marginLeft: "0.5rem", padding: "0.15rem 0.5rem", fontSize: "0.65rem",
                                        background: t.status === "ACTIVE" ? "rgba(16,185,129,0.1)" : "rgba(148,163,184,0.1)",
                                        color: t.status === "ACTIVE" ? "var(--scorai-emerald)" : "var(--scorai-text-dim)",
                                    }}>{t.status === "ACTIVE" ? "Actif" : "Pause"}</span>
                                </div>
                            </div>
                            <span style={{ fontWeight: 700, fontSize: "1rem" }}>
                                {t.amount_fcfa.toLocaleString()} <span className="text-dim" style={{ fontSize: "0.75rem", fontWeight: 500 }}>FCFA</span>
                            </span>
                        </div>
                        <div className="flex-between">
                            <span className="text-dim" style={{ fontSize: "0.8rem" }}>
                                {EVENTS.find(e => e.type === t.event_type)?.icon || "⚡"} {EVENT_LABELS[t.event_type] || t.event_type}
                                {t.times_triggered > 0 && <span> · {t.times_triggered}x</span>}
                            </span>
                            <button onClick={() => togglePause(t)} style={{ background: "none", border: "1px solid var(--scorai-border)", borderRadius: "999px", padding: "0.3rem 0.75rem", cursor: "pointer", fontSize: "0.7rem", fontWeight: 600, color: t.status === "ACTIVE" ? "var(--scorai-text-dim)" : "var(--scorai-emerald)" }}>
                                {t.status === "ACTIVE" ? "⏸ Pause" : "▶ Activer"}
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </main>
    );
}
