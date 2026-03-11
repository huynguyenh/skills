# Proposed Changes to Knowledge Base

## Target file: `~/.claude/knowledge/personal/zenlabs.md`

### Summary

The top-level Drive structure (folders 0-6 + root PPT file) is **unchanged** -- same folder names, same IDs, same purposes. No new top-level folders have been added.

The main update is to add **subfolder detail** for each top-level folder, which was not previously documented. This gives Claude better context when navigating the Drive or placing files.

### Change 1: Add subfolder structure under "Drive Structure"

After the existing top-level folder table, add a new section documenting the subfolders within each top-level folder. This would be appended below the existing table:

```markdown
### Subfolder Detail

**0. Operations** (`1PRssu6UYsUTwxPdRtj7v2mYThnCA1ZSZ`)
| Name | Type | ID |
|------|------|----|
| Incorporating | folder | `1SNSis0gYM11hEguMmZV-Ya81r-SawOyQ` |
| Contract Templates | folder | `1AtfZWeC2Rw-0E5i-LSO_H_aty4koh4qP` |
| Signed Contracts | folder | `1esbZIukt1WR1Olw2i9S6D--qH6fb08uo` |
| Payment Requisition | folder | `1zA-pIuVcfX1aUlGau1yB8cnbPqA_BGhp` |
| zenlabs: ops finanance | spreadsheet | `1iztjQLxBoVEhRVWWFgONPvxBG1S7cw6_BKdbB-AXpxE` |

**1. Accounting** (`1Cr2KRz_0yyw7h-MWs23laWDRZG7389V3`)
| Name | Type | ID |
|------|------|----|
| Sao Ke Techcombank | folder | `16euMbAQn-ImF-1idHXTqZf111YS7m6N5` |
| Bang Luong | folder | `1qoihAqdSg6zLjQo7yviD1iF_hmTVXylD` |
| Hoa don | folder | `1856apgetq1Ac56265FCaGWbc2bQfCS_s` |
| To khai VAT | folder | `1yNLkMpDVuxyPq_1I3nIjJDVNF6qW5nv_` |
| Bao cao thue | folder | `1lbxI6mndX9uLXpjf4Dau4wqQoBzz6WdR` |
| Theo doi hop dong- Khach hang.xlsx | shortcut | `16IrZgsvLKLCgmFHTdfy05J3ozdz3AlNi` |

**2. Employment** (`1ZI8nuI7srEwtd0VFMTY1gbuo1OVaq5rQ`)
| Name | Type | ID |
|------|------|----|
| Full-Time Contract | folder | `1XdwIo2AHdyXIwVu8DBEjg5CShenO5ZBD` |
| Freelancer Payment | folder | `175CCiccceb3XEUKotoTJbMCxnASccUJx` |
| Employee Info | folder | `1QjwhlssU4fh2KIiV_o5zyeph5vFsTEKQ` |
| zenlabs: freelance | spreadsheet | `1kzBHCfu_w7OSHqZVSU4x3P7ZGd0KtuFtUfuDjRqT5PE` |

**3. Contracts** (`1fUlH3y5i1OX-sR4CGQQmnZ9Utrsdi873`)
| Name | Type | ID |
|------|------|----|
| GMD | folder | `1XmJarJeoRA_ur-f6yg4RXUh35KzVi2eM` |
| Golden Ad Group | folder | `1s2Iy8RHAz_eC7_0tcANFgtwLmTBjIgyo` |
| Earth Venture | folder | `1tVJsCFkhDP1HnOcK9fvB3Cx4zaaTNvP0` |
| Theo doi hop dong- Khach hang | spreadsheet | `1sTBxASjgPYeG-ifJ1cH_I7sQkZOav_WQ` |

**4. Projects** (`1xf-aduudCyTKPRvErgQ9mWHki5Vc56iL`)
| Name | Type | ID |
|------|------|----|
| AA/Fin | folder | `1-Z73FH4YFusH-KB4G9NinaQZbn3DogWU` |
| HRIS | folder | `1XGguVLvIoz6IMPjiWoPARmTw2mAcTSYB` |
| WOM-IRM | folder | `1bMF-_bWG7PxGJbleMXWAeNQMImRzgMDa` |
| GMD TMS | folder | `1EZyAE-z3ytCWdkuvRZcbDGmO_xkpISvo` |

**5. Branding** (`1DP143t1pCt5a-zJrq459NgoNFDVO7HVa`)
| Name | Type | ID |
|------|------|----|
| biz card | folder | `1HGCEX8eZFksIvcGl-ROgM4DF5CEm5zXz` |
| Logo | folder | `1Q3SLYWGIhv2MT5QztsW828mWx_1MQmA7` |
| Copy of ZenLabs-BrandGuidelines.pdf | file (PDF, 19.4 MB) | `1aldbl-_6KPQioEHC8AyJ78Rw2aj_JZ89` |

**6. Brainstorming** (`1lOIDiTCJi84wuvgK0b1LRV882tzf9ntL`)
| Name | Type | ID |
|------|------|----|
| zenlabs \| skill test (delete me) | spreadsheet | `14DDnz3nBdjZdTOvIrO2xgCHOvJtQpIS8fgWSQvTio40` |
| zenlabs \| usage-logs | spreadsheet | `1pzTEydtQaVB7VYZ4WCqmt6PCpUCRltwzBP5jTDBM5oM` |
```

### What did NOT change

- Top-level folder structure (0-6) is identical -- same names, same IDs
- Root-level file `ZEM LABS PPT TEMPLATE- V2.pptx` still present
- No new top-level folders were added
- All folder IDs in the knowledge base are still valid

### What is new (not previously in knowledge base)

The entire subfolder layer is new information. The previous knowledge base only recorded the 7 top-level folders. Key observations:

1. **Operations** has 4 subfolders (Incorporating, Contract Templates, Signed Contracts, Payment Requisition) and 1 spreadsheet (ops finanance)
2. **Accounting** has 5 subfolders for Vietnamese accounting categories (bank statements, payroll, invoices, VAT declarations, tax reports) plus a shortcut to a client tracking spreadsheet
3. **Employment** has 3 subfolders (Full-Time Contract, Freelancer Payment, Employee Info) and a freelance tracking spreadsheet
4. **Contracts** has 3 client-specific subfolders (GMD, Golden Ad Group, Earth Venture) and a client contract tracking spreadsheet
5. **Projects** has 4 project subfolders (AA/Fin, HRIS, WOM-IRM, GMD TMS)
6. **Branding** has 2 subfolders (biz card, Logo) and the brand guidelines PDF
7. **Brainstorming** has 2 Claude-created spreadsheets (one marked "delete me")

### No changes to INDEX.md

No new domain files would need to be created. The changes only update the existing `personal/zenlabs.md` file.
