"use client";
import Link from "next/link";

export default function LandingPage() {
  return (
    <main className="container" style={{ paddingBottom: "7rem", paddingTop: "3rem" }}>
      {/* Hero — Translucid Glass */}
      <section className="hero-glass animate-scale-in" style={{ textAlign: "center", padding: "3rem 1.75rem 2.5rem", marginBottom: "2rem" }}>
        <div className="animate-float" style={{ fontSize: "3.5rem", marginBottom: "1rem" }}>⚽️</div>
        <h1 className="gradient-text" style={{ marginBottom: "0.75rem", fontSize: "2.6rem", lineHeight: 1.1 }}>
          ScorAI
        </h1>
        <p className="text-dim" style={{ fontSize: "1rem", lineHeight: 1.6, maxWidth: "300px", margin: "0 auto 2rem", fontWeight: 500 }}>
          Ton équipe gagne, tu épargnes. Débloque un crédit instantané basé sur ta passion.
        </p>
        <div className="stack" style={{ gap: "0.75rem" }}>
          <Link href="/onboarding" className="btn btn-primary" style={{ width: "100%", padding: "1rem", fontSize: "1rem" }}>
            Commencer gratuitement
          </Link>
          <Link href="/dashboard" className="btn btn-outline" style={{ width: "100%", padding: "1rem" }}>
            Explorer la démo
          </Link>
        </div>
      </section>

      {/* Stats — Social Proof */}
      <section className="grid-3 animate-slide-up stagger-1" style={{ marginBottom: "2rem" }}>
        {[
          { value: "12K+", label: "Utilisateurs" },
          { value: "85M", label: "FCFA épargnés" },
          { value: "4.9★", label: "Satisfaction" },
        ].map((s, i) => (
          <div key={i} className="card" style={{ textAlign: "center", padding: "1.25rem 0.75rem" }}>
            <div style={{ fontSize: "1.5rem", fontWeight: 800, letterSpacing: "-0.03em" }}>{s.value}</div>
            <div className="text-dim" style={{ fontSize: "0.75rem", fontWeight: 500, marginTop: "0.15rem" }}>{s.label}</div>
          </div>
        ))}
      </section>

      {/* Features */}
      <section className="stack animate-slide-up stagger-2" style={{ gap: "0.75rem" }}>
        {[
          { icon: "⚡️", title: "Automatique", desc: "Ton équipe marque un but ? Tu épargnes automatiquement. Zéro effort." },
          { icon: "📊", title: "Trust Index", desc: "Un score de crédit construit sur tes habitudes, pas sur ton salaire." },
          { icon: "💸", title: "Zéro Frais", desc: "Notre batch engine absorbe les frais MoMo. 100% de ton argent t'appartient." },
          { icon: "🏆", title: "Classement Social", desc: "Compare ton épargne avec tes amis. Qui est le meilleur fan ?" },
        ].map((item, i) => (
          <div key={i} className="card" style={{ display: "flex", gap: "1rem", alignItems: "flex-start", padding: "1.25rem" }}>
            <div style={{
              width: "44px", height: "44px", borderRadius: "12px",
              background: "white", boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: "1.3rem", flexShrink: 0
            }}>
              {item.icon}
            </div>
            <div>
              <h3 style={{ fontSize: "1rem", marginBottom: "0.15rem" }}>{item.title}</h3>
              <p className="text-dim" style={{ fontSize: "0.85rem", lineHeight: 1.45 }}>{item.desc}</p>
            </div>
          </div>
        ))}
      </section>

      {/* Bottom CTA */}
      <section className="animate-slide-up stagger-3" style={{ marginTop: "2rem", textAlign: "center" }}>
        <p className="text-dim" style={{ fontSize: "0.85rem", marginBottom: "1rem" }}>
          Rejoins +12 000 superfans qui épargnent intelligemment.
        </p>
        <Link href="/onboarding" className="btn btn-emerald" style={{ width: "100%", padding: "1rem" }}>
          🚀 Créer mon compte
        </Link>
      </section>
    </main>
  );
}
