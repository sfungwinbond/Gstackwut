# Security systems

## OpenSSL 3.x

Use high-level EVP/provider APIs so algorithm selection, provider policy, and hardware integration remain explicit. Typical operation boundaries are:

- `EVP_PKEY_keygen` / `EVP_PKEY_fromdata` for key construction;
- `EVP_DigestSign*` and `EVP_DigestVerify*` for signatures;
- `EVP_PKEY_derive*` for ECDH-style derivation;
- `EVP_KDF_fetch` plus `EVP_KDF_derive` for HKDF and other KDFs;
- `EVP_PKEY_encapsulate*` and `EVP_PKEY_decapsulate*` for KEMs.

Fetch algorithms using an explicit library context and property query when FIPS/provider selection matters. Check every return value, query output sizes first where the API requires it, keep peer-key validation enabled, and clear sensitive buffers. OpenSSL 3.5 added native ML-KEM algorithm support. Do not turn example/test randomness controls into production inputs.

Review against the exact deployed OpenSSL version:

- [EVP key derivation](https://docs.openssl.org/3.5/man3/EVP_PKEY_derive/)
- [EVP KDF](https://docs.openssl.org/3.5/man3/EVP_KDF/)
- [HKDF provider](https://docs.openssl.org/3.6/man7/EVP_KDF-HKDF/)
- [ML-KEM provider](https://docs.openssl.org/3.5/man7/EVP_KEM-ML-KEM/)
- [KEM encapsulation APIs](https://docs.openssl.org/3.6/man3/EVP_PKEY_encapsulate/)

### Is OpenSSL an RNG?

OpenSSL is a cryptographic library that includes a random subsystem; it is not itself an entropy source. Applications normally call `RAND_bytes` or `RAND_priv_bytes`. OpenSSL's RAND frontend uses DRBG instances from the EVP_RAND backend, which are seeded and reseeded from an operating-system entropy source on mainstream platforms. The DRBG expands a smaller amount of high-quality entropy into the many pseudorandom bytes protocols need.

Keep four terms separate:

- a physical or OS **entropy source** supplies unpredictable input;
- a **TRNG** samples a physical process and requires conditioning/health tests;
- a **DRBG/CSPRNG** deterministically expands seed state and periodically reseeds;
- an **API/library** such as OpenSSL exposes checked access to those mechanisms.

Check the return value. Current OpenSSL documents that its CSPRNG enters an error state and refuses output when seeding fails. Never replace it with `rand()`, timestamps, UUID formatting, or a hand-built entropy mixer.

## KMS and envelope encryption

A key-management service centralizes authorization, audit, protected key operations, and rotation policy. It does not make a compromised workload trustworthy or prevent plaintext exposure in application memory.

For bulk data, generate a random data-encryption key (DEK), encrypt locally with an AEAD, and ask KMS to wrap/protect the DEK under a key-encryption key (KEK). Store ciphertext, nonce, algorithm/version, authenticated metadata, and wrapped DEK together. On read, authorize and audit unwrap, decrypt in memory, use the DEK briefly, and erase it.

Bind tenant, object ID, schema/version, and purpose as authenticated context so a valid ciphertext cannot be transplanted into another context. Cache plaintext DEKs only under an explicit lifetime and blast-radius policy. Specify behavior for KMS outage, throttling, disabled keys, rotation, rewrapping, deletion waiting periods, and disaster recovery. Separate administrators who set key policy from workloads that use keys.

See [AWS KMS cryptographic details](https://docs.aws.amazon.com/kms/latest/developerguide/kms-cryptography.html) and [AWS KMS concepts](https://docs.aws.amazon.com/kms/latest/developerguide/overview.html).

## X.509 certificates

An X.509 certificate is a CA-signed statement binding a subject/public key to names and constraints for a validity interval. It is not the private key and does not encrypt data by itself.

A verifier builds a path from a leaf through zero or more intermediates to a locally trusted root. It then verifies signatures and policy: time, issuer/subject linkage, basic constraints and CA flags, path length, key usage, extended key usage, name constraints, algorithm/key-size policy, critical extensions, intended identity, and revocation or pinning strategy. “The signature verifies” is only one check.

Embedded devices often have no trustworthy wall clock or network revocation service. A design may pin an OEM root in ROM/OTP, use short chains and product-specific extensions, and combine certificate validation with protected lifecycle state or signed revocation/version data. Document the time model and update path instead of silently skipping validation.

Certificates can authenticate a TLS peer, a firmware-signing key, a DS28C40 device public key, or an attestation key. Use distinct roots/intermediates and extended-key usages when compromise domains or purposes differ.

## MCU verified boot, measured boot, and rollback

Verified boot is a chain of authorization:

1. immutable ROM loads a small first-stage image or manifest;
2. ROM hashes it and verifies a signature using a protected root key/digest;
3. the verified stage repeats this process for the next stage and application;
4. execution transfers only after policy succeeds.

The signed object should bind image digest, target/device family, load address where relevant, security version, key ID, algorithm suite, and dependencies. Anti-rollback compares the signed security version with a monotonic counter or protected minimum version. Authentic old firmware is still dangerous when it contains a known vulnerability.

Measured boot records hashes for later attestation but does not necessarily block execution. Verified boot blocks unauthorized images. Systems may do both. Define fail-closed behavior, recovery/update slots, power-loss handling, debug-port lifecycle, signing-key rotation, factory provisioning, and a way to recover from a bad but validly signed release.

On constrained MCUs, the root is often ROM plus fuses/OTP, with TrustZone-M or an MPU separating secure services after boot. A large OS may use a richer TEE. Do not assume an MCU has process isolation, an MMU, secure storage, or a trustworthy clock.

## TEE and TrustZone

A trusted execution environment isolates selected code and data from a richer, less-trusted environment. Its useful properties depend on a verified boot chain, hardware access control, secure interrupt/peripheral assignment, small trusted code, and a defined secure-monitor/API boundary.

Typical TEE services include key derivation/use, rollback-protected storage, biometric decisions, attestation, and authorization of firmware updates. The normal world passes requests and untrusted buffers; the TEE validates lengths, ownership, freshness, and policy before operating on secrets.

TrustZone is a hardware partitioning mechanism, not automatically a complete TEE. TrustZone-A commonly supports secure/normal worlds around application processors; TrustZone-M partitions MCU memory, peripherals, interrupts, and execution into Secure and Non-secure states. Vulnerable secure services, shared-memory confused-deputy bugs, DMA/peripheral misconfiguration, side channels, and an unverified first stage can still break the design.

## Android StrongBox, ECDH, and library boundaries

StrongBox is an Android KeyMint security level implemented by a dedicated secure processor profile. Android's public `PURPOSE_AGREE_KEY` represents ECDH key agreement. A device can perform ECDH with a StrongBox-backed EC private key when its StrongBox KeyMint implementation supports the requested curve, purpose, and parameters. The application must check StrongBox availability, inspect the resulting key's security level, and handle unsupported algorithms or `StrongBoxUnavailableException` rather than assuming every phone has the same capabilities.

Do not say “StrongBox uses OpenSSL” without vendor-specific evidence. The normal path is Android JCA/Keystore API → Keystore service → KeyMint HAL → vendor secure-processor firmware. The private key remains hardware-bound; the secure processor performs the authorized key operation. Android's Conscrypt TLS/provider module uses BoringSSL, a Google fork of OpenSSL, but that is a separate platform component. Native applications may also bundle OpenSSL, again separately.

KeyMint implementations normally return an encrypted and authenticated key blob for Keystore to store outside the secure processor. Raw key bytes (32 bytes for an AES-256 key or P-256 private scalar) therefore do not predict per-key storage. Capacity planning must separately measure:

- protected blob and authorization bytes;
- alias/database/index overhead;
- certificate or attestation chain bytes;
- filesystem headroom;
- vendor-specific replay-protected metadata for rollback resistance;
- secure-processor operation slots, RAM, and latency.

A preliminary external-storage range of roughly 2–8 KiB per ordinary EC/symmetric key record can be useful for budgeting only, not as a platform guarantee. Measure actual blob and database growth on every target. For example, 1,000 records at 2 KiB blob + 0.5 KiB metadata + 1.5 KiB certificate chain + 20% overhead use about 4.7 MiB outside the secure processor, plus unknown trusted metadata. Rollback-resistant key creation can fail when limited trusted storage is full.

Primary Android sources:

- [Android Keystore system](https://developer.android.com/privacy-and-security/keystore)
- [AOSP hardware-backed Keystore architecture](https://source.android.com/docs/security/features/keystore)
- [AOSP KeyMint key blobs and rollback resistance](https://source.android.com/docs/security/features/keystore/implementer-ref)
- [Android `KeyProperties.PURPOSE_AGREE_KEY`](https://developer.android.com/reference/android/security/keystore/KeyProperties)
- [AOSP Conscrypt and BoringSSL](https://source.android.com/docs/core/ota/modular-system/conscrypt)

## DS28C40 secure authenticator

The Analog Devices DS28C40 is an automotive I2C secure authenticator. It provides a hardware-protected identity and operations including P-256 ECDSA sign/verify, ECDH, SHA-256/HMAC, a true random-number generator, secured OTP/user/key storage, and an authenticated GPIO. The product specifies an I2C interface up to 1 MHz, automotive temperature/qualification, and a unique ROM ID. Consult the exact ordering code and revision.

Interview-level mental model:

- The OEM provisions or generates a device key pair and certifies the public key.
- An ECU sends a fresh challenge and context.
- The authenticator signs the challenge/context (or performs a provisioned HMAC flow).
- The ECU validates the certificate chain to its pinned OEM root, checks identity/usage, verifies the challenge signature, and enforces freshness.
- For confidential/authenticated memory, the host and device can use ECDH-derived key material before the protected operation.
- The authenticated GPIO can gate a board-level function, but only if bypass paths and host enforcement are designed correctly.

The chip does not validate the entire vehicle, secure a compromised ECU, or automatically establish certificate policy. The host owns fresh challenge generation, certificate/path policy, revocation/lifecycle policy, response verification, timeout handling, and the decision that follows. If compromised host software can bypass the decision or directly drive the protected function, the authenticator becomes theater.

The datasheet lists representative operation timings including milliseconds for HMAC and tens to hundreds of milliseconds for ECC operations; use the current datasheet and budget end-to-end bus, host verification, retry, and startup time rather than quoting a primitive time as total authentication latency.

Primary vendor material:

- [DS28C40 product page](https://www.analog.com/en/products/ds28c40.html)
- [DS28C40 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/DS28C40.pdf)
- [AN-2580, DS28C40 use cases](https://www.analog.com/en/resources/app-notes/an-2580.html)
- [Automotive peripheral authentication over GMSL](https://www.analog.com/en/resources/design-notes/authenticating-remote-automotive-peripherals-using-gmsl-tunneling.html)

## System review table

| Layer | Establishes | Does not establish | Evidence to request |
|---|---|---|---|
| Signature | Message integrity/authenticity relative to a trusted key | Key identity or freshness by itself | Verified message encoding and key provenance |
| X.509 path | Public-key identity/constraints under local trust policy | Endpoint health or secret possession unless protocol proves it | Full path-validation result and policy |
| Verified boot | Only authorized code starts | Runtime memory safety or availability | Boot measurements, version/counter, failure logs |
| TEE | Runtime isolation for selected services | Correct secure code or secure boot by itself | TCB inventory, API review, isolation tests |
| KMS | Controlled key operations and audit | Safe plaintext application memory | Policy, logs, rotation/outage tests |
| DS28C40 | Hardware-backed component identity and local crypto operations | Secure host decision path | Provisioning record, fresh transcript, bypass analysis |
