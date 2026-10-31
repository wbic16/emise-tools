# Neuralink & "Neuralese" — A Sourced Brief

(Research brief, 2026-10-30. Every load-bearing claim carries its source. Compiled for the phext-native neuralese spec in this directory.)

## 1. Neuralink's communication vision, in their own material

Neuralink's first product, **Telepathy**, is built on the N1 implant ("the Link"): **1,024 electrodes distributed across 64 flexible threads**, robotically inserted into motor cortex by the R1 robot, fully implanted and wireless. The company has announced a next generation scaling to **~3,000 electrodes** [1][2]. The PRIME study (first human implant: Noland Arbaugh, January 2024; 21 participants enrolled worldwide as of January 2026) is company-reported, not yet peer-reviewed [1][3].

Published throughput is measured as information transfer rate on a cursor grid task. Arbaugh scored **4.6 bits/s in his first research session, later 8.0 bits/s** (May 2024 update) [3]. By the January 2026 "Two Years of Telepathy" update, multiple participants had matched or exceeded the **8–10 bits/s able-bodied mouse range**; one participant exceeded 10 bits/s in his first week [1]. Secondary coverage of an October 2026 update reports a company record of **11.32 bits/s** — company-claimed, not independently verified [4]. Text output via an imagined ten-finger keyboard has reached **up to 40 words/min**; the newer VOICE trial targets **140 words/min** conversational speech decoding [1].

The vision beyond prosthetics is Musk's, and it is explicitly anti-language. To *Wait But Why* (2017): "There are a bunch of concepts in your head that then your brain has to try to compress into this incredibly low data rate called speech or typing… If you have two brain interfaces, you could actually do an **uncompressed direct conceptual communication** with another person" — "**consensual telepathy**" [5]. Repeated on Lex Fridman (2024): concepts are distilled "down to a small number of symbols… **Very lossy compression and decompression**" [6]. The lineage is literary: the **"neural lace" in Iain M. Banks's *Culture* novels** [7]. In March 2025 Neuralink reportedly trademarked "Telepathy" (and "Telekinesis") [2].

## 2. The word "neuralese" — three lineages, one negative finding

**Negative finding: Neuralink does not use the word.** Their vocabulary is "Telepathy," "conceptual telepathy/communication," "neural lace." "Neuralese" is not their term.

**(a) Philosophy of mind.** "Mentalese" names the hypothesized language of thought (Sellars 1964; Fodor's *The Language of Thought*, 1975) [8]. **"Neuralese" is Paul Churchland's rival coinage** (*A Neurocomputational Perspective*, 1989, as cited by Andy Clark): where Fodor's mentalese is symbolic and sentence-like, Churchland's inner medium is high-dimensional **activation vectors**, and a spoken sentence is merely a "one-dimensional projection" of a richer neural state [9].

**(b) AI research.** **Andreas, Dragan & Klein, "Translating Neuralese" (2017)**: multi-agent networks coordinating through a learned channel exchange "recurrent state vectors — an artificial language we might call 'neuralese'" [10]. The modern LLM usage descends from this: latent-space reasoning and inter-model communication via continuous embeddings. Landmark: **Coconut** (Hao et al., Dec 2024; COLM 2025), feeding an LLM's last hidden state back as its next input embedding — a "continuous thought" [11]. A 2026 philosophy paper traces the term from Andreas et al. to today's latent chain-of-thought debate [12]. Neighboring pop phenomenon: **GibberLink** (ElevenLabs London Hackathon, Feb 2025) — voice agents switching to ggwave data-over-sound; a pre-existing human-designed protocol, not an invented language [13].

## 3. Bandwidth numbers, grounded

| Quantity | Figure | Source |
|---|---|---|
| Human speech, information rate | **~39 bits/s**, near-constant across 17 languages | Coupé et al., *Science Advances*, 2019 [14] |
| Silent reading (English, adults) | **238 wpm** non-fiction, 260 fiction; oral reading 183 wpm | Brysbaert meta-analysis, 2019 [15] |
| Natural conversation | ~160 wpm | cited in Willett et al. 2023 [16] |
| Neuralink cursor control | 4.6 → 8.0 bits/s (2024); ≥10 bits/s (2026); mouse ≈ 8–10 bits/s | Neuralink updates [1][3] |
| Best academic speech BCI | **62 words/min**; WER 9.1% (50-word vocab), 23.8% (125k vocab) | Willett et al., *Nature*, 2023 [16] |

The asymmetry: a BCI cursor channel (~10 bits/s) only now matches a mouse and remains below speech's ~39 bits/s; speech-decoding BCIs win by riding the brain's own language machinery rather than replacing it.

## 4. Constraints: why raw neural signal is not yet a "language"

- **No shared codebook.** Decoders are trained per brain. Tang et al. (UT Austin, *Nature Neuroscience* 2023): **16 hours of fMRI per subject**; a decoder trained on one brain performed "barely above chance" on another's, and decoding collapses without the subject's cooperation [17]. Neuralink likewise stresses every implant "must adapt to individual neural architecture" [1].
- **Decoders read trained intentions, not free thought.** Working systems decode attempted movement or speech against known targets, supervised. Nothing published decodes arbitrary conceptual content.
- **The conduit-metaphor critique.** William Benzon (2026 working paper), after Reddy (1979): much thinking is *constituted by* language, so there may be no uncompressed original to transmit. Contested, not settled — but it is the main philosophical pushback [18].
- **Inter-brain variability and drift.** Thread retraction cost the first participant signal; pooled multi-participant models reportedly do not yet beat per-participant models online [4].

**Caution flags:** all Neuralink performance figures are company-reported (a NEJM submission is reported but unpublished); the 11.32 bits/s record rests on secondary coverage [3][4]. The 200 Mbps "raw data" N1 figure circulating on comparison sites was not confirmed in Neuralink's own material and is excluded.

## Sources

1. Neuralink, "Two Years of Telepathy" (Jan 2026) — https://neuralink.com/updates/two-years-of-telepathy/
2. Neuralink N1 guide (secondary, citing Neuralink disclosures) — https://www.insidedeeptech.com/neuralink-n1-implant-r1-robot-clinical-trials-full-guide/
3. Neuralink PRIME study summary of company updates — https://muskularity.com/companies/neuralink-prime/
4. Neuralink October 2026 update, as reported — https://www.insidedeeptech.com/neuralink-n1-implant-r1-robot-clinical-trials-full-guide/
5. Musk to *Wait But Why* (2017), quoted — https://cleantechnica.com/2017/04/24/musk-tweets-neuralink-will-prevent-artificial-intelligence-becoming/
6. Lex Fridman Podcast #438 transcript (2024) — https://metacast.app/podcast/lex-fridman-podcast/9wucYRkO/438---elon-musk-neuralink-and-the-future-of-humanity/ca3Fekm2
7. Neural lace / Banks lineage — https://futuretimeline.net/blog/2019/07/21.htm
8. Piccinini, "Neural Hardware for the Language of Thought" — https://arxiv.org/pdf/2510.10251
9. Stanley, "Tracing the Extended Mind" (Clark on Churchland 1989), *Religions* 2025 — https://www.mdpi.com/2077-1444/16/2/189
10. Andreas, Dragan & Klein, "Translating Neuralese" (2017) — https://ar5iv.labs.arxiv.org/html/1704.06960
11. Hao et al., Coconut (2024) — https://arxiv.org/abs/2412.06769v3
12. van Gerven Oei, "Neuralese, Thinkish, and Poetry" (2026) — https://philpapers.org/archive/VANNTA-20.pdf
13. GibberLink (2025) — https://www.fanaticalfuturist.com/2025/06/two-ais-started-chatting-with-one-another-in-a-new-bot-language/ ; https://github.com/PennyroyalTea/gibberlink
14. Coupé et al., *Science Advances* 5(9), 2019, DOI 10.1126/sciadv.aaw2594
15. Brysbaert, *Journal of Memory and Language* 109 (2019), DOI 10.1016/j.jml.2019.104047
16. Willett et al., "A high-performance speech neuroprosthesis," *Nature* 620 (2023) — https://pubmed.ncbi.nlm.nih.gov/37612500/
17. Tang et al., *Nature Neuroscience* 26 (2023), DOI 10.1038/s41593-023-01304-9 — https://patentlyo.com/patent/2026/09/who-owns-mind-reading.html
18. Benzon, "Direct Brain-to-Brain Thought Transfer" (v2, 2026) — https://www.academia.edu/44109360/Direct_Brain_to_Brain_Thought_Transfer_A_High_Tech_Fantasy_that_Wont_Work_Version_2
