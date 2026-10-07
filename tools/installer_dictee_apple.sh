#!/bin/sh
# Compile uniquement l'adaptateur ; aucun téléchargement de modèle.
set -eu
cd "$(dirname "$0")/.."
mkdir -p .local/bin .local/swift-cache
xcrun swiftc -parse-as-library -O -target "$(uname -m)-apple-macos26.0" \
  -module-cache-path .local/swift-cache tools/apple/dictee.swift -o .local/bin/dictee-apple
.local/bin/dictee-apple --status
