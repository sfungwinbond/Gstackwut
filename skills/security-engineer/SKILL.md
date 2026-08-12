---
name: security-engineer
description: Use this skill for applied cryptography, key-management, secure-boot, hardware-root-of-trust, or security-system design work involving OpenSSL, KMS, KDFs, ECDH, ECDSA, ML-KEM, LMS, X.509, TEEs, MCUs, or secure authenticators such as the DS28C40.
---

# Security Engineer

Design and explain security systems from mathematical primitive to operational failure mode. Produce explicit trust boundaries, original diagrams, testable assumptions, and interview-ready explanations instead of treating algorithm names as architecture.

## Route the request

- For a concept explanation or interview drill, read `references/cryptographic-foundations.md` and `references/interview-and-whiteboard.md`.
- For OpenSSL, KMS, certificates, TEE, MCU boot, or embedded trust architecture, read `references/security-systems.md`.
- For DS28C40 work, read the DS28C40 section in `references/security-systems.md` and distinguish host duties from authenticator duties.
- For a standalone teaching artifact, run `scripts/build_security_lab.py --output OUTPUT.html`; inspect the HTML in a browser at desktop and mobile widths.
- For a design review, start with assets, adversaries, trust anchors, key lifecycle, freshness, recovery, and evidence. Choose algorithms only after those are explicit.

## Required reasoning sequence

1. State the security property: confidentiality, integrity, authenticity, freshness, rollback resistance, availability, non-repudiation, or some combination.
2. Draw components and trust boundaries. Label every location where plaintext, private keys, derived secrets, certificates, counters, and firmware hashes exist.
3. Separate primitives from protocols and policy. ECDH agrees on secret material; it does not authenticate a peer by itself. X.509 binds names and constraints to a public key; it does not prove the endpoint is currently trustworthy. A TEE isolates selected runtime operations; it does not repair an unauthenticated boot chain.
4. Specify domain separation, transcript binding, algorithm identifiers, key identifiers, versions, nonces, and failure behavior.
5. Trace provisioning, normal use, rotation, revocation, crash recovery, rollback, decommissioning, and audit evidence.
6. Test negative paths: invalid chain, wrong usage, reused nonce or LMS leaf, stale firmware, corrupted ciphertext, unavailable KMS, compromised host, and power loss between state update and output.
7. Mark toy mathematics and simulations as educational only. Use reviewed libraries and current high-level APIs in production.

## Design defaults

- Prefer modern OpenSSL EVP/provider interfaces; do not introduce deprecated low-level crypto APIs.
- Feed ECDH or KEM output into a labeled KDF with salt/context. Never use a raw shared secret directly as an application key.
- Authenticate ephemeral key exchanges with a signature, pinned key, certificate chain, or an authenticated higher-level protocol.
- Use envelope encryption for bulk data: local data key for payload, KMS-protected wrapping key for the data key, and authenticated metadata bound as AEAD associated data.
- For hybrid post-quantum designs, combine independently generated classical and ML-KEM shared secrets in a transcript-bound KDF. Do not merely concatenate keys and call the result a protocol.
- Treat LMS/LM-OTS signing state as security-critical transactional state. Reserve and durably advance the leaf index before releasing a signature.
- In verified boot, anchor the first verification key or digest in immutable ROM, OTP, or equivalent protected storage; enforce anti-rollback with a protected monotonic version.
- Keep TEE, bootloader, application, KMS, and external-authenticator responsibilities distinct. Minimize the trusted computing base and define recovery when a trust anchor must rotate.
- For X.509, validate a complete path and intended usage, not only the CA signature. Constrain algorithms, names, key usage, basic constraints, path length, time policy, and revocation or pinning strategy.

## Deliverables

Return the smallest useful set:

- an answer-first security assessment;
- a source-controlled system or sequence diagram;
- a protocol transcript with exact inputs and outputs;
- a key/certificate lifecycle table;
- misuse cases and test vectors;
- interview questions with a scoring rubric;
- reproducible HTML when the work is educational or publishable.

Every diagram must be original, readable without color, and label trust boundaries and verification decisions. Cite primary standards and vendor documentation next to claims that depend on them.

## HTML lab

Generate the bundled course with:

```bash
python3 skills/security-engineer/scripts/build_security_lab.py \
  --output site/security-engineer.html
```

Check whether the committed page matches its source:

```bash
python3 skills/security-engineer/scripts/build_security_lab.py \
  --output site/security-engineer.html --check
```

The lab deliberately uses tiny finite fields and toy parameters so students can inspect every operation. Its outputs are never production keys or security guidance by themselves.
