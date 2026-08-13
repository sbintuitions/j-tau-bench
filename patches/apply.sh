#!/usr/bin/env bash
#
# Clone sierra-research/tau2-bench at the base commit and apply the sbintuitions patch.
#
# Usage:
#   bash apply.sh [target_dir]      # default: ./tau2-bench-patched
#
# Requirements: git, network access to github.com (HTTPS).
#
set -euo pipefail

# --- configuration -------------------------------------------------------
# upstream repository (sierra-research/tau2-bench)
UPSTREAM_URL="https://github.com/sierra-research/tau2-bench.git"

# base commit of upstream `main` this patch is built against
BASE_COMMIT="f0927a4b9cdfa7b374269efaa29ff7fdac90d8fc"
BASE_SUBJECT="Website: preview card links, toggle alignment, and τ³ track naming (#427)"
# -------------------------------------------------------------------------

# --- resolve patch paths (this script lives next to the .patch files) ----
# applied in order; each is logically independent but numbered for a
# deterministic, reproducible apply order.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATCHES=(
  "${SCRIPT_DIR}/0001-orchestrator-error-classification.patch"
  "${SCRIPT_DIR}/0002-claude-prompt-cache.patch"
)

for p in "${PATCHES[@]}"; do
  if [[ ! -f "${p}" ]]; then
    echo "ERROR: patch not found: ${p}" >&2
    exit 1
  fi
done

TARGET_DIR="${1:-tau2-bench-patched}"

# --- refuse to overwrite an existing directory ---------------------------
if [[ -e "${TARGET_DIR}" ]]; then
  echo "ERROR: target already exists: ${TARGET_DIR}" >&2
  echo "       remove it first or pass a different directory name." >&2
  exit 1
fi

echo "=== Clone upstream ==="
echo "URL       : ${UPSTREAM_URL}"
echo "Target    : ${TARGET_DIR}"
git clone --quiet "${UPSTREAM_URL}" "${TARGET_DIR}"

echo "=== Checkout base commit ==="
echo "Commit    : ${BASE_COMMIT}"
echo "Subject   : ${BASE_SUBJECT}"
git -C "${TARGET_DIR}" checkout --quiet "${BASE_COMMIT}"

echo "=== Apply patches ==="
for p in "${PATCHES[@]}"; do
  echo "--- $(basename "${p}") ---"
  git -C "${TARGET_DIR}" apply --stat "${p}"

  if ! git -C "${TARGET_DIR}" apply --check "${p}" 2>/dev/null; then
    echo "ERROR: $(basename "${p}") does NOT apply cleanly to ${BASE_COMMIT:0:7}." >&2
    echo "       the upstream code may have moved past the base commit." >&2
    exit 1
  fi

  git -C "${TARGET_DIR}" apply "${p}"
  echo
done
echo "OK: all patches applied to ${TARGET_DIR} at ${BASE_COMMIT:0:7}"
echo
echo "Changed files:"
git -C "${TARGET_DIR}" diff --name-only
