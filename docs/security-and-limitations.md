# Security limitations and operational cautions

**Do not use this project to hold real funds or as a public cryptocurrency service.** It demonstrates blockchain concepts, not the security guarantees of a production consensus network. The following are source-code observations, not penetration-test results.

## Private keys and persistence

`Wallet.to_dict()` includes `private_key`; `Storage.save_wallet()` writes it to plaintext JSON at `source/node_data/node_<port>/wallet.json`. Never publish this folder, backup it to a public location, or reuse its test wallet keys. `.gitignore` excludes generated state, but check `git status` before pushing.

## HTTP exposure and input handling

Write-capable routes such as `/mine`, `/transactions/new`, and `/nodes/register` lack production authentication/authorization. Some request handlers assume valid JSON shape and types. `/transactions/new` signs missing-signature requests with the **local node wallet**, which is suitable only for a trusted local demo and must be redesigned for public access. `Blockchain.add_transaction()` lacks full positive-amount and type validation; block signature checks do not amount to a complete ledger-state or double-spend proof.

## Consensus limits

The project uses fixed-difficulty simulated PoW and a **longer-valid-chain** selection rule, not a cumulative-work rule or BFT protocol with formally established tolerance. The genesis block depends on wall-clock time, so independently started nodes may begin with different genesis hashes. A simple violation counter blacklists peers after three observed issues, but the blacklist itself is not separately persisted and does not establish Sybil, eclipse, or 51% resistance.

## Recommended operation

Run with `--host 127.0.0.1` on a single trusted machine, or limit access to a controlled teaching LAN and configure firewall rules. Do not expose unauthenticated Flask endpoints or UDP discovery to the public Internet. Production use would require a redesigned key custody model, robust validation, API authentication, rate limiting, consensus security analysis, and independent testing.

The executable Python source and browser interface are preserved as supplied; these are recommendations and limitations, **not implemented fixes**. See the [architecture](architecture.md) and [testing](testing.md) documents for traceability.
