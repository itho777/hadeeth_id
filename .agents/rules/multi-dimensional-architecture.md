# Multi-Dimensional Database Architecture Rules

## 1. The Core Philosophy
Hadeeth ID operates on a **multi-dimensional, non-destructive data architecture**. We DO NOT flatten, merge, or overwrite original historical datasets into a single JSON format. 

## 2. Native Data Storage
All original source data is kept completely isolated and unaltered in `data/sources/<source_name>/`.
- **Fawazahmed / AhmedBaset**: Stored natively. Used as the Primary Anchor for Arabic Text (AR) and English Translations (EN) because it contains all 17 books and strictly follows standard international numbering.
- **Lidwa (Irsyad)**: Stored natively. Used as the primary source for Indonesian Translations (ID) and Sanad Nodes for the Core 9 books.
- **Open-Hadith (mhashim6)**: Stored natively. Used for basic Syarah (Tafseel).
- **Kaggle Narrators**: Stored natively. Used as the global Rawi biographical database.

## 3. The Linking Engine
Instead of merging files, a standalone Linking Engine (`scripts/link_engine.py`) reads the disparate native databases and generates a `master_link.json`. 
- The engine uses the Primary Anchor (Fawazahmed/Darussalam numbering) as the skeleton.
- It maps the other dimensions (Lidwa ID, OpenHadith Syarah) to the anchor using ID proximity and Arabic string matching.
- **Golden Rule:** Never alter the original source texts to force a link. If a link cannot be established programmatically, it must be flagged for manual review or left blank. 

## 4. Dynamic Display
The frontend (`js/app.js`) dynamically constructs the view by querying the `master_link.json` and then fetching the specific native blocks from their respective `data/sources/` folders. It must gracefully handle missing dimensions (e.g., when viewing one of the additional 8 books that lacks a Lidwa ID translation).
