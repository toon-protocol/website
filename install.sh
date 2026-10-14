#!/bin/sh
# Install `toon`:
#
#   curl -fsSL https://toon.ar.io/install.sh | sh
#
# This file is served from the TOON site on Arweave. It is a stub: the installer itself
# lives with the program, in toon-protocol/toon_cli, and this hands over to it, so the
# site never carries a stale copy. That script downloads the release for this machine,
# checks it against the release's SHA256SUMS, and puts `toon` in ~/.local/bin.
# TOON_VERSION and TOON_INSTALL_DIR pass through unchanged.
set -eu
curl -fsSL https://raw.githubusercontent.com/toon-protocol/toon_cli/main/install.sh | sh
