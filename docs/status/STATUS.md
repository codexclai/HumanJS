# HumanJS — current status

**As of:** 2026-11-10  
**Stage:** repository foundation clean-up and verification complete; ready to begin the first Rust CPU implementation slice.

## Canonical repository

- Repository: `codexclai/HumanJS`.
- Visibility: public. Default branch: `main`.
- GitHub `main` is the sole authoritative source. ChatGPT Project Sources may remain empty.
- No open pull requests or open issues were returned by the latest live check before this synchronization.
- The current main-branch policy workflow passed on commit `9ddd7b2fd912ede619907b1e31bb713e6cad8830` (run `42815622728`, success). That check validates repository policy only; it is not a code build, simulation test, or biological validation.
- The repository policy workflow is restricted to pushes to `main` and manual dispatch, with read-only `contents` permission and an immutable checkout action SHA.
- Branch-generating dependency update automation is not part of the accepted workflow.

## Completed preparation

- Consolidated the active requirements, system architecture, brain-scope specification, decision record, roadmap, security guidance, repository hygiene, status, and session boot sequence.
- Confirmed that the boot process retrieves live GitHub state and does not depend on ChatGPT Project Sources or local uploads.
- Removed superseded archive/migration material and duplicate project snapshots from the current tracked tree.
- Removed branch-generating update automation and pull-request-specific scaffolding to align repository operations with the permanent main-only policy.
- Kept the repository license, attribution notice, contribution guidance, security policy, ignore rules, text attributes, and repository-policy validator.
- Verified the previous repository-policy workflow succeeded on the current pre-cleanup main commit.

## Implementation status — not started

The repository does not yet contain:
- A Rust workspace or executable simulation mechanism.
- A Python developer package or its tests.
- A stable C ABI or C++ wrapper.
- An integrated WGSL GPU execution backend.
- Executable JSON brain/model/IR definitions.
- Runtime save/restore, native worker execution, or simulation integration tests.

The configurable default of 10,000 spiking neuron units, save/restore, Rust-native multi-threaded execution, and CPU execution remain requirements, not implemented capabilities. CPU is the first implementation target. GPU support is an objective and must not be claimed until implemented and measured on actual supported hardware.

## Branch status and operational limitation

The live branch check on 2026-11-10 found nine non-main refs in addition to `main`. Comparing each against `main` showed each has one unique commit and is 8–16 commits behind; none is to be used or updated. The connected GitHub operations available in this session can list, compare, and update refs but do not expose branch deletion. No authenticated GitHub browser session was available. These refs therefore remain physically present and must not be described as deleted. The intended steady state remains `main` only.

No rulesets, branch protection, deletion-prevention settings, or automatic branch-generating updates are required. Force pushes remain exceptional and must be inspected and verified.

## Next implementation milestone

Start a minimal Rust workspace with one end-to-end, CPU-only simulation vertical slice. Choose module boundaries from actual ownership and data flow, not arbitrary brain-region crates. Define typed time/state/error/resource contracts, write numerical unit tests, and make the first integrated mechanism causally testable. Add persistence and Rust-native concurrency as explicit tested capabilities rather than placeholders. Gather only the scientific evidence needed for the selected first mechanism and record its provenance.