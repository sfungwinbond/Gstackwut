# Interview and whiteboard guide

## The seven-minute structure

1. Clarify the asset and security goal.
2. Name adversaries and physical/network capabilities.
3. Draw trust zones and data flows before choosing algorithms.
4. Mark roots of trust and every private-key boundary.
5. Walk provisioning, happy path, failure path, update/rotation, and recovery.
6. Name one catastrophic misuse and its test.
7. State residual risk and observability.

Strong candidates say what a component cannot guarantee. They distinguish authentication from authorization, secrecy from integrity, verified boot from measured boot, and primitive security from protocol security.

## Questions and answer signals

### Explain ECDH to an electrical-engineering peer

Look for finite-field group language, `a(bG)=b(aG)`, active man-in-the-middle risk, public-key validation, and a transcript-bound KDF. The paint analogy may build intuition but must be retired before protocol reasoning.

### Explain ECDSA and a nonce-reuse failure

Look for the equations, verification relation, trusted public-key provenance, and derivation of `k` then `d` from two signatures sharing a nonce. Bonus: deterministic nonces, side channels, fault resistance, canonical encoding, and rejection checks.

### Why did LMS need LM-OTS?

Look for a Merkle root authenticating many one-time public keys, an authentication path per signature, and the central operational fact: leaf state cannot be reused. Ask how the candidate survives process crash, concurrent signers, backup restore, and VM cloning.

### Design a KMS envelope-encryption service

Look for local AEAD with a DEK, KMS wrapping under a KEK, authenticated context, tenant isolation, caching bounds, audit, rotation/rewrap, throttling/outage behavior, and plaintext-memory exposure.

### Add ML-KEM to an ECDH protocol

Look for independent inputs, explicit authentication, downgrade resistance, length-delimited transcript-bound combiner/KDF, failure behavior, parameter negotiation, cryptographic agility without unsafe fallback, and size/latency budgeting.

### Explain an X.509 chain

Look beyond signature checks: local trust anchor, basic constraints, key usage/EKU, names, validity/time model, algorithms, critical extensions, revocation/pinning, and purpose separation. For an MCU, ask what replaces online revocation and trustworthy wall-clock time.

### Design MCU verified boot with a TEE

Look for ROM/OTP root, signed manifest, hash/signature verification before execute, anti-rollback counter, A/B recovery, debug lifecycle, key rotation, boot measurements, and a clear transition into isolated runtime services. A TEE is not accepted as a magic box.

### What does the DS28C40 do?

Good answer: a hardware-protected automotive I2C authenticator that can hold identity/key material, perform ECC/HMAC/ECDH operations, protect memory, and control an authenticated GPIO. Then draw an ECU challenge, device signature/certificate, ECU path validation, signature/freshness check, and enforcement decision. Explicitly assign bypass resistance and certificate policy to the surrounding system.

## Scoring rubric

| Dimension | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Threat model | Absent | Generic attacker | Assets/capabilities named | Physical, lifecycle, supply-chain, and insider cases prioritized |
| Trust boundaries | Magic boxes | Components only | Keys/data cross labeled | TCB and bypass paths minimized and justified |
| Cryptographic correctness | Algorithm names | Basic purpose | Protocol inputs/outputs correct | Validation, domain separation, failure behavior, and misuse covered |
| Lifecycle | Happy path only | Mentions rotation | Provision/update/revoke/recover | Crash, rollback, cloning, decommission, and evidence tested |
| Communication | Jargon dump | Mostly linear | Clear diagram and summary | States assumptions, tradeoffs, and residual risk crisply |

A strong undergraduate answer averages at least 2. A senior security-system answer should approach 3 and turn unknowns into concrete verification work rather than bluffing.
