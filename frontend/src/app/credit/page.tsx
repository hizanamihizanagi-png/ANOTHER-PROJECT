"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { useSession } from "@/lib/session";

const FALLBACK_SCORE = {
    trust_score: 562, tier: "MICRO", tier_label: "Confirmé", max_loan_fcfa: 15000,
    explanations: [
        { feature: "savings_discipline", impact: 0.72, direction: "positive", description: "Discipline d'épargne" },
        { feature: "momo_activity", impact: 0.55, direction: "positive", description: "Activité MoMo" },
        { feature: "telecom_stability", impact: 0.61, direction: "positive", description: "Stabilité Télécom" },
        { feature: "behavioral_score", impact: 0.45, direction: "neutral", description: "Comportement" },
    ],
};

const TIERS = [
    { name: "Débutant", range: "0 – 399", max: "0 FCFA" },
    { name: "Confirmé", range: "400 – 599", max: "15 000 FCFA" },
    { name: "Expert", range: "600 – 799", max: "75 000 FCFA" },
    { name: "Élite", range: "800 – 1000", max: "200 000 FCFA" },
];

const ICONS: Record<string, string> = { savings_discipline: "💰", momo_activity: "📱", telecom_stability: "📶", behavioral_score: "🎯" };

export default function CreditPage() {
    const { session } = useSession();
    const [loading, setLoading] = useState(true);
    const [score, setScore] = useState(FALLBACK_SCORE);
    const [amount, setAmount] = useState(10000);
    const [applying, setApplying] = useState(false);
    const [result, setResult] = useState<{ approved: boolean; loan_id?: string; message?: string; reason?: string } | null>(null);

    useEffect(() => {
        const load = async () => {
            if (session.userId) {
                try {
                    const s = await api.getScore(session.userId);
                    setScore(s as typeof score);
                } catch { /* fallback */ }
            }
            setLoading(false);
        };
        load();
    }, [session.userId]);

    const interestRate = 0.10;
    const interest = Math.round(amount * interestRate);
    const total = amount + interest;
    const activeTier = TIERS.find(t => t.name === score.tier_label) || TIERS[1];

    const handleApply = async () => {
        setApplying(true);

        // Try backend first
        if (session.userId) {
            try {
                const res = await api.applyForLoan({ user_id: session.userId, amount_fcfa: amount });
                setResult(res as typeof result);
                setApplying(false);
                return;
            } catch { /* fall through to demo */ }
        }

        // Demo mode — simulate approval
        setTimeout(() => {
            setResult({
                approved: true,
                loan_id: "demo_loan_" + Date.now(),
                message: "Prêt simulé approuvé (mode démo)",
            });
            setApplying(false);
        }, 1500);
    };

    if (result) {
        return (
            <main className="container" style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: "100vh", textAlign: "center", padding: "2rem" }}>
                <div className="animate-scale-in" style={{ fontSize: "4.5rem", marginBottom: "1rem" }}>{result.approved ? "🎉" : "😔"}</div>
                <h2 className="animate-slide-up stagger-1" style={{ marginBottom: "0.5rem" }}>
                    {result.approved ? "Prêt approuvé!" : "Demande refusée"}
                </h2>
                {result.approved ? (
                    <>
                        <div className="animate-slide-up stagger-2" style={{ fontSize: "3rem", fontWeight: 800, margin: "0.75rem 0", letterSpacing: "-0.03em" }}>
                            {amount.toLocaleString()} FCFA
                        </div>
                        <p className="text-dim animate-slide-up stagger-2">Transfert en cours vers ton MoMo.</p>
                        <p className="text-dim animate-slide-up stagger-3" style={{ fontSize: "0.85rem", marginBottom: "2rem" }}>
                            Remboursement: <strong>{total.toLocaleString()} FCFA</strong> dans 30 jours.
                        </p>
                    </>
                ) : (
                    <p className="text-dim animate-slide-up stagger-2" style={{ marginBottom: "2rem" }}>
                        {result.reason || result.message || "Tu ne remplis pas encore les conditions."}
                    </p>
                )}
                <button className="btn btn-primary animate-slide-up stagger-3" onClick={() => setResult(null)} style={{ width: "100%", padding: "1rem", marginBottom: "0.75rem" }}>
                    Nouvelle simulation
                </button>
                <Link href="/dashboard" className="btn btn-outline animate-slide-up stagger-4" style={{ width: "100%", padding: "1rem" }}>
                    Retour à l&apos;accueil
                </Link>
            </main>
        );
    }

    if (loading) {
        return <main className="container" style={{ paddingTop: "4rem", textAlign: "center" }}><div className="animate-fade-in text-dim">Chargement...</div></main>;
    }

    return (
        <main className="container" style={{ paddingBottom: "7rem", paddingTop: "1.75rem" }}>
            <h1 style={{ marginBottom: "0.25rem" }}>Crédit</h1>
            <p className="text-dim" style={{ marginBottom: "1.75rem" }}>Ton Trust Index te donne accès au micro-crédit instantané.</p>

            {/* Trust Score */}
            <div className="hero-glass animate-scale-in" style={{ padding: "1.75rem", marginBottom: "1rem" }}>
                <div className="flex-between" style={{ marginBottom: "1.25rem" }}>
                    <div>
                        <p className="text-dim" style={{ fontSize: "0.8rem", fontWeight: 500 }}>Trust Index</p>
                        <div style={{ fontSize: "2.75rem", fontWeight: 800, lineHeight: 1, letterSpacing: "-0.03em" }}>{score.trust_score}</div>
                    </div>
                    <div className="stat-pill" style={{ background: "rgba(16,185,129,0.1)", color: "var(--scorai-emerald)" }}>{score.tier_label}</div>
                </div>
                <div className="stack" style={{ gap: "0.85rem" }}>
                    {score.explanations.map((exp, i) => {
                        const v = exp.impact;
                        const color = v >= 0.7 ? "fill-emerald" : v >= 0.5 ? "fill-gold" : "fill-danger";
                        const textColor = v >= 0.7 ? "var(--scorai-emerald)" : v >= 0.5 ? "var(--scorai-gold)" : "var(--scorai-danger)";
                        return (
                            <div key={i}>
                                <div className="flex-between" style={{ marginBottom: "0.3rem" }}>
                                    <span style={{ fontSize: "0.85rem", fontWeight: 500 }}>{ICONS[exp.feature] || "📊"} {exp.description}</span>
                                    <span style={{ fontSize: "0.85rem", fontWeight: 600, color: textColor }}>{Math.round(v * 100)}%</span>
                                </div>
                                <div className="progress-bar"><div className={`fill ${color}`} style={{ width: `${v * 100}%` }} /></div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Tiers */}
            <div className="animate-slide-up stagger-1" style={{ marginBottom: "1rem" }}>
                <h3 style={{ marginBottom: "0.5rem", fontSize: "1rem" }}>Niveaux</h3>
                <div className="stack" style={{ gap: "0.35rem" }}>
                    {TIERS.map((t, i) => (
                        <div key={i} className="selectable-item" style={{ cursor: "default", padding: "0.75rem 1rem", borderColor: t.name === activeTier.name ? "var(--scorai-primary)" : undefined, background: t.name === activeTier.name ? "#fafbfc" : undefined }}>
                            <div style={{ flex: 1 }}>
                                <span style={{ fontWeight: 600, fontSize: "0.9rem" }}>{t.name}</span>
                                <span className="text-dim" style={{ fontSize: "0.75rem", marginLeft: "0.5rem" }}>{t.range}</span>
                            </div>
                            <span style={{ fontWeight: 600, fontSize: "0.85rem", color: t.name === activeTier.name ? "var(--scorai-primary)" : "var(--scorai-text-light)" }}>≤ {t.max}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Simulator */}
            <div className="card animate-slide-up stagger-2">
                <h3 style={{ marginBottom: "1.25rem" }}>Simulateur de prêt</h3>
                <div style={{ textAlign: "center", marginBottom: "1.5rem" }}>
                    <div style={{ fontSize: "3rem", fontWeight: 800, letterSpacing: "-0.04em" }}>{amount.toLocaleString()}</div>
                    <div className="text-dim" style={{ fontWeight: 600 }}>FCFA</div>
                </div>
                <input type="range" min={1000} max={score.max_loan_fcfa} step={1000} value={amount} onChange={e => setAmount(Number(e.target.value))} style={{ marginBottom: "1.5rem" }} />
                <div style={{ background: "#f8fafc", borderRadius: "var(--scorai-radius-sm)", padding: "1.1rem", marginBottom: "1.25rem" }}>
                    <div className="flex-between" style={{ marginBottom: "0.6rem" }}>
                        <span className="text-dim" style={{ fontWeight: 500 }}>Intérêts (10%)</span>
                        <span style={{ fontWeight: 600 }}>{interest.toLocaleString()} FCFA</span>
                    </div>
                    <div className="flex-between" style={{ marginBottom: "0.6rem" }}>
                        <span className="text-dim" style={{ fontWeight: 500 }}>Durée</span>
                        <span style={{ fontWeight: 600 }}>30 jours</span>
                    </div>
                    <div className="flex-between" style={{ paddingTop: "0.6rem", borderTop: "1px solid var(--scorai-border)" }}>
                        <span style={{ fontWeight: 600 }}>Total à rembourser</span>
                        <span style={{ fontWeight: 700, fontSize: "1.1rem" }}>{total.toLocaleString()} FCFA</span>
                    </div>
                </div>
                <button className="btn btn-primary" onClick={handleApply} disabled={applying}
                    style={{ width: "100%", padding: "1rem", opacity: applying ? 0.6 : 1 }}>
                    {applying ? "⏳ Traitement..." : `💸 Demander ${amount.toLocaleString()} FCFA`}
                </button>
            </div>
        </main>
    );
}
