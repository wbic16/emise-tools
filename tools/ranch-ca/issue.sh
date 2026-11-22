#!/bin/bash
# ranch-ca issue — mint a leaf certificate from the Ranch Root CA.
# usage: ~/ranch-ca/issue.sh <hostname> [extra-san ...]
#   extra SANs are DNS names by default; prefix an IP as IP:1.2.3.4
# Output: ~/ranch-ca/issued/<hostname>/{key.pem,cert.pem,fullchain.pem}
set -euo pipefail
CA="$(cd "$(dirname "$0")" && pwd)"
[ $# -ge 1 ] || { echo "usage: issue.sh <hostname> [extra-san ...]" >&2; exit 2; }
HOST="$1"; shift
OUT="$CA/issued/$HOST"
mkdir -p "$OUT"; chmod 700 "$OUT"
SANS="DNS:$HOST"
for s in "$@"; do
  case "$s" in IP:*) SANS="$SANS,$s" ;; *) SANS="$SANS,DNS:$s" ;; esac
done
SERIAL=$(cat "$CA/next-serial.txt")
echo $((SERIAL+1)) > "$CA/next-serial.txt"
umask 077
openssl req -newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes -sha256 \
  -keyout "$OUT/key.pem" -out "$OUT/csr.pem" -subj "/CN=$HOST" >/dev/null 2>&1
cat > "$OUT/ext.cnf" <<EOF
basicConstraints=critical,CA:false
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=$SANS
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid
EOF
openssl x509 -req -in "$OUT/csr.pem" -CA "$CA/root-ca.crt" -CAkey "$CA/root-ca.key.pem" \
  -set_serial "0x$SERIAL" -days 365 -sha256 -extfile "$OUT/ext.cnf" -out "$OUT/cert.pem" >/dev/null 2>&1
cat "$OUT/cert.pem" "$CA/root-ca.crt" > "$OUT/fullchain.pem"
chmod 600 "$OUT/key.pem"; chmod 644 "$OUT/cert.pem" "$OUT/fullchain.pem"
rm -f "$OUT/csr.pem" "$OUT/ext.cnf"
FP=$(openssl x509 -in "$OUT/cert.pem" -noout -fingerprint -sha256 | cut -d= -f2)
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
EE=$(( ($(date -u +%s) - 1795327200) / 420 + 1 ))
EXP=$(openssl x509 -in "$OUT/cert.pem" -noout -enddate | cut -d= -f2)
printf '%s | %s | %s | %s | %s | %s | %s\n' "$SERIAL" "$HOST" "$SANS" "$NOW" "$EE" "$EXP" "$FP" >> "$CA/ledger.txt"
echo "issued: $HOST  serial $SERIAL  expires $EXP"
echo "sha256 fingerprint: $FP"
echo "files: $OUT/{key.pem,cert.pem,fullchain.pem}"
