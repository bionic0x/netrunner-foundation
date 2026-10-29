# W3C eddsa-jcs-2022 test vector

Copied byte for byte from `w3c/vc-di-eddsa` at commit
`13e7070534d1ba1c2987cb26bfb1535e0f15bb72`: `TestVectors/keyPair.json`,
`TestVectors/unsigned.json` and `TestVectors/eddsa-jcs-2022/*` (the files listed
below). They are the Annex B.3 example of *Data Integrity EdDSA Cryptosuites
v1.0* (W3C Recommendation, https://www.w3.org/TR/vc-di-eddsa/). W3C test
material is distributed under the W3C Software and Document License
(https://www.w3.org/copyright/software-license/).

The private key is the published example key. It signs nothing in this
repository except the vector itself.

| File | SHA-256 |
|---|---|
| canonDocJCS.txt | 59b7cb6251b8991add1ce0bc83107e3db9dbbab5bd2c28f687db1a03abc92f19 |
| combinedHashJCS.txt | a6a2a31ddcda8bc3f0d5ce6518a83a1463303add4a7eaa2c214e7131a8df0f44 |
| docHashJCS.txt | 48bc629493fb906c7bc01df114855e9d8fe2315c9bee048614b3d90521445936 |
| keyPair.json | 978631fc2aba6e8cd8be0bd5a7bf216e2ac54201594937602a9acd6e9763d08f |
| proofConfigJCS.json | 87f2fa70b44fceefab298df97e76b947391129b07a466b477bf8d7df4744dead |
| proofHashJCS.txt | 97e35ff9b83bd9a31a9f9acb1b6c88f30982f053d77787e0ee84124b050c7421 |
| sigHexJCS.txt | 3534f97ac30cbbcf8e85bbc79fc0ba2a4d37cb68e9a786265e4e72f666afef00 |
| signedJCS.json | 396833e12675a9679c54d238107eae19db80128c07fb2b8b291da7fcef03be38 |
| unsigned.json | 060626e6046fc6f39a4aecc55a60b61071ab9aa3f8fd05b8626f8787ec0ff912 |
