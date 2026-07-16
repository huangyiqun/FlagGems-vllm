#!/usr/bin/env bash
set -eo pipefail

BACKEND="${1:?usage: $0 <backend> [pr-id]}"
PR_ID="${2:-}"

source .venv/bin/activate

# DeviceDetector consumes a vendor name rather than the full setup profile.
export FLAGGEMS_VENDOR="${BACKEND%%-*}"
export PYTHONPATH="${GITHUB_WORKSPACE:-$(pwd)}/src${PYTHONPATH:+:${PYTHONPATH}}"
set -u

echo "Backend: ${BACKEND}"
echo "PR ID: ${PR_ID:-n/a}"

read -r -a selected_targets <<< "${CHANGED_FILES:-}"
tests=()
benchmarks=()

for target in "${selected_targets[@]}"; do
  case "${target}" in
    tests/test_*.py|tests/*/test_*.py)
      tests+=("${target}")
      ;;
    benchmark/test_*.py|benchmark/*/test_*.py)
      benchmarks+=("${target}")
      ;;
  esac
done

if (( ${#tests[@]} == 0 && ${#benchmarks[@]} == 0 )); then
  echo "No tests or benchmarks selected; skipping."
  exit 0
fi

for target in "${tests[@]}" "${benchmarks[@]}"; do
  if [[ ! -f "${target}" ]]; then
    echo "Selected target does not exist: ${target}" >&2
    exit 1
  fi
done

if (( ${#tests[@]} > 0 )); then
  echo "Selected tests: ${tests[*]}"
  python -m pytest -q "${tests[@]}" --quick
fi

if (( ${#benchmarks[@]} > 0 )); then
  echo "Selected benchmarks: ${benchmarks[*]}"
  python -m pytest -q "${benchmarks[@]}" --level core
fi
