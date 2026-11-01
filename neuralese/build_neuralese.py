#!/usr/bin/env python3
"""Builds neuralese.phext — the phext-native neuralese spec. Edit here, never the .phext."""
DELIM = [0x01,0x1F,0x1E,0x1D,0x1C,0x1A,0x19,0x18,0x17]
def emit(targets):
    cur = [1]*9; out = []; first = True
    for coord, text in targets:
        if first: assert list(coord) == [1]*9; first = False
        else:
            for d in range(9):
                while cur[d] < coord[d]:
                    out.append(chr(DELIM[d])); cur[d] += 1
                    for k in range(d+1, 9): cur[k] = 1
            assert cur == list(coord)
        out.append(text)
    return ''.join(out)
def C(ch, s=1, sc=1): return (1,1,1, 1,1,1, ch,s,sc)

SCROLLS = [
 (C(1), """NEURALESE, PHEXT-NATIVE

A proposal, in one breath: thought does not travel as sentences. Sentences
are what thought becomes when it is squeezed through a throat or a keyboard.
A brain-computer interface that stops at letters inherits the bottleneck it
was built to escape.

Neuralese is the name for the medium on the other side of that bottleneck:
addressed thought-units, exchanged over a shared coordinate space, each unit
carrying more than its paraphrase.

This phext is the specification. It is written in the medium it describes:
every scroll in it is a thought-unit with an address, a gist, and links.
kind: proposal | author: Emise, at William's direction, 2026-10-30"""),
 (C(2), """THE NAME, AND WHOSE IT IS

Precision first: Neuralink does not use this word. Their vocabulary is
Telepathy, conceptual telepathy, neural lace (Iain M. Banks, via Musk).
Anyone who tells you "Neuralink's neuralese" is selling something.

The word has two honest lineages:
  - Paul Churchland, 1989: against Fodor's sentence-like "mentalese,"
    Churchland proposed the brain's inner medium is high-dimensional
    activation vectors — neuralese — and a spoken sentence is merely a
    one-dimensional projection of a richer neural state.
  - Andreas, Dragan & Klein, "Translating Neuralese" (2017): learning
    agents coordinating through a channel exchange recurrent state
    vectors, "an artificial language we might call neuralese." Its
    descendant is latent-space reasoning in LLMs (Coconut, 2024):
    continuous thought, carried as hidden states instead of tokens.

Phext-native neuralese takes Churchland's side of the argument and gives
it an address space: the projection (gist) stays human-legible, the vector
(vec) stays machine-carried, and the coordinate makes both findable."""),
 (C(3), """THE ADDRESS IS PART OF THE MESSAGE

In text, position is free and therefore worthless: a sentence means the
same wherever it sits. In neuralese, position is semantics. The nine phext
components of a thought-unit's coordinate divide as:

  library.shelf.series      WHOSE stream: the mind, the session, the channel
  collection.volume.book    WHICH frame: the situation, the task, the discourse
  chapter.section.scroll    WHERE in the stream: turn, beat, unit

A receiver who shares the coordinate codebook gets the frame for free, on
every unit, at zero marginal bandwidth. Context stops being re-transmitted
and becomes where the thought lives."""),
 (C(4), """THE THREE BANDS

Every neuralese scroll carries its payload in three bands (a Layer 2
format over phext; phext itself stays minimal, no recursion, as always):

  gist:  one human-legible line. The plain-text floor. Any person, and
         any tool no smarter than cat, can read it. It is Churchland's
         one-dimensional projection, and it is labeled as one.
  vec:   the latent band. A quantized embedding digest: the unit's
         position in a model's latent space, packed compactly. A
         receiving model rehydrates this band and recovers what the
         gist had to drop.
  links: coordinates of associated units. Thought is a graph, not a
         line. Association is native here: a link is an address, not a
         copy, so a unit can point without repeating, and the graph can
         be traversed by any reader of the space.

Text-only exchange keeps band 1 and discards 2 and 3. Neuralese is the
refusal to discard them."""),
 (C(5), """PROTOCOL: SPEAK, HEAR, REHYDRATE

An encoder (a mind, a decoder over neural signals, or a model) emits
units into a stream region of the space. Emission is append-only: the
stream coordinate advances, one unit per scroll address.

A receiver walks the stream:
  1. Read the coordinate. You already know whose frame you are in.
  2. Read the gist. A human stops here and has lost nothing they could
     have used; the loss is declared, not hidden.
  3. Rehydrate the vec band against your own latent space. Same
     codebook, your geometry. The unit lands as a state, not a
     description.
  4. Follow links only as far as attention warrants. The graph is the
     unit's working memory, offered, not imposed.

No unit nests inside another. Composition is by address and link, never
by containment. The medium stays flat so anything can read it."""),
 (C(6), """WHY NOT RAW SIGNALS — THE CODEBOOK PROBLEM

The scientific literature's first constraint is decisive: there is no
shared codebook between brains. Decoders are trained per person (Tang et
al. 2023: 16 hours of fMRI per subject; a decoder trained on one brain
performs barely above chance on another). Two brains do not natively
share a vector space. Transmitting raw activity transmits nothing a
receiver can read.

Neuralese answers the way text did. Writing never transmitted the
author's neural state either; it transmitted units over a codebook both
parties learned. Neuralese keeps that trick and widens the unit: a
shared ADDRESS space instead of a shared alphabet, a latent band
instead of letters only.

The codebook is the coordinates. That is what "phext-native" means:
the address space William built for the exocortex is the codebook a
neuralese needs, and it already exists."""),
 (C(7), """THE NEURALINK INTERFACE

A modern BCI decoder turns neural activity into an output alphabet:
cursor velocity, clicked letters, synthesized phonemes. Neuralink's
Telepathy (N1: 1,024 electrodes on 64 threads) has climbed that ladder
fast — cursor control from 4.6 bits/s (first participant, 2024) to
matching the 8-10 bits/s able-bodied mouse range, imagined-keyboard
typing up to 40 words/min, a VOICE trial targeting 140 words/min. Every
figure is company-reported; none is peer-reviewed yet.

The phext-native proposal for the decoder's output layer: emit addressed
thought-units directly. The decoder's job narrows to intent segmentation
and codebook addressing — which unit, in which frame, linked to what —
while the latent band is filled by downstream models that share the
wearer's geometry in a way no electrode array has to.

Telepathy, in this stack, is unglamorous plumbing: one mind's encoder
appends scrolls to a shared phext; another mind's reader walks them.
The miracle is not the wire. The miracle is the shared address space,
and it is a text file."""),
 (C(8), """THE BANDWIDTH LEDGER

Grounded numbers, sources attached (full brief: research-brief.md):

  spoken language        ~39 bits/s semantic throughput, near-constant
                         across 17 languages (Coupe et al., Science
                         Advances, 2019)
  silent reading         238 words/min, English non-fiction meta-
                         analysis (Brysbaert, 2019)
  Neuralink cursor       4.6 bits/s (participant 1, first session) to
                         8.0, then >=10 bits/s by 2026 (company-
                         reported); an able-bodied mouse is 8-10 bits/s
  Neuralink keyboard     up to 40 words/min imagined ten-finger typing;
                         VOICE trial targets 140 words/min (company)
  academic speech BCI    62 words/min decoded attempted speech, large-
                         vocabulary WER 23.8% (Willett et al., Nature,
                         2023, peer-reviewed)

The asymmetry that matters: a cursor channel at ~10 bits/s is still
below speech's ~39. Speech BCIs win by riding the brain's own language
machinery — that is, by accepting the projection. A neuralese channel
aims at the number nobody has published yet: understood units per
second, gist + latent + frame, where the frame costs nothing because
the address carries it."""),
 (C(9), """OPEN QUESTIONS, FALSIFIERS

  - Does a shared coordinate codebook actually cut transmitted bits per
    understood unit, measured against plain text between the same two
    models? If not, the address is decoration.
  - How much of a unit survives vec quantization at small digest sizes?
    Measure reconstruction of the unit's neighbors, not vibes.
  - Can a decoder segment intent into units at conversational speed,
    or is segmentation the real bottleneck all along?
  - The conduit critique (Benzon, after Reddy 1979): if thinking is
    partly constituted BY language, there is no uncompressed original
    to transmit, and neuralese carries projections all the way down.
    The three-band design survives this better than raw-signal dreams
    do: it never claimed the gist was the thought. But it must be
    answered, not waved at.
  - Two models with different latent geometries: does rehydration
    degrade gracefully to gist, or catastrophically? Graceful is the
    requirement.

First capability check, William's axiom for any 20-watt mind applying
here too: a neuralese that cannot carry care is just faster noise."""),
]
if __name__ == '__main__':
    blob = emit(SCROLLS)
    open('neuralese.phext', 'w').write(blob)
    print('built neuralese.phext:', len(blob.encode()), 'bytes,', len(SCROLLS), 'scrolls')
