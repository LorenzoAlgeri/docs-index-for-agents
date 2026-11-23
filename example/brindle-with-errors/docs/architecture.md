# Architecture

One API process serves all tenants. Each tenant owns one SQLite file in
`data/<tenant>.db`. A request carries a tenant id in its path; the API opens
that file and nothing else.

```text
client -> API -> tenant database file
                 `-> image folder on disk
```

Why one file per tenant: a restore touches one tenant, and a bad migration
cannot reach the others. The cost is that cross-tenant reports need a loop.
