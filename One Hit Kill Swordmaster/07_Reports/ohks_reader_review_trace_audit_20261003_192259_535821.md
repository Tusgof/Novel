# OHKS Reader Review Trace Audit

- Created (UTC): `2026-10-03T19:22:59.535858+00:00`
- Scope: `ch001-ch020`
- Method: compare recorded provider stdout, existing refined candidate, staged candidate, final output, and source markers; no re-refinement or provider calls.

## Cleaner-loss checks

| chapter | traces | stdout list lines | source `---` | candidate `---` | final `---` | list guard | scene-break guard | sha pair |
|---|---:|---:|---:|---:|---:|---|---|---|
| ch001 | 5 | 0 | 0 | 0 | 0 | PASS | PASS | MATCH |
| ch002 | 5 | 0 | 0 | 0 | 0 | PASS | PASS | MATCH |
| ch003 | 8 | 0 | 0 | 0 | 0 | PASS | PASS | MATCH |
| ch004 | 5 | 0 | 1 | 1 | 1 | PASS | PASS | MATCH |
| ch005 | 6 | 0 | 0 | 0 | 0 | PASS | PASS | MATCH |
| ch006 | 5 | 0 | 0 | 0 | 0 | PASS | PASS | MATCH |
| ch007 | 5 | 0 | 0 | 0 | 0 | PASS | PASS | MATCH |
| ch008 | 6 | 0 | 1 | 1 | 1 | PASS | PASS | MATCH |
| ch009 | 5 | 0 | 0 | 0 | 0 | PASS | PASS | MATCH |
| ch010 | 6 | 0 | 0 | 0 | 0 | PASS | PASS | MATCH |
| ch011 | 5 | 0 | 0 | 0 | 0 | PASS | PASS | MATCH |
| ch012 | 5 | 0 | 0 | 0 | 0 | PASS | PASS | MATCH |
| ch013 | 5 | 0 | 0 | 0 | 0 | PASS | PASS | MATCH |
| ch014 | 5 | 0 | 0 | 0 | 0 | PASS | PASS | MATCH |
| ch015 | 5 | 0 | 0 | 0 | 0 | PASS | PASS | MATCH |
| ch016 | 5 | 0 | 0 | 0 | 0 | PASS | PASS | MATCH |
| ch017 | 6 | 0 | 0 | 0 | 0 | PASS | PASS | MATCH |
| ch018 | 5 | 0 | 0 | 0 | 0 | PASS | PASS | MATCH |
| ch019 | 5 | 0 | 0 | 0 | 0 | PASS | PASS | MATCH |
| ch020 | 6 | 0 | 0 | 0 | 0 | PASS | PASS | MATCH |

The source range contains no `- ` or `* ` list lines. Recorded stdout, refined candidates, staged candidates, and finals contain zero such lines. The single ASCII scene break in ch004 and the single ASCII scene break in ch008 are present in the source, candidate, staged, and final surfaces; repeated trace totals reflect retries and were not duplicated into output.

## Repaired output hashes

| chapter | final path | final SHA-256 | staged SHA-256 | bytes |
|---|---|---|---|---:|
| ch001 | `D:\Fogust\Workspace\Novel\One Hit Kill Swordmaster\05_Output\ch001\ch001.md` | `e64e9589ddc79620a075f0a08b683003e69faf30f80e68c5d3b1e417f30f98b0` | `e64e9589ddc79620a075f0a08b683003e69faf30f80e68c5d3b1e417f30f98b0` | 30573 |
| ch002 | `D:\Fogust\Workspace\Novel\One Hit Kill Swordmaster\05_Output\ch002\ch002.md` | `86fbbcc30b3dd898b3d974e6471a2b021fc3e22c1858dc8c543d0b9dd43566cc` | `86fbbcc30b3dd898b3d974e6471a2b021fc3e22c1858dc8c543d0b9dd43566cc` | 43477 |
| ch003 | `D:\Fogust\Workspace\Novel\One Hit Kill Swordmaster\05_Output\ch003\ch003.md` | `48b92f64865b438e3ddebfc6dc06f77216e164db7de28fa0cc89afd72782e043` | `48b92f64865b438e3ddebfc6dc06f77216e164db7de28fa0cc89afd72782e043` | 34307 |
| ch004 | `D:\Fogust\Workspace\Novel\One Hit Kill Swordmaster\05_Output\ch004\ch004.md` | `edda3fcc68881e15a8ec341d9a216b94201157b66848d341d0fe108d7fe4ebc5` | `edda3fcc68881e15a8ec341d9a216b94201157b66848d341d0fe108d7fe4ebc5` | 31762 |
| ch005 | `D:\Fogust\Workspace\Novel\One Hit Kill Swordmaster\05_Output\ch005\ch005.md` | `0c0d22ea9b14126c1c3f656d24a741b118fe8767f9a410c5028d0c449f9becef` | `0c0d22ea9b14126c1c3f656d24a741b118fe8767f9a410c5028d0c449f9becef` | 40687 |
| ch006 | `D:\Fogust\Workspace\Novel\One Hit Kill Swordmaster\05_Output\ch006\ch006.md` | `7890c128bb0904481b16dc167c23ff95871b0b5e02abe1da3cdfb5d4a74796d1` | `7890c128bb0904481b16dc167c23ff95871b0b5e02abe1da3cdfb5d4a74796d1` | 29245 |
| ch007 | `D:\Fogust\Workspace\Novel\One Hit Kill Swordmaster\05_Output\ch007\ch007.md` | `271dbc94edf611ac8bf4608ac623cc33f2f83d86b280e52973099d8fefd3b486` | `271dbc94edf611ac8bf4608ac623cc33f2f83d86b280e52973099d8fefd3b486` | 33770 |
| ch008 | `D:\Fogust\Workspace\Novel\One Hit Kill Swordmaster\05_Output\ch008\ch008.md` | `e09a1980634b6487d8f8a1b21a1fb46c7ad3328f76555e1b0f8a830a5c47300f` | `e09a1980634b6487d8f8a1b21a1fb46c7ad3328f76555e1b0f8a830a5c47300f` | 29836 |
| ch009 | `D:\Fogust\Workspace\Novel\One Hit Kill Swordmaster\05_Output\ch009\ch009.md` | `b23ad0c556a938e5cc27179815299e28ae6678bb27bd6ba42f4d58d0f227aec6` | `b23ad0c556a938e5cc27179815299e28ae6678bb27bd6ba42f4d58d0f227aec6` | 31592 |
| ch010 | `D:\Fogust\Workspace\Novel\One Hit Kill Swordmaster\05_Output\ch010\ch010.md` | `d99cb01c4fbb2d11279e67b8cdab942106fba0db7c076859169b154ef84962cf` | `d99cb01c4fbb2d11279e67b8cdab942106fba0db7c076859169b154ef84962cf` | 33844 |
| ch011 | `D:\Fogust\Workspace\Novel\One Hit Kill Swordmaster\05_Output\ch011\ch011.md` | `afe27f08091a696f80020eb005f9cedfec74aafec4fe7d5259f7fed69f2c1943` | `afe27f08091a696f80020eb005f9cedfec74aafec4fe7d5259f7fed69f2c1943` | 31693 |
| ch012 | `D:\Fogust\Workspace\Novel\One Hit Kill Swordmaster\05_Output\ch012\ch012.md` | `40ea093adba459be89859678953bcde750c8e62246f34182d556ea0dd3ad09ad` | `40ea093adba459be89859678953bcde750c8e62246f34182d556ea0dd3ad09ad` | 30992 |
| ch013 | `D:\Fogust\Workspace\Novel\One Hit Kill Swordmaster\05_Output\ch013\ch013.md` | `f45456b65203ce63d6877f3b7e9cb7d65d0682c48d9c52b149e64cb369e69d9f` | `f45456b65203ce63d6877f3b7e9cb7d65d0682c48d9c52b149e64cb369e69d9f` | 33213 |
| ch014 | `D:\Fogust\Workspace\Novel\One Hit Kill Swordmaster\05_Output\ch014\ch014.md` | `667296671b36bbcbf8bb0c558a04b7c28c04417f0b9bfa7ec77c587b58c182ce` | `667296671b36bbcbf8bb0c558a04b7c28c04417f0b9bfa7ec77c587b58c182ce` | 33629 |
| ch015 | `D:\Fogust\Workspace\Novel\One Hit Kill Swordmaster\05_Output\ch015\ch015.md` | `ed4bbbfe45841137417d5c1c8413a898dc594eac1c5b94960d6df5d4830715af` | `ed4bbbfe45841137417d5c1c8413a898dc594eac1c5b94960d6df5d4830715af` | 35997 |
| ch016 | `D:\Fogust\Workspace\Novel\One Hit Kill Swordmaster\05_Output\ch016\ch016.md` | `ec919d4067bca73a746f6c13f572d4281d125e7c75a53daa88117ecf9afe1cb0` | `ec919d4067bca73a746f6c13f572d4281d125e7c75a53daa88117ecf9afe1cb0` | 32853 |
| ch017 | `D:\Fogust\Workspace\Novel\One Hit Kill Swordmaster\05_Output\ch017\ch017.md` | `5b864b166f25d14375487cf9b0ec6517be411edafa85974c81474c95f4a3734d` | `5b864b166f25d14375487cf9b0ec6517be411edafa85974c81474c95f4a3734d` | 35499 |
| ch018 | `D:\Fogust\Workspace\Novel\One Hit Kill Swordmaster\05_Output\ch018\ch018.md` | `ab3cc7e108a2473a72b9a09b5498f57b092b4aeb0dab1b50e7efcfa828ad4c6b` | `ab3cc7e108a2473a72b9a09b5498f57b092b4aeb0dab1b50e7efcfa828ad4c6b` | 32779 |
| ch019 | `D:\Fogust\Workspace\Novel\One Hit Kill Swordmaster\05_Output\ch019\ch019.md` | `de85bd0cb2179a156986926d939a1d7f97b24bf4ee9be8e3a1c88816cf943ab2` | `de85bd0cb2179a156986926d939a1d7f97b24bf4ee9be8e3a1c88816cf943ab2` | 30550 |
| ch020 | `D:\Fogust\Workspace\Novel\One Hit Kill Swordmaster\05_Output\ch020\ch020.md` | `e747e9b10b5d09d090e258bf932f7b29884b8a23de3d3c8f1c7d9efc109bbc30` | `e747e9b10b5d09d090e258bf932f7b29884b8a23de3d3c8f1c7d9efc109bbc30` | 36306 |

All final/staged hashes match pairwise. These are the exact 20 repaired final outputs; each corresponding bounded staged candidate is recorded in the JSON artifact.
