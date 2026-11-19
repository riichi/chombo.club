# chombo.club site

The bilingual (Polish default, English) website of Kraków Chombo Club and the build that produces it.

## Content

**Original**:
The Polish version of a post or page; the default language, from which translations are made.
_Avoid_: source post, master copy

**Translation**:
The English version of an Original, sharing its date, category and URL shape under `/en/`.

**Language-exclusive post**:
A post that deliberately exists in only one language and so has no Translation.
_Avoid_: untranslated post (that implies a missing translation)

## Migration

**Baseline**:
The Jekyll-built site output at a frozen commit, used as the reference the Zola build is compared against.
_Avoid_: upstream, reference build, golden

**Render-equivalent**:
Two output files that a typical browser displays identically (or near-identically); differences in whitespace, attribute order, void-tag syntax or character references don't count.
_Avoid_: byte-identical, identical

**Parity check**:
The comparison of the Zola output against the Baseline, file by file, under the Render-equivalent rule plus a written list of known exceptions.
_Avoid_: diff, golden test
