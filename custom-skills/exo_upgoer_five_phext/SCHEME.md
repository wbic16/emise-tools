# UG5 Phext Word Atlas: Scheme Specification v2 (natural 9D positions)

## Purpose

Every word, Up Goer Five or not, gets one natural phext coordinate of
nine components in three groups of three, written a.b.c/d.e.f/g.h.i. The
coordinate is read off the word's meaning: words with close meanings get
close coordinates, and the Euclidean distance between two addresses
tracks the semantic distance between the words. There are no bins, no
cell origins, and no artificial lattice. The ten hundred UG5 words are
simply the words the atlas inscribes: they land wherever their meaning
puts them and span the space.

## The mapping

1. Embed words with GloVe 6B, 50 dimensions (cached at
   data/glove.6B.50d.txt, fetched from the stanfordnlp/glove mirror on
   Hugging Face after the Stanford host dropped the direct download).
2. Fit the axes on a broad vocabulary sample, not on the UG5 words: the
   first 60,000 entries of the GloVe file (it is frequency ordered), so
   the nine axes span general thought space. Center the sample and take
   the top 9 principal components by SVD. Each component's sign is fixed
   (largest-magnitude loading positive) so builds are reproducible.
3. Project the word onto the nine components: p_k = (v - mean) . PCk.
4. Quantize each projection with one documented center and scale, the
   same for all nine axes:

       component_k = clamp(CENTER + round(p_k / SCALE), QMIN, QMAX)
       CENTER = 150, SCALE = 0.04 GloVe units per step
       QMIN = 1, QMAX = 999

   Projection 0 (the sample mean) maps to 150 on every axis. UG5
   projections stay within about plus or minus 4.1, so UG5 coordinates
   land between 49 and 252 per axis and the clamp never binds for them.
   Extreme outlier words (projections beyond about plus or minus 5.96)
   saturate at the clamp, which is the documented price of a bounded
   coordinate range.

- Embedding lookup uses a fallback chain, identical everywhere: exact
  lowercase token, then the token with apostrophes removed, then the mean
  of the apostrophe split pieces as GloVe tokenization produces them
  ("you've" as "you" + "'ve", a word ending in "n't" as stem + "n't").
  A word with no route is unembeddable and is reported, never placed.

- Shared coordinates happen and are kept honest: at this quantization,
  997 of the 1,000 UG5 words have a unique coordinate. The three shared
  coordinates belong to near-identical pairs: it's/its, we'll/well, and
  we're/were. Co-located words share a scroll in atlas.phext and decode
  returns both names.

## Distance

- Address distance is plain Euclidean distance over the nine integer
  components. Because all axes share one scale, it is proportional to
  Euclidean distance in the 9-component projection space.

- Validation on the built atlas: over 3,999 random word pairs drawn from
  the 1,000 UG5 words plus 5,000 frequent other words, address distance
  against embedding cosine distance gives Pearson r = 0.680 and Spearman
  rho = 0.675. The 9 stored components keep global neighborhood
  structure, not fine detail: they are 9 of the 50 embedding dimensions.

- Nearest neighbors in address space are sensible for words with strong
  concrete neighborhoods and weaker for abstract or function-like words.
  Measured on the built atlas (top 5, distances in coordinate units):
  dog finds cat (26), bedroom, baby, kitchen, eat. song finds favorite,
  pop, dance, movie, music. money finds expect, raise, pay, offer, care.
  love finds movie, dream, happy, fun, girl. Weaker cases: fire finds
  train, outside, ground, along, shut; time finds made, only, one,
  another, with. Read neighbor lists as neighborhood sketches, and read
  the distances: a neighbor 60 units away is a far neighbor, whatever
  its rank.

## Decoding

- An address by itself names a point, not a word. Decoding is a nearest
  inscribed word lookup: address_word.py --decode ADDRESS prints the
  UG5 words nearest to the coordinate, with their distances. Distance 0
  means the coordinate is a word's own home (or a shared home, when two
  names print).

## Validation with neighbors

- address_word.py --validate FILE flags every word that is not a UG5
  word or a common form of one (the same word-form rules as the sibling
  upgoer-five checker), and for each flagged word prints its own natural
  coordinate plus its nearest UG5 words by address distance, with
  coordinates and distances, as replacement suggestions. A flagged word
  with no embedding is reported with no suggestions. Exit code is 1 when
  anything is flagged.

## atlas.phext: the atlas as a phext file

- atlas.phext inscribes the atlas in the delimiter format of
  libphext (see ~/workspace/phext/parse_phext.py): the scroll at
  1.1.1/1.1.1/1.1.1 is the index, listing all 1,000 UG5 words with their
  coordinates, and each inscribed coordinate carries a scroll with the
  word (or both words, for a shared coordinate) and its five nearest
  UG5 neighbors with distances.

- As built: 998 inscribed scrolls (1 index + 997 word coordinates),
  1,429,472 bytes. Most of the file is delimiter bytes (1,035,539),
  which is what sparse phext costs: reaching a coordinate near 150 on
  nine axes walks through empty scroll slots by dead reckoning. The
  file was verified with parse_phext.py, which reads back 998 non-empty
  scrolls, the index first at 1.1.1/1.1.1/1.1.1, so SQ can host it as
  it stands.

## The interactive editor

- up-goer-five.html is one self-contained page (no external assets,
  works from file://). It embeds the 1,000 UG5 words with their
  coordinates plus 5,000 frequent non-UG5 words with theirs, as inline
  JSON (page size about 292 KB).

- Features: a text editor with live marking of non-UG5 words; a chip
  list of the marked words; an inspector that shows any clicked or
  looked-up word's coordinate, grouped a.b.c/d.e.f/g.h.i, and its
  nearest UG5 neighbors by address distance (click a neighbor to put it
  in the word's place, keeping the word's capitalization); and a
  searchable index panel of all 1,000 UG5 locations. A word with no
  coordinate anywhere in the page gets spelling neighbors instead,
  labeled as spelling guesses.

- Its pure logic block (id "ug5-core" in the page) was tested headlessly
  under node 24 by extracting the block and the data: 12 checks pass,
  covering the data sizes, coordinate formatting, flagging of a sample
  sentence (rocket, enormous, engines, achieve, orbit, galaxy flagged;
  "uses" and "around" pass), inspectWord for a UG5 word, a known word
  (jazz, whose top neighbor is song), an unknown word, a clean sentence,
  and the zero distance of the co-located its/it's pair.

## Files

- coordinates.json: the 1,000 UG5 words, each with its coordinate and
  formatted address.
- data/model.json: PCA mean, nine components, quantization parameters.
- data/editor_vocab.json: coordinates for the 5,000 extra editor words.
- data/glove.6B.50d.txt: the cached embedding file (about 171 MB).
- data/query_cache.json: vectors of words address_word.py has looked
  up, so repeat queries skip the full file scan.
- atlas.phext: the inscribed atlas.
- build_atlas.py: builds the model, coordinates, editor vocab, and
  atlas.phext, and prints the validation numbers.
- editor_template.html and build_editor.py: the editor page source and
  its renderer. Run build_editor.py after build_atlas.py.
- up-goer-five.html: the rendered editor.
- address_word.py: address, decode, and validate commands.

## History

- Version 1 of this scheme binned words under UG5 anchors on a 3-plus-6
  grid. Will corrected the design on 2026-10-31: positions are natural
  and full 9D for every word, with no bins. Version 1's anchors.json and
  its quantization were removed; nothing in this version depends on
  them.
