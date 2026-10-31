# Candidate Users for Phext-Native Neuralese — Sourced Brief

(Research brief, 2026-10-30. Speculative fits are marked as such.)

**Framing.** The strongest near-term candidates are not "the general public." They are (1) tiny, highly motivated BCI cohorts whose output is currently flattened to cursor clicks or linear text, (2) speech-neuroprosthesis/AAC communities with the same flattening problem at much larger scale, (3) AI researchers already demonstrating latent communication but lacking an interoperable, inspectable envelope, and (4) PKM/exocortex power users already living in linked, addressed text.

## 1. BCI recipients and their platform ecosystems

**Neuralink PRIME / VOICE participants.** PRIME (ClinicalTrials.gov NCT06429735; estimated US enrollment 15) decodes motor intent to cursor control, computer use, gaming/CAD and robotic-arm control; Neuralink reported 21 participants worldwide in January 2026 and 26 by June 2026, including seven in GB-PRIME at UCLH. Its VOICE feasibility study (NCT07224256, planned n=6) reported one ALS participant reaching 75 words/min at 5.8% word-error rate on a 125,000-word vocabulary in week one — company-reported, not yet peer-reviewed. *Gap:* output is ephemeral action or a text/voice stream; no persistent, addressable record of decoded units that the user, clinicians, or an assistant model can link, revisit, or augment. *Reachability:* high visibility but gated — via trial teams, publications and the patient registry; vendor/clinician integration required (speculative).

**Synchron, Blackrock/BrainGate, Paradromics, Precision.** A 2026 BCI tracker estimates ~150+ implanted people across programs: Blackrock NeuroPort 40+, BrainGate 35+, Synchron Stentrode 20+, Precision Layer 7 15+, Paradromics Connexus 3. Synchron's Apple-protocol patients use motor intent as an HID — point-and-click on iPhone/iPad/Vision Pro. Paradromics obtained an FDA IDE for a fully implantable speech BCI and reported a first permanent Connexus implant in June 2026. Precision's Layer 7 has been tested in 37+ people but is cleared only for up to 30-day temporary monitoring — a platform partner candidate more than a communication-user cohort today. *Gap:* HID clicks and decoded words discard intent structure; one decoded unit could carry a gist for the screen, a latent digest for a personal model, and links to routines/people/prior utterances. (Speculative; clinically regulated.)

## 2. Speech neuroprosthesis labs and AAC users

**Academic speech labs.** UCSF's Chang lab decoded attempted speech to a digital avatar at 78 words/min (253-electrode ECoG, 1,024-word vocabulary), and in 2026 reported simultaneous speech-and-gesture decoding — communication is multimodal, while output channels remain text/voice/avatar. Stanford's Neural Prosthetics Translational Lab reported 62 words/min with a 125,000-word vocabulary. UC Davis's BrainGate2 participant Casey Harrell is the clearest "power user": years of home use and, in 2026 coverage, 183,000+ sentences / ~2M words over 3,800+ hours. *Gap:* high-volume users generate a life's worth of utterances as flat transcripts; addressed scrolls could become their searchable, linkable external memory, with latent bands preserving context. *Reachability:* excellent for research pilots — named labs, published authors, open trial infrastructure.

**AAC community.** ASHA estimates cited in a 2025–26 speech-generating-device market report put potential AAC benefit at ~5M Americans and ~97M people globally; Lingraphica reports 10,000+ cumulative device users. Today's tools are phrase banks, symbol grids and spelling with word prediction. *Gap:* pre-stored phrases are islands; a coordinate-linked personal corpus plus model-rehydratable digests could support faster, more personal formulation while the gist band stays human-readable for family and clinicians. *Reachability:* ASHA/ISAAC, speech-language pathologists, SGD vendors — large, but adoption is clinical and reimbursement-driven (speculative as a format channel).

## 3. Latent-communication AI researchers and agent-framework communities

**Meta FAIR — Coconut.** "Training Large Language Models to Reason in a Continuous Latent Space" (Hao et al.) feeds the last hidden state back as the next input embedding — "continuous thought." **LatentMAS** (Zou et al., 2025) extends this to multi-agent systems: agents share a latent working memory, claiming lossless transfer vs. text mediation, 70.8–83.7% fewer output tokens and 4–4.3× faster inference; code is open-source. **Tsinghua's Cache-to-Cache (C2C)** projects and fuses KV-caches directly between different LLMs, beating text communication on accuracy/latency in its experiments. *Gap:* in-process or same-cluster mechanisms with no durable, cross-vendor, human-auditable interchange artifact. Phext's contribution would be the envelope: stable coordinates, a gist for audit, a quantized digest for rehydration, links for provenance. Whether quantized digests can bridge *different* models' latent geometries is unproven (speculative). *Reachability:* highest in this brief — arXiv authors, public GitHub repos.

**Framework/protocol communities.** AutoGen agents converse via structured text messages; LangGraph passes text lists between graph nodes; CrewAI likewise. Google's Agent2Agent (A2A) protocol — now Linux Foundation-governed — deliberately keeps agents opaque and exchanges text/files/JSON, not internal state. *Candidate play:* an A2A/framework extension profile where a message part carries a phext coordinate + gist + digest reference. *Reachability:* open-source maintainers and protocol working groups; the most plausible distribution path for the model-to-model use case.

## 4. Adjacent power users: PKM, exocortex, quantified self

**Obsidian / Logseq / Roam users.** Thought stored as local, linked text already: Obsidian (local-first Markdown, bidirectional links, large plugin ecosystem), Logseq (block-addressable outliner), Roam ("networked thought"). *Gap:* addresses are local (file/block), links carry no latent representation, and there is no shared 11-D coordinate scheme across people, agents and devices. *Reachability:* the easiest design-partner pool — public forums/Discords, plugin developers, no gatekeeper.

**Quantified Self.** QS meetups have run in ~71 cities. *Gap:* self-data sits in app silos as charts; a phext exocortex could link a measurement scroll to context, interventions and an AI-readable digest. Fit is real but diffuse (partly speculative).

**Bottom line.** Recruit in this order: (i) latent-communication researchers and agent-framework maintainers for the format itself, (ii) PKM plugin builders for a usable exocortex prototype, (iii) speech-lab investigators for a research pilot, and only then (iv) implant vendors/AAC channels, where the need is strongest but regulation and gatekeeping are decisive.

## Sources

- Neuralink PRIME record: https://ctv.veeva.com/study/precise-robotically-implanted-brain-computer-interface
- GB-PRIME (7 participants, UCLH): https://www.uclhospitals.brc.nihr.ac.uk/news/seven-patients-now-participating-neuralink-trial
- Neuralink VOICE 75 wpm report: https://insidebci.com/news/2026-10-29-neuralink-voice-speech-75-words-per-minute-word-error-rate-als/
- BCI patient cohorts by program: https://bciintel.com/who-is-getting-brain-implants/
- Synchron + Apple Vision Pro / HID: https://ctc2017corp.web.stage.q4inc.com/files/doc_news/Synchron-Announces-First-Use-of-Apple-Vision-Pro-with-a-Brain-Computer-Interface-2024.pdf
- Synchron iPad control via Apple BCI HID: https://www.redsharknews.com/synchron-uses-new-apple-tech-to-allow-als-patient-to-control-an-ipad
- UCSF Chang lab 78 wpm avatar: https://engineerine.com/ucsf-bci-speech-restoration-digital-avatar-paralysis/
- UC Davis BrainGate2 speech BCI: https://neuroengineering.ucdavis.edu/news/new-brain-computer-interface-allows-man-als-speak-again
- AAC/ASHA estimates and SGD market: https://www.strategicmarketresearch.com/market-report/speech-generating-devices-market
- Coconut: https://arxiv.org/abs/2412.06769v3
- LatentMAS: https://arxiv.org/abs/2511.20639
- Cache-to-Cache: https://arxiv.org/html/2510.03215v2
- A2A protocol overview: https://fast.io/resources/a2a-protocol-google-agents/
- PKM tools: https://www.saashub.com/best-note-taking-software/c/knowledge-management
- Quantified Self gatherings study: https://www.citedrive.com/en/discovery/on-the-cult-of-the-individual-the-quantified-self-public-gatherings-self-tracking-and-individualism
