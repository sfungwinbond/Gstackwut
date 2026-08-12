# Cryptographic foundations

Use this reference to keep explanations mathematically correct while staying at an upper-undergraduate electrical/computer-engineering level.

## Finite fields and elliptic curves

For an odd prime `p`, the finite field `F_p` contains integers `0..p-1` with addition, subtraction, multiplication, and division modulo `p`. Division by nonzero `a` means multiplication by `a^(p-2) mod p`. There are no rounding errors, and every nonzero element has one multiplicative inverse.

A short-Weierstrass elliptic curve over `F_p` is

`E: y^2 = x^3 + ax + b (mod p)`

with `4a^3 + 27b^2 != 0 (mod p)`. Its points plus the point at infinity `O` form an abelian group. Point addition is geometric intuition translated into field arithmetic:

- distinct points: `lambda = (y2-y1)/(x2-x1)`;
- doubling: `lambda = (3x1^2+a)/(2y1)`;
- `x3 = lambda^2-x1-x2` and `y3 = lambda(x1-x3)-y1`, all modulo `p`.

Scalar multiplication `Q = dG` repeats this group operation. Given `d` and `G`, computing `Q` is easy; recovering `d` from `G` and `Q` is the elliptic-curve discrete-log problem for appropriately selected curves and subgroups. Real systems must validate peer public keys, curve membership, subgroup/order conditions where applicable, encodings, and the point at infinity.

## ECDH

Alice samples private scalar `a` and publishes `A=aG`; Bob samples `b` and publishes `B=bG`. Both obtain the same group point:

`aB = a(bG) = abG = b(aG) = bA`.

The paint-mixing picture is only intuition for an easy forward transform and a hard inverse. It does not model group structure, entropy, public-key validation, active attackers, or the KDF. A complete protocol authenticates the exchanged public keys or transcript and derives application keys:

`PRK = HKDF-Extract(salt, EncodeX(abG))`

`K = HKDF-Expand(PRK, protocol || roles || A || B || suite || transcript_hash, L)`.

ECDH alone is vulnerable to an active man-in-the-middle. A derived key must be bound to identities, roles, algorithm suite, and the handshake transcript.

## ECDSA

Let `G` have prime order `n`, private key `d`, public key `Q=dG`, and message representative `z` from a specified hash/truncation rule.

Signing samples a unique unpredictable nonce `k in [1,n-1]`, computes `R=kG`, `r=x(R) mod n`, and `s=k^-1(z+rd) mod n`. Verification computes `w=s^-1`, `u1=zw`, `u2=rw`, `X=u1G+u2Q`, and accepts when `r = x(X) mod n` after all range and key checks.

If `k` is known, `d=(sk-z)r^-1 mod n`. If the same `k` signs two different message representatives, `k=(z1-z2)(s1-s2)^-1 mod n`, after which `d` follows. Bias, weak randomness, fault leakage, or side channels can be just as serious as exact reuse. Deterministic nonce derivation can remove dependence on online randomness, but implementations still need constant-time operations and fault resistance.

ECDSA authenticates a message relative to a trusted public key; it does not encrypt. The trust path for `Q`—pinning, a certificate, provisioning, or another authenticated channel—is part of the system.

## HKDF and domain separation

HKDF is extract-then-expand:

- Extract compresses possibly nonuniform input keying material into a pseudorandom key using an optional salt.
- Expand derives one or more purpose-specific keys with an `info` label.

Use distinct structured labels for directions and purposes, for example `product/v2/client-to-server/aead-key`. Bind stable encodings of protocol version, suite, roles, peer identities, and transcript. A KDF does not add entropy that is not present; it separates and distributes existing entropy safely.

## ML-KEM and hybrid establishment

ML-KEM is a key-encapsulation mechanism standardized by NIST in FIPS 203. A recipient creates an encapsulation key and decapsulation key. A sender encapsulates to produce ciphertext `ct` and shared secret `ss`; the recipient decapsulates `ct` to recover `ss`. It is not a general-purpose data-encryption API and it does not authenticate the sender.

Parameter sets ML-KEM-512, -768, and -1024 target increasing security categories with larger keys/ciphertexts and more work. Protocol designers should use approved encodings and APIs rather than implement the lattice mathematics themselves.

A defensible hybrid combines independent classical and post-quantum contributions with context:

`hybrid = HKDF-Extract(salt, len(ecdh_ss)||ecdh_ss||len(mlkem_ss)||mlkem_ss)`

`traffic = HKDF-Expand(hybrid, suite||roles||identities||transcript_hash, L)`

Exact combiner requirements are protocol-specific. Preserve downgrade resistance, authenticate both public-key inputs, erase intermediates, and define what happens if one algorithm fails. Hybrid does not mean silently falling back to the weaker path.

## Why LM-OTS and LMS appeared

Shor's algorithm threatens deployed factoring- and discrete-log-based signatures if cryptographically relevant quantum computers become practical. Hash-based signatures rely on conservative hash-function assumptions and simple operations.

LM-OTS is a one-time signature: revealing multiple signatures under one LM-OTS private key leaks too much structure. LMS generates many LM-OTS keys, hashes their public keys into a Merkle tree, publishes one root, and includes an authentication path with each selected leaf signature. HSS stacks LMS trees to increase capacity and operational flexibility.

The tradeoff is state. The signer tracks a leaf index `q`; reusing an LM-OTS leaf can enable forgery. A safe signer atomically reserves/persists the next unused index before making the signature externally visible. Backup/restore, cloning, concurrent signers, VM snapshots, and power loss are protocol concerns, not mere database details. Stateless hash-based schemes address a different operational point and have different size/performance tradeoffs.

## Primary sources

- [NIST FIPS 186-5, Digital Signature Standard](https://csrc.nist.gov/pubs/fips/186-5/final)
- [NIST SP 800-56A Rev. 3, pair-wise key establishment](https://csrc.nist.gov/pubs/sp/800/56/a/r3/final)
- [RFC 5869, HKDF](https://www.rfc-editor.org/rfc/rfc5869)
- [NIST FIPS 203, ML-KEM](https://csrc.nist.gov/pubs/fips/203/final)
- [RFC 8554, LMS and HSS](https://www.rfc-editor.org/rfc/rfc8554)
