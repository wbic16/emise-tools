# Up Goer Five Phext Word Atlas

## Know what the atlas is

- Use this skill when the user wants a word's phext address, wants a phext address read back into nearby words, wants a text checked against the ten hundred words with coordinate-based replacement ideas, or wants to write in the atlas editor page.

- Know that every word has one natural 9 part phext address of the form a.b.c/d.e.f/g.h.i, taken from where its meaning sits in a 9 axis space fitted on a broad word sample.

- Know that address distance tracks meaning distance only roughly, with a measured correlation near 0.68, so present neighbors as neighborhood sketches and always show their distances.

- Read `~/workspace/custom-skills/upgoer-five-phext/SCHEME.md` before explaining the mapping in depth, changing the scale or center, or rebuilding the atlas.

## Address and decode words

- Run `python3 ~/workspace/custom-skills/upgoer-five-phext/address_word.py WORD` to address one or more words, and pass `--decode ADDRESS` to find the inscribed words nearest to a coordinate.

- Report a UG5 result as the word's home coordinate, and name its nearest UG5 neighbors with distances when the user wants context.

- Report a non UG5 result with its own coordinate and its nearest UG5 words, since those neighbors are the useful part of the answer.

- Report a word printed as UNEMBEDDABLE plainly as having no address in this atlas, and never invent one for it.

- Accept two names at distance 0 on a decode as a shared coordinate, since three near-identical UG5 pairs share a home.

## Validate a text

- Run `python3 ~/workspace/custom-skills/upgoer-five-phext/address_word.py --validate FILE` to flag the non UG5 words in a text and get coordinate-based replacement suggestions for each.

- Give the user the flagged words with their best few neighbors, and say plainly when a flagged word has no embedding and therefore no suggestions.

- Pair this skill with the sibling upgoer-five skill when the user wants the text actually rewritten into clean Up Goer Five, since that skill owns the translation loop and this one owns the map.

## Use and rebuild the editor

- Open `~/workspace/custom-skills/upgoer-five-phext/up-goer-five.html` for the interactive editor, which marks non UG5 words as the user types and offers neighbor replacements by coordinate distance.

- Regenerate the page after any atlas rebuild with `python3 ~/workspace/custom-skills/upgoer-five-phext/build_editor.py`, and copy it over any hosted or shared copy the user keeps.

- Edit `editor_template.html` rather than the generated page when the user wants the editor itself changed, then regenerate.

## Rebuild the atlas

- Rebuild only when the word list changes or the user asks for a fresh atlas, with `python3 ~/workspace/custom-skills/upgoer-five-phext/build_atlas.py`.

- Check the build output before trusting a rebuild, since it prints the shared coordinate pairs, the distance correlation, neighbor samples, and the atlas.phext scroll count.

- Compare the new correlation with the 0.68 recorded in SCHEME.md, and flag the rebuild if it drops in a clear way.

- Take the word list only from `~/workspace/custom-skills/upgoer-five/words.txt`, the sibling skill's copy of the ten hundred words.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.
