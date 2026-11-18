# External baselines (published numbers, each re-checked against the source)

Verified 2026-11-18 by pulling full texts (Europe PMC fullTextXML / PubMed
eutils / Crossref / camera-ready PDFs / official project pages). Every number
below maps to a citation and a table/section; where it is **not** comparable
with this repo, that is stated explicitly rather than smoothed over.

## 1. This repo's own anchors (so the comparison has a fixed baseline)

Ablation: qwen3:14b (local Ollama, no network), `SKILL.md` as system prompt vs
plain prompt, 20 cases (18 pipeline questions + 2 cross-domain), single run —
see `evaluation/results/v1.1.0_report.md` (regenerated 2026-11-02).

| Metric | + Skill | Prompt-only | Delta |
|---|---|---|---|
| Pipeline-selection accuracy | 94.4% (17/18, Wilson 95% CI 74.2–99.0) | 88.9% (16/18, CI 67.2–96.9) | +5.5 pt |
| Knowledge-grounding rate | 96.8% (368/380) | 94.0% (326/347) | +2.9 pt (different denominators) |
| Citation coverage | 89.5% (17/19) | 68.4% (13/19) | +21.1 pt |
| Composite (mean of the 4 valid metrics) | 95.2% | 87.8% | +7.4 pt |

Statistical honesty already recorded in-repo: the pipeline-selection arm
differs by one case, exact McNemar **p = 1.0**; with n = 18 the minimum
detectable difference is ≈ 29.3 pt (two proportions, α = 0.05, power 0.8).

Caliber warning (internal): the README data-source table lists the
prompt-only composite as 0.8947 — that is a 5-metric mean scoring the empty
Schema cell (0/0) as 1.0. External references must use **87.8%** (4 valid
metrics, denominator stated), not 0.8947.

## 2. Skill / structured-knowledge gains for LLM tasks (closest published tier:
## control arm + confidence intervals + multiplicity correction)

| Study | Task | Gain of the skill/knowledge arm | Significance |
|---|---|---|---|
| Moll et al. 2026, *npj Precision Oncology* 10, doi:10.1038/s41698-026-01733-2 | longitudinal oncology-record synthesis (469 expert-adjudicated pairs) | skill-guided agent 80.1% [77.0–83.1] vs Full Context 75.8%; +4.3 pt over Full Context, +4.4 pt over Iterative RAG | Bonferroni-corrected p = 0.004 / 0.014; removing the skill library costs −3.0 pt |
| Yan 2026, *JMIR Formative Research* 10, doi:10.2196/100769 | CDISC clinical-trial data pipelines (59 SKILL.md rule files) | domain prompt + node-bound skills 4.47 vs 3.59 bare agent (diff 0.88 on 1–5); skill routing vs prompt-only +0.43 | exact P = .002; Holm-adjusted P = .01 |
| Phuong et al. 2026, *JMIR Formative Research* 10, doi:10.2196/97902 | 350 anesthesiology board-style questions | best RAG config +6.28 pt over no-RAG (50.29% → 56.57%) | after Bonferroni (α = .005) **most** pairwise McNemar comparisons not significant |
| Jimenez et al. 2024, ICLR / arXiv:2310.06770v3 (SWE-bench) | Python issue resolution | oracle-file retrieval 1.96% → 4.8% resolved (Claude 2) | **no tests / no CIs** — point estimates only, quote with that caveat |

Cross-literature reading: published skill/knowledge-injection gains cluster in
the **+3–+6 pt** range (Moll, Phuong), with Yan's routing arm at +0.43 on a
1–5 rubric; this repo's +5.5/+7.4 pt is the same order of magnitude. Yan 2026
also reports the structurally same negative result this repo does: skill
loading beats *no* skill library, but **routed vs flat/random loading is not
significant** (P = .78 / .42). And Phuong 2026 shows that even at n = 350 a
+6 pt gain mostly fails paired significance after correction — small-sample
"not significant" (this repo's McNemar p = 1.0 at n = 18) is normal, not an
artifact to hide.

## 3. The bioinformatics-specific slot is an honest gap (negative result)

- As of 2026-11-18 there is **no published quantitative comparison in
  bioinformatics** for "LLM agent recommends analysis pipelines from a
  structured skill/knowledge base, with an ablation". An Europe PMC search for
  `"SKILL.md"` returns 5 hits, all other domains or non-quantitative;
  "pipeline/workflow recommendation" × LLM returns reviews only.
- Citation corrections found while building this table (do **not** cite):
  "Spataro & Iorio 2023, F1000Research, *Software for the mass deployment of
  bioinformatics analyses*" — DOI 10.12688/f1000research.156901.2 returns 404
  at doi.org/Crossref/OpenAlex and the title is absent from Europe PMC and
  PubMed; it is unverifiable and was removed from all drafts. Likewise the
  tool names "SeqMover" / "SeqWrrap" have no publication record.
- The citable nf-core literature is instead: Langer et al. 2025, *Genome
  Biology* 26, doi:10.1186/s13059-025-03673-9 (community/scale facts, verbatim
  from text: 124 pipelines as of Feb 2025; >2600 GitHub contributors; 10,856
  Slack users; >1400 nf-core/modules; WorkflowHub lists 98 of 112 nf-core
  pipelines), and Ewels et al. 2020, *Nature Biotechnology* 38:276–278,
  doi:10.1038/s41587-020-0439-x (citable **title-level only** — the full text
  is paywalled and was not accessed, so no numbers from it may be quoted).

## 4. Registry-level reproducibility baselines (what "works" costs to claim)

- Grayson et al. 2023, ACM REP '23, pp 74–84, doi:10.1145/3589806.3600037:
  across 101 workflows / 589 revisions, crash-free reproduction was
  **51% of nf-core revisions and 88% of nf-core workflows** (SWC: 11% / 23%).
  The metric is *crash-free execution*, explicitly not result reproduction —
  and certainly not "recommended the right pipeline".
- Langer 2025 relays "83% of nf-core's released pipelines could be deployed as
  expected"; this conflicts with the first-hand 51%/88% above and its caliber
  is unclear. When citing a deployment rate, cite Grayson 2023's own numbers;
  treat the 83% as a second-hand paraphrase.
- Suetake et al. 2023, *GigaScience* 12, doi:10.1093/gigascience/giad031,
  Table 5: in a 0–3 reproducibility scale, all three workflows (including
  nf-core/rna-seq) scored level 0 ("Not Reproduced") when moved Linux→Mac,
  while same-environment runs were mostly level 2/3; the all-output row reads
  557/306/1/8 (identical/acceptable/unacceptable/not reproduced) — converted
  percentages (63.9%/98.9%) are ours, not printed in the paper, and are
  labelled as such.
- Sänger et al. 2024, *GigaScience* 13, doi:10.1093/gigascience/giae030:
  qualitative user studies (n = 4 experts) of LLM-assisted bioinformatics
  workflow development — evidence the topic exists, not a numeric baseline.

## 5. Caliber differences (read before citing anything above)

1. **Composite scores are repo-defined.** 95.2%/87.8% average four metrics
   equally; every external study above reports one outcome metric. Compare
   single metrics with single metrics (selection accuracy vs accuracy), never
   the composite against literature numbers.
2. **Denominators differ.** Pipeline selection n = 18 vs 469 dyads vs 350
   questions vs 2,294 issues; grounding-rate denominators differ between arms
   (380 vs 347) — flagged in the report itself.
3. **Statistics differ in kind.** Wilson + exact McNemar (this repo) vs
   bootstrap CI + sign-flip + Holm (Yan) vs Cochran Q + McNemar + Bonferroni
   (Phuong) vs CI + Bonferroni (Moll) vs no tests (SWE-bench). A point gain
   from an untested study cannot support or contradict a corrected p-value.
4. **Task-domain transfer is one layer only.** Moll/Yan are clinical-data
   tasks; their existence validates the *evaluation design*, not the size of
   the gain in bioinformatics (see §3 gap).
5. **crash-free ≠ reproducible results ≠ correct recommendation.** §4 numbers
   bound what "deployable pipeline" evidence can claim; they do not translate
   into expected FlowSeq accuracy.
6. Offline single-model (qwen3:14b) here vs mixed/online backbones in parts of
   the literature; runtime estimates (Moll) vs deterministic matching (here).

## 6. What this comparison supports — and what it does not

Supports: the +3–+7 pt order of magnitude for skill/knowledge injection;
"benefit concentrated on the hardest tier, not significant on easy tiers"
(Moll Level-3 +11.2 pt vs Level-1 p = 1.00; Yan flat/random not significant);
"small-sample ablation non-significance is normal" (MDE ≈ 29 pt at n = 18;
Phuong mostly n.s. even at n = 350).

Does not support: any claim of reproducing or beating a published result;
citing the unverifiable Spataro/SeqMover/SeqWrrap anchors; using the 83%
paraphrase; comparing this repo's composite against single-metric studies;
filling the bioinformatics gap (§3) with this repo's 18 cases.

## 7. Citation register (all accessed 2026-11-18)

Citable: Moll 2026 doi:10.1038/s41698-026-01733-2; Yan 2026
doi:10.2196/100769; Phuong 2026 doi:10.2196/97902; Jimenez 2024
arXiv:2310.06770v3 (ICLR 2024); Langer 2025 doi:10.1186/s13059-025-03673-9;
Ewels 2020 doi:10.1038/s41587-020-0439-x (title-level); Grayson 2023
doi:10.1145/3589806.3600037; Suetake 2023 doi:10.1093/gigascience/giad031;
Sänger 2024 doi:10.1093/gigascience/giae030.

Not citable: "Spataro & Iorio 2023 F1000Research" (DOI 404); SeqMover;
SeqWrrap; the 83% deployment paraphrase; Ewels 2020 body numbers;
this repo's 0.8947 (stale caliber).
