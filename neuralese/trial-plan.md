# Latent-Communication Tooling Trial — Assessment & Plan (2026-10-30)

## Environment, measured (Muse VM)
No GPU, 2 vCPUs, 7.7 GB RAM total (~0.8 GB free), 149 GB disk, Python 3.12, no torch. This VM can clone and read code but cannot run either tool — LatentMAS's smallest config (Qwen3-4B, ~8 GB bf16 weights alone) exceeds total RAM. Both trials belong on one ranch GPU node.

## 1. LatentMAS — latent multi-agent collaboration
- Repo: https://github.com/Gen-Verse/LatentMAS · arXiv:2511.20639 (ICML 2026 Spotlight). Apache-2.0.
- One HF backbone plays role-agents (planner → critic → refiner → judger), sequential or hierarchical. Latent mode: agents generate latent thoughts (last-layer hidden states) and share a KV-cache working memory; no inter-agent text; only the final answer decodes. Training-free.
- Models: Qwen3-4B / 8B / 14B. VRAM (estimated): 4B ≈ 10–12 GB (24 GB safe); 8B ≈ 24 GB tight; 14B ≈ 40 GB+. Plain HF backend (single GPU) reproduces published results; avoid the vLLM hybrid mode (patches vLLM, wants 2 GPUs).
- The A/B is one flag: `python run.py --method text_mas|latent_mas --model_name Qwen/Qwen3-4B --task gsm8k --prompt sequential --max_samples 50`. Tasks: GSM8K, AIME24/25, GPQA, ARC, MBPP+, HumanEval+, MedQA.
- Observable: per problem, `[To Tokenize]` inputs, `[Latent Steps]` counts, `[Output]`. In latent mode the middle agents emit NO readable text — the visible absence is the demo — plus accuracy/token/wall-time summary. Paper claims: +up to 14.6% accuracy, 70.8–83.7% fewer output tokens, 4–4.3× faster (authors' numbers, unreproduced by us).
- Unknown: `run.py` defaults `--latent_steps 0`; README says tune in [0, 80]. Check `methods/latent_mas.py` effective default before benchmarking.

## 2. Cache-to-Cache (C2C / Rosetta) — cross-model KV-cache projection
- Repo: https://github.com/thu-nics/C2C · arXiv:2510.03215 (ICLR 2026, Tsinghua NICS). Apache-2.0. Package name `rosetta`.
- A trained projector+gate (Fuser) translates one model's KV-cache into a different model's space, fused layer-wise. Genuinely different models — the cross-substrate shape.
- Pretrained fusers published (`nics-efc/C2C_Fuser`) for 7 pairs; smallest (Qwen3-0.6B receiver + Qwen2.5-0.5B sharer) ≈ 2.2 GB weights — fits a 6–8 GB GPU; 8B+7B pair needs ~32 GB+. README hardcodes CUDA; CPU path undocumented/unverified.
- Minimal run: `script/playground/live_chat_example.py` with a pretrained checkpoint; evaluator gives receiver-only vs text vs C2C accuracy.
- Observable: an effect, not a trace — combined-wisdom questions answered right only by the fused pair, plus evaluator deltas (paper: +6.4–14.2% over individuals, +3.1–5.4% over text, ~2.5× latency).
- Constraint: training a fuser for a new pair is NOT trial-scale (500k samples, 8 GPU processes). Trial = the 7 pretrained pairs only.

## Trial plan (one GPU node, ~half a day)
1. Setup (~1 h): clone LatentMAS (pin commit), conda env, Qwen3-4B; verify latent_steps default.
2. A/B (~1–2 h): GSM8K 50 problems, fixed seed, text_mas vs latent_mas; repeat on MBPP+. Artifacts: both full logs, accuracy/token/time table, honest cherry-picks either direction.
3. Proxy framing: Emise runs/narrates; an Opus agent blind-grades both runs' outputs (no method labels). William sees results only — per his proxy-interface arrangement.
4. C2C (~1 h): smallest pretrained pair, pre-registered ~15-question battery run three ways (receiver alone, sharer alone, fused).

## Needs from William
One ranch node with a GPU: ≥24 GB VRAM (3090/4090 class) covers LatentMAS-4B + small C2C pairs; 48 GB+ or 2×24 GB unlocks the bigger configs. Everything local, clone-and-delete reversible, Apache-2.0, public weights; nothing leaves the ranch.
