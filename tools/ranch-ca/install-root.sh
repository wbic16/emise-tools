#!/bin/bash
# ranch-ca install-root — install the Ranch Root CA into this machine's
# system trust store (Debian/Ubuntu layout: /usr/local/share/ca-certificates).
#
# usage: sudo bash install-root.sh [path-to-root-ca.crt]
#   default cert path: root-ca.crt beside this script.
# Verifies the cert against the rebuilt system bundle before declaring success.
set -euo pipefail
CERT="${1:-$(cd "$(dirname "$0")" && pwd)/root-ca.crt}"
[ -f "$CERT" ] || { echo "install-root: no cert at $CERT" >&2; exit 1; }
echo "installing: $(openssl x509 -in "$CERT" -noout -subject)"
echo "fingerprint: $(openssl x509 -in "$CERT" -noout -fingerprint -sha256 | cut -d= -f2)"
cp "$CERT" /usr/local/share/ca-certificates/ranch-root-ca.crt
update-ca-certificates
openssl verify -CAfile /etc/ssl/certs/ca-certificates.crt "$CERT"
echo "install-root: Ranch Root CA trusted by this machine's system store"
