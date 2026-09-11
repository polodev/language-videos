# Hindi Pathshala Bd — Facebook assets

- [Profile logo](../../../output/imagegen/hindi-facebook/logo.png): 1024 × 1024 PNG, designed for a circular avatar crop.
- [Facebook cover](../../../output/imagegen/hindi-facebook/facebook-cover.png): 1648 × 720 PNG.
- [Exact prompts](image-prompts.md) and [generation settings](image-prompts.json).

Generated with OpenAI `gpt-image-2` at **medium** quality. The cover used the logo as its image reference. Both images were visually reviewed for spelling and layout. The generated files and checksums are recorded in `output/imagegen/hindi-facebook/generation-manifest.json`.

Display name: **Hindi Pathshala Bd**. Handle: **@HindiPathshalaBd**. Tagline: **Learn Hindi easily through Bangla.**

The reference ebook project uses JSON image declarations and `gpt-image-2`; its ebook-only no-text rule and default low quality were not carried into these explicitly requested medium-quality brand graphics. No files in that reference project were changed.

The key is read privately from the user-specified local environment file. It is never stored in this project. The wrapper in `scripts/generate_brand_images.py` invokes the installed imagegen CLI; it does not duplicate the SDK implementation. Existing outputs are not overwritten automatically.
