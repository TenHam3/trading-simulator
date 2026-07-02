#!/usr/bin/env bash
set -euo pipefail

# Resolve repo root so this script works regardless of the caller's cwd.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROTO_DIR="$ROOT_DIR/proto"
OUT_DIR="$ROOT_DIR/generated"

shopt -s nullglob
proto_files=("$PROTO_DIR"/*.proto)
shopt -u nullglob

if [ ${#proto_files[@]} -eq 0 ]; then
    echo "No .proto files found in $PROTO_DIR" >&2
    exit 1
fi

echo "Compiling ${#proto_files[@]} proto file(s):"
printf '  %s\n' "${proto_files[@]##*/}"

python -m grpc_tools.protoc \
    -I"$PROTO_DIR" \
    --python_out="$OUT_DIR" \
    --grpc_python_out="$OUT_DIR" \
    "${proto_files[@]}"
