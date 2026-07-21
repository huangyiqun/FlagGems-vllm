# Multi-backend CI operations

The multi-backend workflow intentionally separates environment validation from
operator capability testing. A backend is not assumed to support every test or
benchmark merely because FlagGems can create its vendor environment.

## Scheduling and trust boundary

- Pull requests select non-NVIDIA backends only through the exact `label`
  values in FlagGems' pinned `.github/backends.json`.
- `ci/all-vendors` selects every enabled non-NVIDIA backend. Use it only for a
  deliberate maintainer-approved validation run.
- `ci/benchmark` enables the selected core benchmarks. Benchmarks also run on
  `main` pushes or when `run_benchmarks` is selected in `workflow_dispatch`.
- `workflow_dispatch` can select all non-NVIDIA backends with
  `run_non_nvidia`.
- The checked-in workflow rejects fork pull requests before self-hosted jobs.
  Because a fork can propose edits to that workflow, configure GitHub's fork
  workflow approval policy strictly and inspect changes that weaken this
  guard before approving a run. The pinned FlagGems workflow must enforce the
  guard again; prefer ephemeral runner isolation as the final boundary. Do not
  replace this protection with `pull_request_target` plus a checkout of fork
  code. Dependabot pull requests are also excluded because GitHub applies the
  fork security model to them.

The repository must provide these labels (spelling and case are significant):

```text
vendor/Ascend
vendor/Enflame
vendor/Hygon
vendor/Iluvatar
vendor/Kunlunxin
vendor/MetaX
vendor/MooreThreads
vendor/SpaceMit
vendor/Sunrise
vendor/Thead
vendor/TsingMicro
ci/all-vendors
ci/benchmark
```

`vendor/Thead` follows the backend registry exactly; do not use
`vendor/THead`.

## Capability rollout

`.github/backend-capabilities.json` is fail closed. Unknown backends receive an
empty operator allowlist and cannot run benchmarks. The setup action still runs
`tools/check_backend_env.py`, which verifies imports, the configured vendor,
device discovery, and a small float32 allocation/addition.

After a backend passes the preflight on a trusted same-repository branch, add
only tests confirmed on that hardware to its `tests_allow` list. Enable and
allowlist benchmarks separately after correctness is stable. The NVIDIA H20
profile is the only initial `allow_all_tests` profile.

The generic preflight is not a substitute for a vendor health query. In
particular, the current SpaceMit descriptor exposes a CPU-compatible device
name. Enflame, SpaceMit, and Sunrise should gain dedicated `gpu_check` scripts
in FlagGems before their hardware availability is considered fully verified.

## Required repository and organization settings

1. In the `flagos-ai` organization runner groups, grant `FlagGems-vllm`
   access to runners labelled `h20`, `ascend`, `enflame`, `hygon`, `iluvatar`,
   `kunlunxin`, `metax`, `mthreads`, `spacemit`, `sunrise`, `thead`, and
   `tsingmicro`. Prefer groups restricted to the exact reusable workflow.
2. Ensure every runner is online, has the matching vendor driver/SDK, and is
   running Actions Runner v2.327.1 or newer. The pinned checkout/setup actions
   use the Node 24 action runtime.
3. Allow official pinned GitHub actions and the reusable workflow from
   `flagos-ai/FlagGems` in the repository Actions policy.
4. Provide outbound HTTPS/DNS access to GitHub, FlagOS resources, the vendor
   package indexes, Astral/uv, and the configured Python mirror. The runner
   workspace, uv cache, and user-local binary directory must be writable.
5. Require the stable `multi-backend summary` check in the branch ruleset.
   Enable code-owner review for CI files. CODEOWNERS review is an audit control,
   not a runtime security boundary.
6. Require approval for workflows from all external contributors, and treat
   any change to a self-hosted job's condition, checkout ref, setup action, or
   test runner as security-sensitive during that approval.
7. Prefer ephemeral/JIT runners. For persistent runners, keep secrets and
   access to internal network services to a minimum and verify cleanup after
   cancelled jobs.

GitHub documents that a called workflow can use only self-hosted runners made
available in the caller repository's context. Sharing an organization alone
does not grant runner access:
https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations

## FlagGems reusable-workflow dependency

The FlagGems revision is intentionally repeated in three syntax locations that
cannot use an expression: the registry checkout, reusable workflow call, and
setup checkout. `python tools/check_ci_pins.py` prevents those pins from
drifting.

The currently pinned FlagGems workflow still declares the unused
`RUNNER_SSH_KEY` input and calls a caller-local checkout retry action after its
bootstrap checkout. A failed bootstrap cannot load that local action. Until a
FlagGems companion change is merged, the caller passes only its short-lived,
read-only `GITHUB_TOKEN`; do not create a long-lived SSH private-key secret.

The FlagGems companion change must:

1. enforce the same same-repository/fork guard inside the pinned called
   workflow instead of trusting only caller-controlled workflow code;
2. inline the checkout attempts in `backend-test.yaml` and leave `ref`
   unspecified (or fix it to `github.sha`);
3. add a 60-minute timeout to the called backend job;
4. make `RUNNER_SSH_KEY` optional, then remove the unused interface after all
   callers stop passing it; and
5. pass `test_script`, `backend`, and `pr_id` through quoted environment
   variables rather than interpolating workflow inputs into shell source.

After that change lands, update all three FlagGems SHAs together, remove
`.github/actions/checkout-retry`, stop passing `RUNNER_SSH_KEY`, and rerun the
pin check.

## Bring-up sequence

Use a branch hosted inside `flagos-ai/FlagGems-vllm`; fork code is deliberately
blocked from self-hosted runners. Add one `vendor/*` label at a time. First
validate checkout, setup, dependency imports, device discovery, and the
portable smoke. Then populate that backend's tested allowlist. Run an explicit
all-vendor dispatch only after every backend passes independently.
