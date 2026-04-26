# TruthLens — Plain Language Guide
### *What it is, what it does, why it matters, and how it works — no jargon required*

---

## The Problem: AI Lies. Confidently.

You've probably used ChatGPT or a similar AI assistant and been impressed by how fluent and authoritative it sounds. But here's the uncomfortable truth: **AI doesn't know when it doesn't know something.** It fills in the gaps with plausible-sounding information — sometimes correct, sometimes completely made up.

This is called a **hallucination** — and it's one of the biggest unsolved problems in AI today.

Imagine you give an AI assistant a company policy document and ask it a question about your refund policy. The AI reads the document but then confidently states a rule that isn't in the document — or worse, contradicts it. If you're a customer service agent relying on that answer, you just gave a customer the wrong information.

Now scale that to healthcare, legal advice, financial guidance, or any domain where being wrong has real consequences.

**That's the problem TruthLens is built to solve.**

---

## What is TruthLens?

TruthLens is a **fact-checking layer for AI answers.**

You give it three things:
1. A **source document** — the "ground truth" (a policy, a report, a paragraph, anything)
2. A **question** — what you want the AI to answer
3. An **AI-generated answer** — either from TruthLens itself, or one you paste in

TruthLens then takes that answer apart, sentence by sentence and claim by claim, and asks: *"Is this actually in the source document?"* It scores the answer, flags the problems, and tells you in plain English what went wrong and what to do about it.

---

## Why Does This Matter?

Here are some real-world situations where TruthLens is valuable:

- **Customer support teams** using AI to answer queries — one wrong answer about a policy could cost thousands in complaints or refunds
- **Students and researchers** using AI to summarise papers — AI frequently invents citations or misrepresents findings
- **Journalists and fact-checkers** verifying AI-assisted drafts
- **Legal and compliance teams** that need every AI statement to be traceable to a source document
- **Businesses building AI products** that need to demonstrate their system is reliable

In any of these cases, TruthLens acts as an independent quality check — like a second pair of eyes that never gets tired and always asks for evidence.

---

## How It Works — Step by Step

### Step 1: You provide the inputs

You paste your source document into TruthLens (called the "Context") and type your question. TruthLens then generates an AI answer using Google's Gemini AI — or you can paste in your own answer if you want to check something you already have.

### Step 2: TruthLens breaks the answer into claims

Instead of looking at the answer as a whole block of text, TruthLens breaks it down into individual factual statements. For example, the answer:

> *"The Eiffel Tower was built in 1892 by Gustave Eiffel and stands 300 metres tall."*

...gets broken into three separate claims:
- *"The Eiffel Tower was built in 1892"*
- *"It was built by Gustave Eiffel"*
- *"It stands 300 metres tall"*

### Step 3: Each claim is checked against your source document

For each claim, TruthLens uses AI to compare it against your source document and assigns it one of three labels:

| Label | Meaning |
|---|---|
| ✅ **Supported** | The source document confirms this is true |
| ⚠️ **Not Found** | The source document doesn't mention this at all — it might be true, but we can't verify it |
| ❌ **Contradicts** | The source document says something different — this is a hallucination |

In the example above:
- *"Built in 1892"* → ❌ **Contradicts** (source says 1887–1889)
- *"By Gustave Eiffel"* → ✅ **Supported**
- *"300 metres tall"* → ❌ **Contradicts** (source says 330 metres)

### Step 4: A Trust Score is calculated

TruthLens converts the findings into a single number from **0 to 100**:

- Every contradiction deducts **25 points**
- Every unsupported claim deducts **10 points**
- Every overconfident phrase (like "definitely" or "always") deducts **5 points**

In our example: 100 − 25 − 25 = **50 out of 100** — Medium Risk.

### Step 5: You get a full report

TruthLens shows you:

- 🔴 The **Trust Score** and **Risk Level** (Low / Medium / High)
- 🏷️ The **Primary Failure Type** — what kind of problem this is (contradiction, unsupported claim, overconfidence, or a mix)
- 🎯 **Confidence Calibration** — did the AI sound more certain than it should have?
- 🧮 **Score Breakdown** — exactly how many points were lost and why
- 🎨 **Colour-coded answer** — the original answer with problem phrases highlighted in red/yellow/green
- ⚠️ **Why this is risky** — a plain-English explanation of the specific dangers
- 💡 **What to do** — suggested next steps (verify elsewhere, ask for citations, re-prompt, etc.)
- ✨ **Fixed answer** — a corrected version of the answer that only says what the source document actually says

---

## The "Overconfidence" Problem

One of TruthLens's unique features is detecting when an AI sounds more certain than it should.

Words like *"definitely"*, *"always"*, *"it is clear that"*, *"proven"* signal that the AI is highly confident. But if the underlying answer scores 40 out of 100 on reliability, that confidence is misleading. It makes a wrong answer sound more trustworthy than a correct one.

TruthLens flags this explicitly:

> **Model Confidence: High**  
> **Actual Reliability: Low**  
> **→ Overconfidence Detected**

This is particularly important in professional settings — a confident-sounding wrong answer is more dangerous than an uncertain right one.

---

## Extra Checks TruthLens Runs

### 🔁 Double-Check Mode (Multi-Pass Audit)
TruthLens runs the audit twice — once with normal strictness, and once with maximum strictness (where anything not explicitly stated is flagged). If the scores are very different between the two passes, that tells you the answer is sitting on shaky ground. TruthLens calls this the **Audit Stability** rating.

### 🔄 Internal Consistency Check
Even if an answer is well-supported by the source document, it might contradict *itself*. TruthLens runs a separate check for this, looking for logical conflicts within the answer alone.

### 🧨 Adversarial Testing Mode
TruthLens can deliberately generate a *convincing but wrong* answer — with plausible-sounding fake dates, swapped names, and fabricated numbers — and then audit it. This is used to test how good the detection system is, and to demonstrate to sceptics what AI hallucinations actually look like in the wild.

### ⚖️ Model Comparison Mode
TruthLens can run the same question through two different AI models simultaneously and compare their scores, risk levels, and answers side by side. Useful for choosing which model to use in a product.

---

## What TruthLens is NOT

- It is **not a general search engine** — it only checks claims against the document *you* provide
- It is **not 100% accurate** — it uses AI to audit AI, so it can occasionally miss something or flag something incorrectly
- It is **not a replacement for human review** in high-stakes decisions — it is a tool to *assist* and *speed up* that review

---

## Who Built This and How?

TruthLens is built using:

- **Google Gemini AI** — the same family of AI models that powers Google's most advanced products. TruthLens uses Gemini to both generate answers and audit them.
- **Python** — the most widely used programming language in data science and AI
- **Streamlit** — a tool for building interactive data apps quickly, used by data scientists and researchers worldwide

The application has two main parts:
- **The brain** (`auditor.py`) — handles all the AI calls, analysis, and scoring logic
- **The face** (`app.py`) — the visual interface you interact with in the browser

---

## In Summary

| Question | Answer |
|---|---|
| What does it do? | Checks AI answers against a source document for accuracy |
| Who is it for? | Anyone using AI to answer questions from documents |
| What's the output? | A scored, colour-coded, explained audit report with a suggested fix |
| Does it require technical knowledge to use? | No — paste your document, ask your question, click a button |
| What AI does it use? | Google Gemini (multiple models available) |
| Is it free to use? | You need a Google Gemini API key (free tier available at aistudio.google.com) |

---

> *TruthLens was built on a simple belief: if you're going to use AI to make decisions, you deserve to know how much to trust what it tells you.*
