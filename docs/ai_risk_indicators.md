# AI Risk Indicators

## 1. Purpose of AI KRIs
AI Key Risk Indicators (KRIs) provide measurable signals of instability, drift, or unsafe behavior in AI systems. These indicators support proactive governance and ensure that AI systems remain compliant, safe, and auditable.

## 2. KRI Definitions (Human-Readable)

### A. Number of AI Incidents per Week
Definition:
Count of all incidents logged in the last 7 days.

Why it matters:
Spikes indicate instability, drift, or misuse.

### B. Hallucination Incidents per AI System
Definition:
Number of hallucination-tagged incidents per AI system.

Why it matters:
Hallucinations are a top regulatory concern for safety and reliability.

### C. High-Severity Incidents
Definition:
Incidents marked as severity “High” or “Critical”.

Why it matters:
These require immediate escalation and root-cause analysis.

### D. Open vs Resolved Incidents
Definition:
Ratio of unresolved incidents to resolved ones.

Why it matters:
High open-incident count indicates operational risk and governance gaps.

### E. Changes per AI System (Volatility)
Definition:
Number of approved changes (model, prompt, RAG) per AI system in the last 30 days.

Why it matters:
High volatility = higher risk of regressions and unexpected behavior.

### F. Prompt/RAG Changes Linked to Incidents
Definition:
Count of incidents occurring within X days of a prompt or RAG update.

Why it matters:
This is your drift correlation signal — extremely valuable for auditors.

## Simple explanation
These KRIs define what "risky AI behavior" means in business terms.
They turn raw logs into governance-ready insights.

---

## Prompt & RAG Drift Indicators

### 1. Purpose
Prompt and RAG drift refers to operational instability caused by frequent or poorly controlled changes to prompts, retrieval sources, or knowledge bases. Drift increases the likelihood of hallucinations, inconsistent outputs, and unexpected model behavior.

**Key insight:** Drift is not about embeddings or statistical variance. It's about **operational instability** — too many changes, too fast, or changes made reactively after incidents.

### 2. Governance Definition of Drift

#### A. Frequent Prompt Version Changes
**Definition:** More than 3 prompt updates in 30 days

**Why it matters:**
- Indicates instability in prompt engineering
- Suggests unclear requirements or lack of testing
- Shows the system is being tuned reactively rather than proactively

**Auditor perspective:**
"This system's prompts are changing too often. Is there a clear requirement? Are changes being tested?"

#### B. Frequent RAG Source Changes
**Definition:** More than 3 RAG updates in 30 days

**Why it matters:**
- Indicates unstable knowledge base
- Suggests poor content governance
- Raises questions about data quality and curation

**Auditor perspective:**
"This knowledge base is volatile. How do you ensure consistency and accuracy?"

#### C. Changes Shortly After Incidents
**Definition:** Prompt or RAG update within 7 days of an incident

**Why it matters:**
- Indicates reactive behavior
- Suggests the system is compensating for instability
- Shows lack of proactive governance

**Auditor perspective:**
"Are you fixing the root cause or just patching symptoms?"

### 3. What Drift Is NOT
- ❌ **Not statistical drift** (model distribution shifts)
- ❌ **Not embedding drift** (vector space changes)
- ❌ **Not concept drift** (data distribution changes over time)

### 4. What Drift IS
- ✅ **Operational drift** = Too many changes too fast
- ✅ **Reactive drift** = Changes right after incidents
- ✅ **Governance drift** = Lack of change control discipline

This is exactly how regulators (FINMA, FDA, EMA, EU AI Act) expect drift to be defined.

### Simple explanation
Drift = instability. Not math. Not embeddings.
Just "too many changes too fast" or "changes right after something went wrong."

## 3. AI KRI → Data Source Mapping

KRI | Data Source | Field(s) Used | Notes
--- | --- | --- | ---
Incidents per week | Incident table | created_at, severity, type | Filter by last 7 days
Hallucination incidents | Incident table | type = 'hallucination' | Per AI system
High-severity incidents | Incident table | severity = 'high' or 'critical' | Used for escalation
Open vs resolved | Incident table | status | open, in_progress, resolved
Changes per AI system | ChangeRequest table | created_at, ai_system_id | Measures volatility
Prompt/RAG drift signals | PromptVersion, RAGVersion, Incident | timestamps | Correlate changes to incidents

Explanation:
These KRIs reuse existing system data. No new tables or data collection mechanisms are required. The indicators are computed from the Incident, ChangeRequest, PromptVersion, and RAGVersion tables already defined in the AI-GRC platform.

## Simple explanation
You’re not adding new data — you’re extracting risk signals from the data you already collect.
