# Brief for the Tecolutla database review agents

Context: we are preparing a technical presentation of the Tecolutla oil field (Contract Area 24, CNH-R01-L03-A24/2016, Veracruz, Mexico; operator Tonalli Energía; El Abra reef reservoir; wells TEC-2, -3, -5, -6, -7, -9, -10DES, -11DES, -101; planned TEC-12) to a Kinjal engineer (Kinjal is acquiring 100 % of Tonalli). The repository /home/user/git_practice holds the analysis so far. Read for context (do not edit):
- docs/Tecolutla_Field_History_and_TEC12_Review_v4.md (the review)
- docs/18_kinjal_briefing.md (presentation prep, anticipated questions)
- docs/gaps.md (open data gaps; G-numbers)
- data/processed/deck_notes/*.md (notes from files already read)

Goal: go through EVERY file in your assigned Google Drive folder tree, file by file, and review, assess and interpret it for inclusion in the review/presentation.

Tools: load the Google Drive MCP tools with ToolSearch query "select:mcp__Google_Drive__search_files,mcp__Google_Drive__read_file_content,mcp__Google_Drive__get_file_metadata". List children with search_files query "parentId = '<folderId>'" (pageSize 100, excludeContentSnippets true, follow nextPageToken), recurse into subfolders. Read files with read_file_content (works for PDF, Office, Google formats, images). Do NOT download files into the repository and do NOT edit or commit anything in the repo.

Already covered: /tmp/claude-0/-home-user-git-practice/cfddd84a-7303-5f1c-8e6b-47d4ec46ea9e/scratchpad/dbreview/covered_ids.txt (Drive ids already read) and covered_titles.txt (lower-case file names already read). The Drive contains many exact duplicates (same title and size, different ids, often created Feb 2025). For a file whose id is covered, or whose title (lower case) is in covered_titles.txt with the same content, record read_status=covered and do not re-read unless it looks like a different version. For duplicates inside your folder, read one copy and mark the others duplicate_of=<id>.

What to do with each unique, uncovered file:
- Readable documents (PDF, xlsx, docx, pptx, csv, txt, msg if readable): read it. Large scanned PDFs: read the extracted text; note if the text is incomplete.
- Binary/specialist formats (LAS, DLIS, SEG-Y, zip, 7z, rar, dwg, petrel, mdb, exe, video): do not read; record metadata, what the name/size implies, and whether it matters (e.g. a SEG-Y volume is the missing seismic package G-55).
- Photos/images: read only if they look technical (logs, maps, schematics, tables); otherwise metadata only.
- Administrative noise (invoices, receipts, payroll, routine correspondence): skim and summarise in one line; flag anything with cost, liability, regulatory or technical value.
If the folder is very large (hundreds of unique uncovered files), you must still inventory all of them, but read in priority order: technical (wells, logs, tests, pressure, PVT, core, geology, seismic, reserves, production) > regulatory/contract > operations/HSE/costs > admin. Mark what you could not reach as read_status=not_read with the reason. Never guess the content of a file you did not read.

Interpretation standard: units on every number, provenance (file id + sheet/page), Spanish documents interpreted into English, dates as YYYY-MM-DD. Compare against the repository: flag anything that contradicts, corrects, confirms or adds to the review, the briefing or an open gap (cite the G-number). Do not interpolate or invent values.

Outputs (write with Bash/Write into /tmp/claude-0/-home-user-git-practice/cfddd84a-7303-5f1c-8e6b-47d4ec46ea9e/scratchpad/dbreview/, prefix = your folder key):
1. <key>_inventory.csv: id,title,mimeType,size_bytes,modifiedTime,folder_path,duplicate_of,read_status (read|partial|covered|duplicate|binary|image_skipped|admin_skim|unreadable|not_read)
2. <key>_review.csv (one row per unique file you read or assessed): id,folder_path,title,doc_type,doc_date,issuer_author,summary,key_data_with_units,interpretation,relevance (high|medium|low|none),use_in_presentation (slide/topic or "no"),repo_impact (confirms|corrects|adds|contradicts|none + what, G-numbers)
3. <key>_findings.md (max ~1,200 words): the most important new facts and corrections for the presentation, ranked; contradictions with the repository; gaps closed or opened; files that should be obtained in native form (e.g. SEG-Y, LAS); counts (files inventoried, unique, read, covered, duplicates, binaries, not read).
Return a short summary (under 250 words) with those counts and the top five findings.
