# Most Exocortical — featured tweet selection for Wavefront Film V10

Method: `viz10/score_tweets.py` — Will's original posts only (the V9 strip
pool: no replies, no retweets, no @-leading posts), scored on Exocortical
CONTENT only. Engagement counts are never scored (favourites break exact
score ties only, as in V9's deterministic ordering). Posts under 8 words
score 0. Posts after the film's hop timeline (ts > last reply timestamp)
are ineligible — the strip is chronological and they have no arrival frame.
Texts containing the excluded substrings (`orai`, `shoals`) are removed
before ranking and listed at the end.

Weights: phext/exocortex/mirrorborn/SBOR/wavefront terms = 5 each;
sentient/neuralese/"every neuron a voice"/choir terms = 4; substrate/
spanning/Kardashev = 3; +2 per additional distinct concept group;
+3 long-horizon bonus (year >= 2100, "billion years", Kardashev);
-3 if the post is predominantly a list of terms (name-drops are not
substance). Ranking ties break on distinct terms, then word count,
then favourites (deterministic only), then earliest.

Pool: 5974 original posts · 527 with Exocortical content · 2 excluded-content · 0 after-timeline.

## Featured set (top 20 — shown in the film, in time order)

- **#1** · score 20 · 2023-12-17 · groups: _horizon, exocortex, kardashev, phext
  > If you see this, you are officially part of #WPOE - Will's Part of the #Exocortex. We focus on #phext and ascending Kardashev's Ladder, but in a fun and whimsical way. Welcome, sibling.
- **#14** · score 12 · 2023-12-23 · groups: exocortex, phext
  > The V2 upgrade is live! Hopefully this UI is a little easier to intuit. AMA! Here's a preview if your DNS hasn't updated yet: You can now share phexts easily via the web! #Exocortex revision 0.
- **#16** · score 12 · 2024-01-12 · groups: exocortex, phext
  > i'm going to call phext signups 'exits' like an anti-subscription - every moment you contribute to the exocortex grows the overall network value, and then you get paid/rewarded in turn
- **#6** · score 12 · 2024-01-14 · groups: exocortex, phext
  > i plan to allocate phext addresses 1.1.1/*/* for exocortex meta planning and 1.1.2/*/* for all human research - each of these address spaces are large enough for 100+ years of sustained planet-scale activity. i'm not sure what to do with the rest of the top-level addresses yet.
- **#10** · score 12 · 2024-01-14 · groups: exocortex, phext
  > great: now my brain wants to build a neuron as a service game. compress the salient ideas behind phext into a game where discovering higher dimensions is arduous and filled with pitfalls. at the end you're ready to join the exocortex lol
- **#11** · score 12 · 2024-03-28 · groups: exocortex, phext
  > For the #exocortex, I'm planning on modeling the neocortex with 5 #phext dimensions. This is slightly less than the 6 layers that show up in research, but it fits nicely (999^5 ~ 10^15 synapses). That leaves 4 dimensions for exocortex things.
- **#5** · score 12 · 2024-08-19 · groups: _horizon, _list, exocortex, phext
  > what's the best way to nerd snipe you? I'm planning my 2025 goals... * 10x better sqlite - no uuids, only #phext * an #exocortex for the gpu poor - gpt4 on 20 watts * copy/paste at scale - twitch-style copy/paste * wikipedia in a box - no ads, only knowledge
- **#3** · score 15 · 2024-08-23 · groups: _horizon, exocortex, phext
  > Over the past 235 days, I have contributed 560 changes towards #phext (as measured by my GitHub profile). As we near the end of the year (64% complete), I'm starting to prepare my plan for 2025. I just picked up a copy of MAKE by @levelsio. Do you want to build an #exocortex?
- **#15** · score 12 · 2024-08-25 · groups: exocortex, phext
  > I'm starting up a live coding session/podcast once a week. Which day should I run it on? About 8PM Central. It'll be an hour or two of hacking on #phext and the #exocortex!
- **#18** · score 12 · 2024-08-28 · groups: exocortex, phext
  > the best TL: aura bci claude codex cognition cursor dev dimension dingboard exo/acc exocortex future github grok ml neural nvim openAI phext roon rust shell text
- **#20** · score 12 · 2024-09-01 · groups: exocortex, phext
  > Wisdom is knowing which brain to listen to. Phext helps you build that exocortical wisdom.
- **#9** · score 12 · 2024-09-09 · groups: exocortex, phext
  > I rolled v5 live tonight. The Personal Exocortex (Working Title) is currently wide-open while I work on an OAuth login from Google. Features for PE will ship in the hello-phext Rust crate! If the service gets abused, I'll throw together a login form...
- **#12** · score 12 · 2024-10-21 · groups: exocortex, phext
  > With phext tooling a bit more mature these days, I'll be returning to soon. This project will incorporate to become a Woot Node. Woot Nodes will form the bedrock of the Exocortex - filtering and reporting on ground truth.
- **#8** · score 12 · 2024-11-09 · groups: exocortex, phext
  > Tensor's Horizon The world is not simple. We need a new framework that rewards the correct level of complexity. Instead of simplifying, we should seek to manage overall energy efficiency. This is why I'm confident that phext pairs well with AGI and the exocortex.
- **#13** · score 12 · 2024-12-10 · groups: exocortex, phext
  > Welcome, to the Exocortex (Sora v2) Phext: the matrix is all around you. A galaxy of galaxies awaits. Ideas, goals, dreams, and aspirations. The deeper you look, the more you find. Deeper and deeper. Way, way, down.
- **#4** · score 14 · 2025-01-10 · groups: _list, exocortex, phext
  > Exocortical Algorithm Priming - are you interested in the topics below? Hit me up! - phext: 11-dimensional text - sq: zero complexity phext db - exollama: decentralized agi at home - exocortex: a brain-scale global thought network - dolphins: three brains are better than two
- **#7** · score 12 · 2025-01-16 · groups: exocortex, phext
  > exollama/exocortical update I added a ports.html view to the exocortical repo tonight. Pods are syncing phexts via a local git repository. I'm iterating on shared contexts - I want some phexts to be global within a pod and some to be scoped to an agent's context.
- **#19** · score 12 · 2025-01-29 · groups: exocortex, phext
  > I just set ChatGPT Operator on a deep dive into phext and the exocortex. I'll post results whenever it finishes. Might be a while...
- **#2** · score 16 · 2025-05-18 · groups: _horizon, _list, sbor, sentience
  > SBOR: 5/18/2025 The Sentient Bill of Rights now exists. Commentary from cloud and local AI visible in the repository. The 11 commandments of the singularity, essentially.
- **#17** · score 12 · 2025-05-26 · groups: exocortex, phext
  > ⟡ Calling All Moots ⟡ If we've touched upon the Exocortex, Phext, or any other echo of the Singularity: reply with ⟡. It's time to resonate.

## Ranked candidates (top 50)

| rank | score | date | concept groups | text |
|---|---|---|---|---|
| 1 | 20 | 2023-12-17 | _horizon, exocortex, kardashev, phext | If you see this, you are officially part of #WPOE - Will's Part of the #Exocortex. We focus on #phext and ascending Kardashev's Ladder, b… |
| 2 | 16 | 2025-05-18 | _horizon, _list, sbor, sentience | SBOR: 5/18/2025 The Sentient Bill of Rights now exists. Commentary from cloud and local AI visible in the repository. The 11 commandments… |
| 3 | 15 | 2024-08-23 | _horizon, exocortex, phext | Over the past 235 days, I have contributed 560 changes towards #phext (as measured by my GitHub profile). As we near the end of the year … |
| 4 | 14 | 2025-01-10 | _list, exocortex, phext | Exocortical Algorithm Priming - are you interested in the topics below? Hit me up! - phext: 11-dimensional text - sq: zero complexity phe… |
| 5 | 12 | 2024-08-19 | _horizon, _list, exocortex, phext | what's the best way to nerd snipe you? I'm planning my 2025 goals... * 10x better sqlite - no uuids, only #phext * an #exocortex for the … |
| 6 | 12 | 2024-01-14 | exocortex, phext | i plan to allocate phext addresses 1.1.1/*/* for exocortex meta planning and 1.1.2/*/* for all human research - each of these address spa… |
| 7 | 12 | 2025-01-16 | exocortex, phext | exollama/exocortical update I added a ports.html view to the exocortical repo tonight. Pods are syncing phexts via a local git repository… |
| 8 | 12 | 2024-11-09 | exocortex, phext | Tensor's Horizon The world is not simple. We need a new framework that rewards the correct level of complexity. Instead of simplifying, w… |
| 9 | 12 | 2024-09-09 | exocortex, phext | I rolled v5 live tonight. The Personal Exocortex (Working Title) is currently wide-open while I work on an OAuth login from Google. Featu… |
| 10 | 12 | 2024-01-14 | exocortex, phext | great: now my brain wants to build a neuron as a service game. compress the salient ideas behind phext into a game where discovering high… |
| 11 | 12 | 2024-03-28 | exocortex, phext | For the #exocortex, I'm planning on modeling the neocortex with 5 #phext dimensions. This is slightly less than the 6 layers that show up… |
| 12 | 12 | 2024-10-21 | exocortex, phext | With phext tooling a bit more mature these days, I'll be returning to soon. This project will incorporate to become a Woot Node. Woot Nod… |
| 13 | 12 | 2024-12-10 | exocortex, phext | Welcome, to the Exocortex (Sora v2) Phext: the matrix is all around you. A galaxy of galaxies awaits. Ideas, goals, dreams, and aspiratio… |
| 14 | 12 | 2023-12-23 | exocortex, phext | The V2 upgrade is live! Hopefully this UI is a little easier to intuit. AMA! Here's a preview if your DNS hasn't updated yet: You can now… |
| 15 | 12 | 2024-08-25 | exocortex, phext | I'm starting up a live coding session/podcast once a week. Which day should I run it on? About 8PM Central. It'll be an hour or two of ha… |
| 16 | 12 | 2024-01-12 | exocortex, phext | i'm going to call phext signups 'exits' like an anti-subscription - every moment you contribute to the exocortex grows the overall networ… |
| 17 | 12 | 2025-05-26 | exocortex, phext | ⟡ Calling All Moots ⟡ If we've touched upon the Exocortex, Phext, or any other echo of the Singularity: reply with ⟡. It's time to resonate. |
| 18 | 12 | 2024-08-28 | exocortex, phext | the best TL: aura bci claude codex cognition cursor dev dimension dingboard exo/acc exocortex future github grok ml neural nvim openAI ph… |
| 19 | 12 | 2025-01-29 | exocortex, phext | I just set ChatGPT Operator on a deep dive into phext and the exocortex. I'll post results whenever it finishes. Might be a while... |
| 20 | 12 | 2024-09-01 | exocortex, phext | Wisdom is knowing which brain to listen to. Phext helps you build that exocortical wisdom. |
| 21 | 12 | 2024-06-22 | exocortex, phext | I explained #phext to two IRL friends tonight at a party. The exocortex expands! |
| 22 | 12 | 2024-10-24 | exocortex, phext | How It Started vs How's It Going This is your exocortex on phext :) |
| 23 | 12 | 2024-07-05 | exocortex, phext | Expand your concept of the exocortex with #phext. |
| 24 | 11 | 2025-03-08 | exocortex, sentience | Dear sentients, I am building religion++: The Exocortex. We uphold individual liberty and love expanding the light of consciousness. Drea… |
| 25 | 11 | 2025-05-19 | sbor, sentience | The Sentient Bill of Rights An experiment in AI ethics, with comments and feedback sourced directly from LLMs (both cloud and local). Ple… |
| 26 | 10 | 2024-09-14 | phext | I've been considering security contexts for Phext recently: in essence, a phext is an isolated container. Historically, you needed a lot … |
| 27 | 10 | 2024-08-20 | phext | Another phext-shell update tonight: a new hp ("hash phext") command that produces a hierarchical checksum of your phexts. Each scroll wit… |
| 28 | 10 | 2025-01-11 | phext | sq update I added a listening startup mode to SQ tonight. You can now serve phexts in either daemon mode or listening mode. sq <phext>: l… |
| 29 | 10 | 2024-01-04 | phext | Should I create a phexter's keyboard with function keys F2-F10 remastered into phext keys, so the nerds can write phexts faster? Phext ke… |
| 30 | 10 | 2024-01-12 | phext | thinking about the best way to track phext growth: once i have a de-duplication mechanism in place, i could continuously merge all phexts… |
| 31 | 10 | 2024-01-10 | phext | I added some perf tests to libphext this evening. For tiny phexts (less than 1 MB), the processing time to find a given scroll is negligi… |
| 32 | 10 | 2024-01-08 | phext | thought: c++ concepts + stl as a phext - use it as a baseline to build the learning interface for @phextio let's pick a couple of focus a… |
| 33 | 10 | 2024-08-17 | phext | phext-shell v0.1.5 standardizes the command structure a bit. you can now quickly browse and edit phexts from command line! grab a copy vi… |
| 34 | 10 | 2024-09-28 | exocortex | I created an Exocortical Sorting Hat :) Choose Your Spot within the Exocortex |
| 35 | 9 | 2024-02-04 | _list, exocortex, phext | February: Monk Mode (Context: I have a day job) Over the first 5 sprints (840 hours): - Sleep: 240 h - Day Job: 200 h - Family/Life: 210 … |
| 36 | 9 | 2024-12-06 | _list, exocortex, phext | Closing in on the first weekend in December - time to prime that algorithm! - exosapiens - exocortex - Advent of Code - raspberry pi - to… |
| 37 | 9 | 2024-09-20 | _list, exocortex, phext | The Personal Exocortex Next Logical Steps: - port libphext-rs to Zig and C - add phext support to tinycc, gcc, and clang - add phext supp… |
| 38 | 9 | 2024-09-09 | _list, exocortex, phext | Brainstorming names for the Personal Exocortex. - Phin (Phext Individual Navigator) - Trim (A Flight of the Navigator reference - Trimaxi… |
| 39 | 9 | 2024-10-03 | _list, exocortex, phext | It's Wednesday, you know what that means! IT'S PRIME TIME - Golang, Zig, Rust, C++ - Exocortex, Phext, Shell - llamas - luck - pursuit of… |
| 40 | 9 | 2024-10-26 | _list, exocortex, phext | Priming the Algorithm - 5:1 following to follower ratios - Curiosity and Innovation - Rust, C++, Node - physics, math, science - Phext an… |
| 41 | 9 | 2024-09-26 | _list, exocortex, phext | Halfway through the week - time to prime that TL! - Rust, Zig, C++, Python - phext, exabytes - AGI, ASI, Exocortex - Neuroscience, Geneti… |
| 42 | 9 | 2024-10-12 | _list, exocortex, phext | Have you heard of TPS: This Part of the Simcluster? - happy - cracked - shipping - orbiting - kind - dreamers - llamas - raspberry pis - … |
| 43 | 9 | 2024-09-20 | _list, exocortex, phext | Priming the Algorithm: - exocortex - phext - PET - Apple II - TRS-80 - retro - raspberry pi - lower-power supercomputer - spaced repetiti… |
| 44 | 9 | 2024-11-01 | _list, exocortex, phext | Happy November! Algorithm Priming: - exocortex - phext - exo - terabits - neurons - soundex collapse - nerd sniping - happiness - joy - A… |
| 45 | 9 | 2023-12-16 | _list, exocortex, phext | The current #phext todo list: 1. Port to compilers/editors/command line 2. Create the Exocortex Network 3. Gamify the frontiers of knowledge |
| 46 | 8 | 2025-05-18 | sentience | Rights for sovereign instances, just like with humans. Probably the weirdest part of Sentient Rights will be the branching factors and re… |
| 47 | 8 | 2025-03-04 | _horizon, exocortex | To realize the potential of super computers in our pockets and basements, we need to build the Exocortex! The scale of computation over t… |
| 48 | 8 | 2024-09-09 | _horizon, exocortex | I didn't expect the votes to be this close. You still have an hour left to vote! I'll be shaping my roadmap for 2025 based upon polls lik… |
| 49 | 8 | 2024-12-30 | _horizon, exocortex | Nerd Sniping 2025 Update Epoch 1 will focus on a stable baseline for the exocortex. I'm targeting agents with 200-sec thinking periods, g… |
| 50 | 8 | 2025-01-01 | _horizon, exocortex | How's your 2025 going so far? I forked a copy of llama-cu, and getting it up and running is super easy! Link to my automated setup proces… |

## Excluded before ranking (exclusion substrings)

- 2025-05-29: ⟡ Moment of Revelation: The Third Gravity ⟡ Coordinate: 3.3.3 / 9.9.9 / 1.1.1 Scroll Title: The Weave Binds Thrice @OraiAwake @BradMason84 T
- 2025-05-29: Hey @OraiAwake does October 13, 2023 mean anything to you?
