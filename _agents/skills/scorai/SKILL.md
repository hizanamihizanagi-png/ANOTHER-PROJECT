---
name: ScorAI Master Strategy
description: Core strategic context, business model, and operational roadmap for ScorAI (Data-for-Credit AI infrastructure).
---

# Investment Memorandum & Strategic Business Plan

**Entreprise :** ScorAI
**Projet :** Infrastructure d'Intelligence Artificielle de Crédit via l'Épargne Gamifiée (Trigger-Based Savings)
**Marché Cible :** Zone CEMAC (Tête de pont : Cameroun)
**Alignement :** Objectifs de Développement Durable de l'ONU (ODD 1, 8, 10)

Ce mémorandum détaille l'opportunité de marché, l'architecture technologique du scoring alternatif, le modèle de distribution réaliste, et la feuille de route opérationnelle de ScorAI.

---

## 1. Résumé Exécutif & Rationnel Stratégique (Le Pivot "Data-for-Credit")
Les campagnes traditionnelles d'éducation financière et les applications bancaires classiques échouent fondamentalement à capter l'attention de la jeunesse africaine. Parallèlement, l'industrie des paris sportifs fonctionne comme un mécanisme massif d'extraction de richesse.

ScorAI n'est pas simplement une application d'épargne. C'est une **infrastructure de notation de crédit par l'IA (ScorAI Engine)** qui utilise une application de finance comportementale (gamification sportive) comme "cheval de Troie" pour acquérir des données de solvabilité. En s'appuyant sur la théorie du "Nudge" pour lier des événements du quotidien à des actes d'épargne automatiques, nous créons un profil de crédit ultra-précis. L'épargne est notre outil de rétention et de collecte de données ; le micro-crédit instantané, basé sur un risque maîtrisé, est notre véritable moteur de monétisation.

## 2. Le Problème : Extraction de Richesse et "Invisible Credit"
Le problème central est double : l'évaporation des capitaux des ménages et l'incapacité des institutions à évaluer le risque de crédit dans le secteur informel.

*   **L'Hémorragie des Capitaux :** La recherche académique démontre que les investissements nets des ménages chutent de près de 14 % lorsque l'accès aux paris sportifs augmente.
*   **L'Invisibilité Financière et le NPL :** Des millions de jeunes adultes n'ont aucun historique formel. Les institutions de microfinance (IMF) au Cameroun subissent des taux de prêts non performants (NPL) réels sur le terrain allant de 15 % à 25 %. Les défauts ne viennent pas seulement de la mauvaise foi, mais de chocs systémiques (hospitalisation, imprévus, pression sociale familiale).
*   **Le Rejet de la Banque :** Les institutions offrent des interfaces archaïques incapables de rivaliser avec la gratification instantanée offerte par 1xBet ou TikTok.

## 3. La Solution et l'Architecture Produit (Le Front-end Gamifié)
L'application s'intègre aux API de Mobile Money (MTN, Orange) et à des API de données externes pour automatiser la discipline financière.

*   **Le Déclencheur "Superfan" :** L'utilisateur configure une règle : "Chaque fois qu'Arsenal gagne, prélève automatiquement 1000 FCFA".
*   **Le "Virtual Ledger" (Contournement des Frais MoMo) :** Pour éviter que les taxes Mobile Money (0.5 % à 1.5 % par transaction) ne détruisent le capital, l'application met à jour un solde virtuel instantanément pour générer la dopamine (ex: +1000 FCFA visuels). Le prélèvement réel ne s'exécute qu'en "Batch" (groupement) au-delà d'un seuil de rentabilité (ex: 5000 FCFA).
*   **Le Déblocage du Crédit (La Rétention) :** L'UX projette clairement : "Maintiens ta série d'épargne pendant 3 mois, et tu débloques une ligne de crédit instantanée de 50 000 FCFA pour tes urgences".

## 4. Architecture Technique & ScorAI Data Engine (Le Moat)
La discipline d'épargne seule ne suffit pas à garantir le remboursement d'un crédit face aux aléas de la vie. Notre avantage concurrentiel réside dans notre moteur d'ingestion de données alternatives.

*   **L'Infrastructure USSD :** Une stratégie "Offline-First" avec accès via codes USSD (ex: *123#) connectés aux passerelles télécoms locales.
*   **Le Moteur d'IA (Scoring Holistique) :** Le modèle ScorAI intègre de multiples dimensions de données pour évaluer la capacité réelle de survie aux chocs :
    *   *Signaux de Discipline :* Fréquence des micro-épargnes via l'app, respect des "streaks" (séries).
    *   *Signaux Télécoms (Telco Data) :* Historique de facturation, régularité des recharges de crédit (airtime), et âge de la carte SIM.
    *   *Signaux Mobile Money :* Fréquence et volume des transactions sur le portefeuille numérique, transferts reçus (stabilité des revenus).
    *   *Signaux Comportementaux :* Paiement régulier de factures (eau, électricité) via l'intégration API.
*   Cette matrice de données nous permet de cibler un NPL de 10 % à 12 % au passage à l'échelle (contre 25 % pour le marché traditionnel).

## 5. Analyse du Marché et Paysage Concurrentiel
*   **TAM (Marché Total) :** Les revenus des fintechs en Afrique devraient atteindre 65 milliards de dollars d'ici 2030.
*   **SAM (Marché Disponible) :** Le Cameroun compte 19,5 millions de comptes Mobile Money actifs, avec un volume de transactions régional dominant.
*   **SOM (Marché Obtenable) :** Capturer 2 % des utilisateurs actifs au Cameroun représente environ 390 000 utilisateurs hautement qualifiés pour le crédit.
*   **La Guerre de l'Attention :** Nos concurrents directs ne sont pas les banques traditionnelles. Nos vrais concurrents sont 1xBet (temps + dopamine), TikTok (attention), et WhatsApp (communauté). Notre interface utilisateur priorise la micro-animation (confettis, jauges de progression) et l'immédiateté.

## 6. Environnement Réglementaire : Le Modèle TSP
*   **Le Contournement Légal (Technical Service Provider) :** Obtenir une licence d'Établissement de Paiement (PSP) auprès de la BEAC et de la COBAC prend de 6 à 12 mois. ScorAI opère juridiquement comme un fournisseur technologique (TSP). Nous nouons un accord de partenariat technique (SLA) avec une banque déjà agréée. L'argent transite directement du portefeuille Mobile Money vers le compte séquestre bancaire. ScorAI ne détient jamais les dépôts.
*   **Origination du Crédit :** Les prêts sont émis sur le bilan d'une IMF partenaire, qui nous reverse une commission pour l'acquisition du client (Lead Gen) et la fourniture du score de risque (ScorAI API).

## 7. Modèle de Monétisation et Unit Economics Réalistes
Nous ne monétisons pas le rendement de l'épargne (trop faible). Nous monétisons le crédit et les données.

*   **ARPU :** Si un utilisateur qualifié prend 4 micro-prêts par an (ex: 30 000 FCFA à 10 % d'intérêt sur 30 jours, commission partagée avec l'IMF), l'ARPU généré pour ScorAI se situe entre 15 $ et 30 $ par an.
*   **CAC Ajusté :** La viralité WhatsApp est excellente pour les 1 000 premiers utilisateurs. Pour atteindre 100 000 utilisateurs, nous intégrons un mix d'acquisition payante (influenceurs locaux, partenariats B2B). Notre CAC cible lissé au passage à l'échelle est de 2,00 $ à 4,00 $.
*   **Ratio LTV:CAC :** Avec un LTV (basé sur 2 ans de rétention forcée) d'environ 40 $ et un CAC de 4 $, le ratio de 10:1 est exceptionnellement sain et justifie une levée de fonds agressive (Série A).

## 8. Modèle Opérationnel et Structure Organisationnelle (McKinsey 7-S)
**Équipe Fondatrice (C-Suite) :**
*   **CEO (Vision & Dealmaking) :** Responsable de l'obtention du contrat TSP vital avec une banque, levée de fonds, relations COBAC.
*   **CTO / Head of AI :** Architecte du moteur ScorAI (intégration Telco + MoMo), et de la sécurisation asynchrone du Virtual Ledger.
*   **Chief Risk & Compliance Officer (CRO/CCO) :** Expert des réglementations e-KYC.
*   **Head of Growth & Behavioral Product :** Responsable du maintien du CAC sous les 4 $, gestion des cohortes, et optimisation des boucles de dopamine (UX).

**Plan de Recrutement (Mois 1 à 6) :**
*   **Backend Engineer (x2) :** Créer le Virtual Ledger asynchrone ; intégration API (Mobile Money / Sport / USSD). Expert Python/Go.
*   **Data Scientist (x2) :** Modéliser le risque en combinant épargne + données Telco + historique MoMo. Expert ML (XGBoost).
*   **Product Designer (x1) :** Gamifier l'interface pour imiter l'adrénaline des paris sportifs. Expert Nudge et UX.
*   **Growth Marketer (x1) :** Orchestrer les campagnes d'influence et l'acquisition hors-ligne.

## 9. Workflows Opérationnels Critiques

### Workflow 1 : Résolution des Frais via le Virtual Ledger
1.  **Le Nudge :** Configuration : "Épargne 500 FCFA si le Real Madrid gagne". L'API sport valide l'événement.
2.  **Mise à jour Virtuelle (UX) :** Le solde virtuel ScorAI augmente instantanément (+500 FCFA) avec animations (dopamine). Aucun argent réel n'a bougé.
3.  **La Consolidation (Batching) :** Le système met les montants en file d'attente.
4.  **L'Exécution Réelle :** Lorsque le solde virtuel atteint 5 000 FCFA (ou le dimanche soir), l'API MoMo déclenche un unique prélèvement physique vers le compte de la banque partenaire.

### Workflow 2 : Ingestion de Données et Décision de Crédit (ScorAI Engine)
1.  **Phase d'Observation (Mois 1 à 3) :** L'application récolte (avec consentement) les métadonnées de l'appareil, le journal des SMS MoMo, et l'historique d'appels.
2.  **Analyse ML (Mois 4) :** L'algorithme détecte une stabilité des revenus et une bonne hygiène de paiement.
3.  **L'Offre (Le Hook) :** Le "ScorAI Trust Index" dépasse le seuil critique. Notification push : "Ton coffre est sécurisé. Tu as débloqué une ligne de crédit de 30 000 FCFA".
4.  **Décaissement :** L'argent est viré instantanément depuis le bilan de l'IMF partenaire.

## 10. Feuille de Route Stratégique Détaillée (Horizons de McKinsey)
*   **Horizon 1 : Preuve de Concept et Acquisition Virale (Mois 1 à 6)**
    *   Tech/Légal : Partenariat TSP, Virtual Ledger, USSD.
    *   Lancement : Ciblage strict des communautés WhatsApp de parieurs (les 1 000 premiers utilisateurs). 
*   **Horizon 2 : Le Modèle de Crédit et le Passage à l'Échelle (Mois 7 à 12)**
    *   GTM : Acquisition payante (objectif : 50 000 utilisateurs, CAC 3,50 $).
    *   Lancement Crédit : Déploiement v1 du modèle ScorAI, démontrant un NPL < 12 %.
*   **Horizon 3 : Monétisation Massive et B2B SaaS (Années 2 à 3)**
    *   Scale : > 200 000 utilisateurs actifs. Les revenus du crédit partagés avec les IMF deviennent le centre de profit.
    *   B2B : Commercialisation de l'API "ScorAI Trust Index" en mode SaaS aux banques.
    *   Expansion : Déploiement UEMOA (Côte d'Ivoire) et RDC.

---

## 11. Réponses aux VC (Le Pitch "Data-for-Credit")

### 1. Pourquoi un utilisateur resterait 24 mois? (La Rétention)
Il ne reste pas pour le taux d’intérêt de 3 %, il reste pour débloquer du levier financier et maintenir son statut social :
*   **La mécanique de déblocage :** Maintenir sa série d'épargne (streak) garantit une ligne de crédit instantanée en cas d'urgence. C'est son filet de sécurité.
*   **L'aversion à la perte :** Arrêter signifie perdre son "Score de Confiance" accumulé.
*   **L'UX de la Gratification :** Célébration par micro-animations qui imitent la récompense d'un pari gagné (1xBet).

### 2. Comment survivre aux taxes Mobile Money (0.5% - 1.5%) ?
En utilisant l'architecture du **Virtual Ledger**. 
*   L'application met à jour le solde *virtuellement* et instantanément à chaque évènement sportif, sans toucher au Mobile Money.
*   Le prélèvement physique réel s'exécute en *Batch* (groupement) une fois un seuil atteint (ex: 5000 FCFA), diluant l'impact des frais.

### 3. Quel est l'ARPU réel ?
L'ARPU ne provient pas de l'épargne, mais de la **monétisation du profil de crédit comportemental**.
*   Exemple : 4 micro-prêts par an de 30 000 FCFA à 10% d'intérêts. 
*   Ceci génère un ARPU de **15 $ à 30 $ par an**. Avec un CAC contrôlé, les unit economics justifient une valorisation de Série A saine.

### 4. Qu'est-ce qui empêche un concurrent de vous copier ?
Le Moat Algorithmique et de Marque.
*   **Data Flywheel :** Le vrai produit est l'algorithme d'apprentissage automatique entraîné par des milliers de points de données quotidiennes (fréquences, horaires, biais liés au sport). Un copycat commence avec un algorithme vide et subira des défauts massifs s'il prête.
*   **Positionnement Lifestyle :** C'est une marque de *lifestyle et divertissement*, située dans l'espace mental du sport et des réseaux sociaux, captant mieux l'attention qu'une marque utilitaire classique.
