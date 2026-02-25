"use client";
import { useState } from "react";
import { api } from "@/lib/api";
import { useSession } from "@/lib/session";

const TEAMS = [
    { id: 42, name: "Arsenal", league: "Premier League", logo: "🔴" },
    { id: 50, name: "Man City", league: "Premier League", logo: "🔵" },
    { id: 85, name: "PSG", league: "Ligue 1", logo: "🔵🔴" },
    { id: 541, name: "Real Madrid", league: "La Liga", logo: "⚪" },
    { id: 529, name: "Barcelona", league: "La Liga", logo: "🔴🔵" },
    { id: 40, name: "Liverpool", league: "Premier League", logo: "🔴" },
    { id: 838, name: "Coton Sport", league: "Elite One 🇨🇲", logo: "🟢" },
    { id: 839, name: "Canon Ydé", league: "Elite One 🇨🇲", logo: "🟡" },
];

const EVENTS = [
    { type: "WIN", label: "Victoire", icon: "🏆" },
    { type: "GOAL", label: "But marqué", icon: "⚽" },
    { type: "CLEAN_SHEET", label: "Clean Sheet", icon: "🧤" },
    { type: "DRAW", label: "Match nul", icon: "🤝" },
];

export default function OnboardingPage() {
    const { setSession } = useSession();
    const [step, setStep] = useState(1);
    const [name, setName] = useState("");
    const [phone, setPhone] = useState("");
    const [selectedTeam, setSelectedTeam] = useState<typeof TEAMS[0] | null>(null);
    const [selectedEvent, setSelectedEvent] = useState("WIN");
    const [amount, setAmount] = useState(1000);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleComplete = async () => {
        if (!selectedTeam) return;
        setLoading(true);
        setError("");

        let userId = "demo_" + Date.now();
        let referralCode = "SCOR" + name.slice(0, 2).toUpperCase() + Math.floor(Math.random() * 99);

        try {
            const signup = await api.signup({
                phone_number: phone,
                display_name: name,
                favorite_team_id: selectedTeam.id,
                favorite_team_name: selectedTeam.name,
            });
            userId = signup.user_id;
            referralCode = signup.referral_code;

            // Create the first trigger
            await api.createTrigger({
                user_id: userId,
                team_id: selectedTeam.id,
                team_name: selectedTeam.name,
                event_type: selectedEvent,
                amount_fcfa: amount,
            }).catch(() => { }); // Non-blocking
        } catch {
            // Backend may be down — still save session with demo ID
        }

        // Always save session so the rest of the app works
        setSession({ userId, displayName: name, referralCode });
        setLoading(false);
        window.location.href = "/dashboard";
    };

    return (
        <main className="container" style={{ minHeight: "100vh", display: "flex", flexDirection: "column", paddingTop: "3.5rem", paddingBottom: "2rem" }}>
            {/* Progress */}
            <div style={{ display: "flex", gap: "0.5rem", marginBottom: "2.5rem" }}>
                {[1, 2, 3].map(s => (
                    <div key={s} style={{ flex: 1, height: "3px", borderRadius: "2px", background: s <= step ? "var(--scorai-primary)" : "rgba(0,0,0,0.06)", transition: "background 0.3s" }} />
                ))}
            </div>

            {error && (
                <div style={{ background: "rgba(239,68,68,0.1)", color: "var(--scorai-danger)", padding: "0.75rem 1rem", borderRadius: "var(--scorai-radius-sm)", marginBottom: "1rem", fontSize: "0.9rem", fontWeight: 500 }}>
                    ⚠️ {error}
                </div>
            )}

            <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
                {step === 1 && (
                    <div className="animate-slide-up" style={{ flex: 1, display: "flex", flexDirection: "column" }}>
                        <h1 style={{ marginBottom: "0.5rem" }}>Bienvenue.</h1>
                        <p className="text-dim" style={{ fontSize: "1.05rem", marginBottom: "2.5rem" }}>Crée ton profil en 30 secondes.</p>
                        <div className="stack" style={{ gap: "1rem" }}>
                            <div>
                                <label className="text-dim" style={{ fontSize: "0.8rem", fontWeight: 600, display: "block", marginBottom: "0.4rem" }}>Prénom</label>
                                <input type="text" placeholder="Ex: Jean-Pierre" value={name} onChange={e => setName(e.target.value)} />
                            </div>
                            <div>
                                <label className="text-dim" style={{ fontSize: "0.8rem", fontWeight: 600, display: "block", marginBottom: "0.4rem" }}>Numéro MoMo</label>
                                <input type="tel" placeholder="6XX XXX XXX" value={phone} onChange={e => setPhone(e.target.value)} />
                            </div>
                        </div>
                        <div style={{ marginTop: "auto", paddingTop: "2rem" }}>
                            <button className="btn btn-primary" disabled={!name || !phone} onClick={() => setStep(2)} style={{ width: "100%", padding: "1rem", opacity: (!name || !phone) ? 0.4 : 1 }}>
                                Continuer
                            </button>
                        </div>
                    </div>
                )}

                {step === 2 && (
                    <div className="animate-slide-up" style={{ flex: 1, display: "flex", flexDirection: "column" }}>
                        <h1 style={{ marginBottom: "0.5rem" }}>Ton équipe.</h1>
                        <p className="text-dim" style={{ fontSize: "1.05rem", marginBottom: "2rem" }}>Choisis le club de ton cœur.</p>
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
                            {TEAMS.map(team => (
                                <div key={team.id} className={`selectable-item ${selectedTeam?.id === team.id ? "selected" : ""}`} onClick={() => setSelectedTeam(team)}
                                    style={{ flexDirection: "column", padding: "1.25rem 0.75rem", textAlign: "center", gap: "0.35rem" }}>
                                    <div style={{ fontSize: "1.75rem" }}>{team.logo}</div>
                                    <div style={{ fontWeight: 600, fontSize: "0.9rem" }}>{team.name}</div>
                                    <div className="text-dim" style={{ fontSize: "0.7rem" }}>{team.league}</div>
                                </div>
                            ))}
                        </div>
                        <div style={{ display: "flex", gap: "0.75rem", marginTop: "auto", paddingTop: "2rem" }}>
                            <button className="btn btn-outline" onClick={() => setStep(1)} style={{ padding: "1rem 1.5rem" }}>Retour</button>
                            <button className="btn btn-primary" disabled={!selectedTeam} onClick={() => setStep(3)} style={{ flex: 1, padding: "1rem", opacity: !selectedTeam ? 0.4 : 1 }}>Continuer</button>
                        </div>
                    </div>
                )}

                {step === 3 && (
                    <div className="animate-slide-up" style={{ flex: 1, display: "flex", flexDirection: "column" }}>
                        <h1 style={{ marginBottom: "0.5rem" }}>Le Trigger.</h1>
                        <p className="text-dim" style={{ fontSize: "1.05rem", marginBottom: "2rem" }}>Configure ta première règle d&apos;épargne.</p>
                        <div style={{ marginBottom: "1.5rem" }}>
                            <label className="text-dim" style={{ fontSize: "0.8rem", fontWeight: 600, display: "block", marginBottom: "0.5rem" }}>Événement</label>
                            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem" }}>
                                {EVENTS.map(ev => (
                                    <div key={ev.type} className={`selectable-item ${selectedEvent === ev.type ? "selected" : ""}`} onClick={() => setSelectedEvent(ev.type)}
                                        style={{ justifyContent: "center", gap: "0.4rem", padding: "0.85rem" }}>
                                        <span>{ev.icon}</span>
                                        <span style={{ fontWeight: 500, fontSize: "0.85rem" }}>{ev.label}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                        <div style={{ marginBottom: "1.5rem" }}>
                            <label className="text-dim" style={{ fontSize: "0.8rem", fontWeight: 600, display: "block", marginBottom: "0.5rem" }}>Montant</label>
                            <div style={{ textAlign: "center", marginBottom: "1rem" }}>
                                <span style={{ fontSize: "2.75rem", fontWeight: 800, letterSpacing: "-0.03em" }}>{amount.toLocaleString()}</span>
                                <span className="text-dim" style={{ fontSize: "1rem", marginLeft: "0.25rem" }}>FCFA</span>
                            </div>
                            <input type="range" min={500} max={5000} step={500} value={amount} onChange={e => setAmount(Number(e.target.value))} />
                        </div>
                        <div className="card" style={{ textAlign: "center", padding: "1.25rem", background: "#f8fafc" }}>
                            <p style={{ fontSize: "0.9rem", fontWeight: 500 }}>
                                Chaque <span className="text-emerald" style={{ fontWeight: 700 }}>{EVENTS.find(e => e.type === selectedEvent)?.label}</span> de <strong>{selectedTeam?.name}</strong>, épargne <span style={{ fontWeight: 700 }}>{amount.toLocaleString()} FCFA</span>
                            </p>
                        </div>
                        <div style={{ display: "flex", gap: "0.75rem", marginTop: "auto", paddingTop: "2rem" }}>
                            <button className="btn btn-outline" onClick={() => setStep(2)} style={{ padding: "1rem 1.5rem" }}>Retour</button>
                            <button className="btn btn-primary" onClick={handleComplete} disabled={loading} style={{ flex: 1, padding: "1rem", opacity: loading ? 0.6 : 1 }}>
                                {loading ? "Création..." : "🚀 Activer mon trigger"}
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </main>
    );
}
