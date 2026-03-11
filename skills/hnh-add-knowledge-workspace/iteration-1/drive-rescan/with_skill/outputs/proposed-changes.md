# Proposed Changes to Knowledge Base

**Based on:** Drive rescan reconciliation (2026-03-10)

---

## File: `personal/zenlabs.md`

### Change 1: Add subfolder structure under each top-level folder

**Classification:** NEW -- enriches existing Drive Structure section with subfolder detail

**Action:** Replace the current Drive Structure table and surrounding content with an expanded version that includes subfolders.

**Current content (lines 7-19):**
```markdown
### Drive Structure
The Drive is organized with numbered top-level folders:

| # | Folder | Folder ID | Purpose |
|---|--------|-----------|---------|
| 0 | Operations | `1PRssu6UYsUTwxPdRtj7v2mYThnCA1ZSZ` | Company operations -- admin, processes, internal docs |
| 1 | Accounting | `1Cr2KRz_0yyw7h-MWs23laWDRZG7389V3` | Financial records, invoices, bookkeeping |
| 2 | Employment | `1ZI8nuI7srEwtd0VFMTY1gbuo1OVaq5rQ` | HR, employee contracts, hiring docs |
| 3 | Contracts | `1fUlH3y5i1OX-sR4CGQQmnZ9Utrsdi873` | Client/vendor contracts, agreements |
| 4 | Projects | `1xf-aduudCyTKPRvErgQ9mWHki5Vc56iL` | Project-specific folders and deliverables |
| 5 | Branding | `1DP143t1pCt5a-zJrq459NgoNFDVO7HVa` | Brand assets, logos, marketing materials |
| 6 | Brainstorming | `1lOIDiTCJi84wuvgK0b1LRV882tzf9ntL` | Ideas, drafts, scratch work -- **default folder for new files when no specific project is given** |

Also at root: `ZEM LABS PPT TEMPLATE- V2.pptx` (shared, by giangthanht)
```

**Proposed replacement:**
```markdown
### Drive Structure
The Drive is organized with numbered top-level folders:

| # | Folder | Folder ID | Purpose |
|---|--------|-----------|---------|
| 0 | Operations | `1PRssu6UYsUTwxPdRtj7v2mYThnCA1ZSZ` | Company operations -- admin, processes, internal docs |
| 1 | Accounting | `1Cr2KRz_0yyw7h-MWs23laWDRZG7389V3` | Financial records, invoices, bookkeeping |
| 2 | Employment | `1ZI8nuI7srEwtd0VFMTY1gbuo1OVaq5rQ` | HR, employee contracts, hiring docs |
| 3 | Contracts | `1fUlH3y5i1OX-sR4CGQQmnZ9Utrsdi873` | Client/vendor contracts, agreements |
| 4 | Projects | `1xf-aduudCyTKPRvErgQ9mWHki5Vc56iL` | Project-specific folders and deliverables |
| 5 | Branding | `1DP143t1pCt5a-zJrq459NgoNFDVO7HVa` | Brand assets, logos, marketing materials |
| 6 | Brainstorming | `1lOIDiTCJi84wuvgK0b1LRV882tzf9ntL` | Ideas, drafts, scratch work -- **default folder for new files when no specific project is given** |

Also at root: `ZEM LABS PPT TEMPLATE- V2.pptx` (shared, by giangthanht)

### Subfolder Structure

#### 0. Operations
| Subfolder / File | Type | ID |
|------------------|------|----|
| Incorporating | folder | `1SNSis0gYM11hEguMmZV-Ya81r-SawOyQ` |
| Signed Contracts | folder | `1esbZIukt1WR1Olw2i9S6D--qH6fb08uo` |
| Contract Templates | folder | `1AtfZWeC2Rw-0E5i-LSO_H_aty4koh4qP` |
| Payment Requisition | folder | `1zA-pIuVcfX1aUlGau1yB8cnbPqA_BGhp` |
| zenlabs: ops finanance | spreadsheet | `1iztjQLxBoVEhRVWWFgONPvxBG1S7cw6_BKdbB-AXpxE` |

#### 1. Accounting
| Subfolder / File | Type | ID |
|------------------|------|----|
| Sao Ke Techcombank | folder | `16euMbAQn-ImF-1idHXTqZf111YS7m6N5` |
| Bang Luong | folder | `1qoihAqdSg6zLjQo7yviD1iF_hmTVXylD` |
| Hoa don | folder | `1856apgetq1Ac56265FCaGWbc2bQfCS_s` |
| To khai VAT | folder | `1yNLkMpDVuxyPq_1I3nIjJDVNF6qW5nv_` |
| Bao cao thue | folder | `1lbxI6mndX9uLXpjf4Dau4wqQoBzz6WdR` |

#### 2. Employment
| Subfolder / File | Type | ID |
|------------------|------|----|
| Full-Time Contract | folder | `1XdwIo2AHdyXIwVu8DBEjg5CShenO5ZBD` |
| Freelancer Payment | folder | `175CCiccceb3XEUKotoTJbMCxnASccUJx` |
| Employee Info | folder | `1QjwhlssU4fh2KIiV_o5zyeph5vFsTEKQ` |
| zenlabs: freelance | spreadsheet | `1kzBHCfu_w7OSHqZVSU4x3P7ZGd0KtuFtUfuDjRqT5PE` |

#### 3. Contracts
- Organized by client, plus a contract tracking spreadsheet

| Subfolder / File | Type | ID |
|------------------|------|----|
| GMD | folder | `1XmJarJeoRA_ur-f6yg4RXUh35KzVi2eM` |
| Golden Ad Group | folder | `1s2Iy8RHAz_eC7_0tcANFgtwLmTBjIgyo` |
| Earth Venture | folder | `1tVJsCFkhDP1HnOcK9fvB3Cx4zaaTNvP0` |
| Theo doi hop dong- Khach hang | spreadsheet | `1sTBxASjgPYeG-ifJ1cH_I7sQkZOav_WQ` |

#### 4. Projects
| Subfolder | ID |
|-----------|----|
| AA/Fin | `1-Z73FH4YFusH-KB4G9NinaQZbn3DogWU` |
| HRIS | `1XGguVLvIoz6IMPjiWoPARmTw2mAcTSYB` |
| WOM-IRM | `1bMF-_bWG7PxGJbleMXWAeNQMImRzgMDa` |
| GMD TMS | `1EZyAE-z3ytCWdkuvRZcbDGmO_xkpISvo` |

#### 5. Branding
| Subfolder / File | Type | ID |
|------------------|------|----|
| biz card | folder | `1HGCEX8eZFksIvcGl-ROgM4DF5CEm5zXz` |
| Logo | folder | `1Q3SLYWGIhv2MT5QztsW828mWx_1MQmA7` |
| Copy of ZenLabs-BrandGuidelines.pdf | file (PDF) | `1aldbl-_6KPQioEHC8AyJ78Rw2aj_JZ89` |

#### 6. Brainstorming
| File | Type | ID |
|------|------|----|
| zenlabs \| usage-logs | spreadsheet | `1pzTEydtQaVB7VYZ4WCqmt6PCpUCRltwzBP5jTDBM5oM` |
```

**Note:** The file `zenlabs | skill test (delete me)` in Brainstorming is excluded from the proposed KB update because it appears to be a scratch/test file intended for deletion.

---

### Change 2: None needed

**Files with no changes required:**
- `personal/zenlabs-employees.md` -- no employee data discoverable from Drive structure alone; would need a Notion rescan to update
- `INDEX.md` -- already accurate; no new domain files being created

---

## Summary of proposed edits

| File | Change type | Description |
|------|-------------|-------------|
| `personal/zenlabs.md` | MERGE (enrich) | Add new "Subfolder Structure" section documenting 20 subfolders and 5 key files across all 7 top-level folders |
| `personal/zenlabs-employees.md` | No change | Drive scan does not surface new employee data |
| `INDEX.md` | No change | No new domain files added |
