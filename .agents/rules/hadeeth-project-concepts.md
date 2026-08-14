# Hadeeth ID - Core Concepts & Architecture Rules

This file provides critical context to the AI about the architecture, database quirks, and design philosophy of the Hadeeth ID project. Always read and adhere to these rules before making structural changes or patching data.

## 1. The Numbering System Conundrum
The project uses multiple data sources that unfortunately use different numbering systems. You must be hyper-aware of this when mapping data:
- **Darussalam Numbering (Primary UI Reference):** Splits variant narrations into distinct numbers. For Sahih Muslim, this goes up to 7,563 hadiths.
- **AhmedBaset Database:** Contains 7,459 hadiths for Sahih Muslim. It does not perfectly map 1:1 to Darussalam at the end of the books.
- **Lidwa/Irsyad Database (`shahih-muslim.sql`):** Groups variants together. It only has 5,362 entries for Sahih Muslim.

**Rule:** Never assume a 1:1 mapping between these databases without checking the exact Arabic text. When writing scripts to patch data, always account for variant offsets.

## 2. Data File Architecture
The UI (`js/app.js`) acts as the presentation layer, dynamically merging data from several static JSON files hosted on a CDN:
- `data/chapters/<book>.json`: Contains metadata, chapter structure, and sometimes fallback English/Indonesian texts from the SQL dump.
- `data/editions/ara-<book>.json`: The primary Arabic text source (originally from fawazahmed0). **Known bug:** The end of Sahih Muslim (last ~112 hadiths) contains duplicated garbage text (the Khawarij hadith) due to upstream scraping errors.
- `data/editions/ind-<book>.json`: Indonesian translations.
- `data/editions/eng-<book>.json`: English translations.

## 3. UI and Language Fallback Rules
- **No Automatic Fallbacks:** If a translation (English or Indonesian) is missing for a specific hadith variation, DO NOT fallback to the other language. The UI must explicitly note that it is unavailable (e.g., "(Terjemahan tidak tersedia untuk variasi sanad ini)").
- **Language Syncing:** The translation language displayed in the UI must directly match the global language selected by the user in the top navigation bar.

## 4. Modifying Data
- Never replace the entire dataset without explicit permission.
- When patching corrupted data (like the Muqaddimah or the end of Sahih Muslim), write isolated Python scripts that pull from a verified source, map the text correctly, and surgically update the `data/editions/*.json` files.
