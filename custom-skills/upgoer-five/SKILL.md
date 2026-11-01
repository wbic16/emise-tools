# Up Goer Five Translation

## Turn English into Up Goer Five

- Use this skill when the user asks for an Up Goer Five or UG5 version of a text, asks to write using only the ten hundred most used words, or asks whether a text stays inside those words.

- Draft the translation in short, plain sentences that use only words from `~/workspace/custom-skills/upgoer-five/words.txt`.

- Build hard ideas out of simple parts, such as calling a rocket a thing that goes up and a cell a tiny building block of life.

- Write numbers as words, and remember that even the word thousand is not on the list, so say ten hundred instead.

## Check and fix until clean

- Run the checker on every draft before showing it to the user, with `python3 ~/workspace/custom-skills/upgoer-five/scripts/check_ug5.py <file>` or by feeding the text on stdin.

- Rewrite each flagged word with a listed word, or rephrase the sentence to go around it, then run the checker again.

- Repeat until the checker reports zero flagged words, and only then present the text as an Up Goer Five translation.

- Add `--suggest` when a flagged word is hard to replace, and treat the close listed words it prints as starting points rather than answers.

- Know that the checker accepts common changed forms of a listed word, such as uses from use or going from go, and pass `--strict` when the user wants only the exact listed forms.

## Keep the meaning true

- Keep the meaning of the first text even when the simple words make the translation much longer.

- Flag proper names and words with no good simple form to the user instead of letting them slip in, and offer a simple-words description of the thing as the way around it.

- Keep names the user insists on, and tell them plainly that the text is no longer fully inside the ten hundred words.

- Leave swear words and contractions as they are when the first text has them, since words such as can't are on the list.

## The word list

- Take the allowed words only from `~/workspace/custom-skills/upgoer-five/words.txt`, which holds the 1000 words from the dictionary file of the Up Goer Five text editor at https://splasho.com/upgoer5/phpspellcheck/dictionaries/1000.dicin

- Know that the last word in that file is a stray TRUE that came with the source, and leave the list as it was published rather than quietly fixing it.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.
