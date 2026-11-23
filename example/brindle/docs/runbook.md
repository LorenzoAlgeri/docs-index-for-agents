# Runbook

## The export is slow

1. Check the size of the tenant file. Above 200 MB, run the vacuum job.
2. If it stays slow, ask the owner to split old recipes into an archive tenant.

## Restore one tenant

1. Stop writes for the tenant (set the flag in the admin screen).
2. Copy last night's backup over `data/<tenant>.db`.
3. Clear the flag and run the smoke test in `docs/onboarding.md`.
