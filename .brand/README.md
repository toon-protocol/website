# .brand

The brand source text the site is written from, copied from `toon-protocol/brand`, which is
public, so that work on this repository needs nothing outside it. Each file is copied
verbatim and starts with a comment naming its source file and commit. The directory starts
with a dot, so `build.py` leaves it out of the Arweave manifest.

```
messaging.md   the messaging hierarchy (Levels 1–4, proof points marked live or owed) and "Things not to say"
voice.md       the voice rules, vocabulary, words to avoid and "Things we never say"
identity.md    the palette with hex values and measured contrast, the type and the mark rules
```

The brand's SVGs are in `assets/icon/` and the IBM Plex fonts, with their OFL licences, are
in `assets/fonts/`. The fonts are the latin-subset woff2 files from the `@fontsource/ibm-plex-sans`,
`@fontsource/ibm-plex-sans-condensed` and `@fontsource/ibm-plex-mono` packages, version 5.3.0.

The copies link to `positioning.md`, `context.md` and `competitors.md`, which are not copied;
those links don't resolve here.

The source is the brand's `main`. To refresh, copy the files again from a newer `main` commit and
update the comment at the top of each.
