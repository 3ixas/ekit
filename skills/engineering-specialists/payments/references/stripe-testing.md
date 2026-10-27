# Stripe webhook and billing verification

Use only for Stripe work. This is a test-design reference, not permission to create provider resources or change accounts. Read the project's payment model, actual webhook route, environment configuration, and installed CLI/SDK versions first. Never assume a port, log directory, account, API version, or event format from another project.

## Choose the environment and delivery path

- Confirm the intended account and sandbox from current configuration without printing credentials. Prefer a dedicated sandbox for new integrations; follow the project's existing isolated test environment where established. Missing credentials or ambiguous environment identity block provider actions, not independent local checks. Report the prerequisite without requesting secrets in chat. Live payments, public endpoints/tunnels, and provider configuration changes need task authority.
- For authorized local forwarding, prefer `stripe listen --forward-to <discovered-local-route>` over a public tunnel. Confirm flags through the installed CLI and current [listen reference](https://docs.stripe.com/cli/listen). Select event types and snapshot/thin delivery to match the handler. Do not use `--live` for sandbox tests.
- Configure the app with the signing secret for the actual delivery path: CLI-forwarded events use the CLI secret; direct registered-endpoint events use that endpoint's secret. These are not interchangeable. `stripe listen --print-secret` prints the CLI secret and exits; it does not start forwarding. Capture it privately only when needed and ensure account/environment match the listener. Do not describe it as necessarily changing on every restart.
- Start the listener separately with access-restricted captured output and record its readiness. The readiness line can contain the signing secret: do not print raw listener logs in reports. Restart or reload the app if its configuration requires it. Stop only listener processes owned by this test.

## Prove webhook handling

1. Send an unsigned or incorrectly signed request to the actual handler. Expect the project's rejection response and no payment-state mutation. Verify the untouched request body reaches signature verification; do not disable signature checks to make the test pass.
2. Trigger relevant sandbox smoke events using the installed CLI and inspect forwarded event IDs/types, response codes, and handler results. A valid accepted event normally returns `2xx`; confirm any asynchronous processing completes before asserting application state.
3. Inspect the resulting database, entitlements, ledger, or other authoritative application state. Include duplicate-event/retry checks when material, proving idempotency rather than counting log lines. A successful response alone does not establish correct billing behaviour.

Use [Stripe's webhook guide](https://docs.stripe.com/webhooks) and [signature troubleshooting](https://docs.stripe.com/events/manage-webhook-endpoints#signature-errors) for current details. Synthetic CLI events prove intake and routing; they do not reproduce a complete purchase or subscription lifecycle.

## Prove subscription lifecycle behaviour

For authorized time-based sandbox simulations, follow the current [Test Clock API guide](https://docs.stripe.com/billing/testing/test-clocks/api-advanced-usage) and [billing testing guide](https://docs.stripe.com/billing/testing):

1. Create a fresh Test Clock and fresh customer attached to it, then the relevant subscription fixtures. Record ownership and IDs privately; reuse no unrelated customer or subscription.
2. Advance time in supported increments and wait for the clock to return to `ready`, with a bounded timeout. Wait for relevant webhook processing too; clock readiness alone does not prove application convergence.
3. Check the expected invoices, subscription state, and application effects for the scoped renewal, trial, failure, or cancellation scenario. Account for documented invoice finalization timing; do not equate a simulated renewal with proof of Checkout behaviour.
4. Preserve sanitized evidence before authorized fixture cleanup. Deleting a clock can delete its associated customers and subscriptions; clean up only resources created for this test and within the granted authority.

Report Pass, Fail, or Skip separately for signature rejection, signed intake, application state, and lifecycle scenarios. Missing provider access leaves those checks Skip; local fixtures are not live Stripe proof.

Method independently adapted from HumanLayer's pinned Stripe verification skill, corrected and bounded using official Stripe documentation reviewed on 2026-10-24. Consult those sources again when executing; this reference does not freeze provider behaviour.
