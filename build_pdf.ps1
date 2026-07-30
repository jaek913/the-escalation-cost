# =====================================================================
# Lagging Truth - series PDF build  (Research-to-Publication Standard)
# =====================================================================
# Reusable paper-build script. It:
#   1. writes the standard header.tex + metadata.yaml to TEMP as UTF-8 *no-BOM*
#      (via [System.IO.File]::WriteAllText - avoids the PowerShell UTF-16/BOM
#       redirection trap that corrupts a redirected/Set-Content file),
#   2. (if the paper has an appendix) demotes every appendix heading one level
#      in a TEMP copy, so the -1 heading shift renders "Appendix A" as a
#      top-level \section instead of demoting its leading "# " to a paragraph,
#   3. renders manuscript_rendered.md [+ demoted appendix] with pandoc + xelatex.
#
# Only the committed slug-named PDF is kept (no committed PDF_Build/ folder) -
# this matches the current-Standard convention (Adaptation / MSC), recorded in
# the MSC ledger as D-026.
#
# PER PAPER, edit only the four variables in the SETTINGS block.
# Requires: pandoc + xelatex (MiKTeX/TeX Live) on PATH; Cambria + Cambria Math
# installed (Windows / Office fonts).
#
# How to run (from the repo root, with this script there):
#     .\build_pdf.ps1
#   or, if execution policy complains:
#     powershell -ExecutionPolicy Bypass -File .\build_pdf.ps1
#
# SERIES DEVIATION IN THIS COPY (one, and only one): the success check below
# asserts the output PDF was ACTUALLY REWRITTEN by this run, by capturing the
# pre-build LastWriteTime and requiring the post-build stamp to be newer. The
# series script reports SUCCESS whenever the output file merely EXISTS, which
# means a permission-denied write (the usual cause: the PDF is open in a
# viewer) leaves the previous build on disk and still prints SUCCESS. That is
# the same defect class as DECISIONS 78 - a gate whose surrounding procedure
# reads the wrong signal - and it is closed here structurally rather than by
# operator discipline. Recommended for backport to the other papers.
# =====================================================================

$ErrorActionPreference = "Stop"

# --------------------------- SETTINGS -------------------------------
$PaperDir   = Join-Path $PSScriptRoot "paper"
$Slug       = "the-escalation-cost"
$Manuscript = Join-Path $PaperDir "the-escalation-cost.rendered.md"
$Appendix   = $null   # Appendices A-G are inline in the manuscript (set a path here only for a separate appendix)
# --------------------------------------------------------------------

$Output = Join-Path $PaperDir "$Slug.pdf"

Write-Host ""
Write-Host "=== Lagging Truth PDF build: $Slug ===" -ForegroundColor Cyan

# --- pre-flight: tools on PATH ---
foreach ($t in @("pandoc","xelatex")) {
    if (-not (Get-Command $t -ErrorAction SilentlyContinue)) {
        Write-Host "ERROR: '$t' not found on PATH." -ForegroundColor Red
        Write-Host "       pandoc: https://pandoc.org/installing.html" -ForegroundColor Red
        Write-Host "       xelatex: install MiKTeX (https://miktex.org) or TeX Live" -ForegroundColor Red
        exit 1
    }
    Write-Host ("[ OK ] {0} -> {1}" -f $t, (Get-Command $t).Source)
}
if (-not (Test-Path $Manuscript)) { Write-Host "ERROR: manuscript not found: $Manuscript" -ForegroundColor Red; exit 1 }
Write-Host "[ OK ] manuscript: $Manuscript"

# --- stale-output guard: remember the pre-build stamp (see SERIES DEVIATION) ---
$PreBuildStamp = $null
if (Test-Path $Output) {
    $PreBuildStamp = (Get-Item $Output).LastWriteTime
    Write-Host ("[ OK ] existing PDF stamp recorded: {0}" -f $PreBuildStamp)
} else {
    Write-Host "[ OK ] no existing PDF (first build)"
}

# --- series header.tex (Cambria + Cambria Math; matches Papers 1 and 2) ---
# Identical build core; the only paper-specific content (title/author/date)
# lives in the manuscript_rendered.md YAML front matter, NOT here.
$Header = @'
% header.tex - Lagging Truth series preamble (Cambria + Cambria Math)
% --- fonts (Ligatures=NoCommon applies to all four faces) ---
\usepackage{unicode-math}
\setmainfont{Cambria}[Ligatures=NoCommon]
\setmathfont{Cambria Math}
% --- spacing / typography ---
\usepackage[margin=1.25in]{geometry}
\linespread{1.15}
\setlength{\parskip}{6pt}
\setlength{\parindent}{0pt}
\setlength{\emergencystretch}{3em}
% --- math ---
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{mathtools}
\usepackage{cases}
% --- checkmark glyph (\ding{51}) ---
\usepackage{pifont}
% --- section title formatting ---
\usepackage{titlesec}
\titleformat{\section}{\Large\bfseries}{\thesection}{1em}{}
\titleformat{\subsection}{\large\bfseries}{\thesubsection}{1em}{}
\titleformat{\subsubsection}{\normalsize\bfseries}{\thesubsubsection}{1em}{}
% --- tables ---
\usepackage{booktabs}
\usepackage{array}
\usepackage{tabularx}
\usepackage{longtable}
% --- SERIES DEVIATION (2 of 2, this paper only): wide numeric tables ---
% This paper's sector tables carry 14-character FRED codes (R4238IM163SCEN,
% MRTSIR452USS) in a narrow column. Those codes contain no break opportunity, so
% at full body size they overrun their cell and print ON TOP of the next column:
% "MRTSIR452USS" and "0.0650" interleaved as MRTSIR4520U.S0S650 on page 32, 44
% overlapping character pairs on that page alone. Shrinking the table body is the
% fix; it is scoped to tables so body type is untouched.
%
% This was removed once, on the reasoning that four-decimal display rounding had
% eliminated the width pressure. That was wrong: rounding fixed the NUMERIC
% columns, and the driver here is the SECTOR NAMES, which rounding cannot touch.
% The regression shipped because the collision check in use at the time compared
% WORDS, and overlap severe enough to interleave characters is extracted as a
% single word token - so the check had nothing to compare and reported zero. It
% was caught by the author reading the page. Collision detection must be
% CHARACTER-level; word-level is structurally blind to the worst case.
\usepackage{etoolbox}
\AtBeginEnvironment{longtable}{\small}
\setlength{\tabcolsep}{4pt}
% --- code blocks: wrap long lines if any paper has code ---
\usepackage{fvextra}
\DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,breakanywhere,commandchars=\\\{\}}
% --- title rule under the title ---
\usepackage{titling}
\pretitle{\begin{center}\LARGE}
\posttitle{\par\end{center}\vspace{1em}\begin{center}\rule{0.35\textwidth}{0.5pt}\end{center}\vspace{0.5em}}
% --- hyperref last ---
\usepackage[colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue]{hyperref}
% --- equation numbering within section ---
\numberwithin{equation}{section}
% --- allow long URLs to break ---
\usepackage{xurl}
'@

# --- series metadata.yaml (settings only; geometry lives in header.tex to avoid an option clash) ---
# map the manuscript's raw Unicode check/cross marks to pifont glyphs at runtime;
# kept out of the here-string so build_pdf.ps1 stays pure ASCII (PS 5.1 reads a no-BOM script as ANSI).
# pifont is already loaded above; Cambria has no glyph for U+2713 / U+2717.
$Header = $Header + "`n% raw-Unicode mark mapping (added by build script)`n\usepackage{newunicodechar}`n\newunicodechar{$([char]0x2713)}{\ding{51}}`n\newunicodechar{$([char]0x2717)}{\ding{55}}`n"

$Metadata = @'
---
documentclass: article
fontsize: 11pt
papersize: letter
colorlinks: true
linkcolor: blue
urlcolor: blue
citecolor: blue
header-includes:
  - \usepackage{microtype}
...
'@

$utf8NoBom    = New-Object System.Text.UTF8Encoding($false)
$Tmp          = [System.IO.Path]::GetTempPath()
$HeaderPath   = Join-Path $Tmp "lt_header.tex"
$MetadataPath = Join-Path $Tmp "lt_metadata.yaml"
[System.IO.File]::WriteAllText($HeaderPath,   $Header,   $utf8NoBom)
[System.IO.File]::WriteAllText($MetadataPath, $Metadata, $utf8NoBom)
Write-Host "[ OK ] header.tex + metadata.yaml written to TEMP (UTF-8 no-BOM)"

# --- assemble inputs; demote appendix headings one level if present ---
# PDF-only TEMP transforms (committed artifacts untouched):
#  - ASCII '(c) 2026 Jae Kim' -> copyright glyph (source stays pure ASCII per repo convention)
$man = [System.IO.File]::ReadAllText($Manuscript, $utf8NoBom)
$man = $man.Replace('(c) 2026 Jae Kim', ([string][char]0x00A9 + ' 2026 Jae Kim'))
#  - allow line breaks inside decimal slash-runs (e.g. 1.0057/1.0099/1.0121) in prose
$man = [regex]::Replace($man, '(?<=\d)/(?=\d+\.\d)', '/\allowbreak ')
#  - allow line breaks inside long comma-joined code runs (e.g. the registered
#    sector class lists in Section 11, rendered from the ledger as
#    "A31SIS,A36SIS,AMDMIS,..." with no spaces). Without this the run is a single
#    unbreakable token ~100 characters wide and xelatex sets it straight off the
#    right edge of the paper - measured at 222.8pt past the text block and 134.8pt
#    beyond the physical page before the fix (Phase 5c PDF QA, DECISIONS 131).
#    The trailing space after \allowbreak is consumed by TeX as the control-word
#    terminator, so no visible space is introduced - same idiom as the line above.
$man = [regex]::Replace($man, '(?<=[A-Z0-9]),(?=[A-Z])', ',\allowbreak ')
#  - allow line breaks INSIDE long FRED sector codes (R4238IM163SCEN,
#    MRTSIR452USS). These are 12-14 characters of unbroken capitals and digits
#    with no natural break point, and the Sector column in TBL-2 and TBL-4 is
#    about 56pt where the code needs about 62pt - so xelatex cannot wrap them and
#    sets them straight over the next column, printing "MRTSIR452USS" and
#    "0.0650" interleaved as MRTSIR4520U.S0S650. Shrinking the table body was not
#    enough on its own. A break opportunity is inserted at the digit-to-letter
#    boundary (R4238IM163|SCEN, MRTSIR452|USS), which is used ONLY if the line
#    needs it and is invisible otherwise; the characters themselves are unchanged.
$man = [regex]::Replace($man, '(?<=^|[^A-Za-z0-9])([A-Z]{1,6}\d{2,4}[A-Z]{0,3}\d{0,3})(?=[A-Z]{2,4}(?![a-z]))', '$1\allowbreak ')
$ManTmp = Join-Path $Tmp "lt_manuscript_pdf.md"
[System.IO.File]::WriteAllText($ManTmp, $man, $utf8NoBom)
Write-Host "[ OK ] PDF-only transforms applied -> $ManTmp"

# --- PDF-only citation transform ---------------------------------------
# The manuscript carries pandoc-style [@key] citations and [@key]: definitions.
# Those keys are load-bearing: verify.py ties them both ways and fails on any
# orphan or dangling citation, which is how the reference list is proved clean.
# The build has no --citeproc step, so without this transform the keys reach the
# PDF verbatim - the body printing "[@Lee-1997a]" and the reference list printing
# as a run-on block with "[@Key]:" prefixes, neither of which matches the series.
# The transform rewrites them to the series' author-year form for the PDF ONLY;
# the committed artifacts keep their keys and the gate stays green. It fails the
# build rather than degrading silently on any unparseable, undefined or
# ambiguous citation.
$CiteTmp = Join-Path $Tmp "lt_manuscript_cited.md"
$CiteScript = Join-Path $PSScriptRoot "verification\pdf_citations.py"
& python $CiteScript $ManTmp $CiteTmp
if ($LASTEXITCODE -ne 0) {
    Write-Host "=== BUILD FAILED === citation transform reported an error above." -ForegroundColor Red
    exit 1
}
$ManTmp = $CiteTmp
$Inputs = @($ManTmp)
if ($Appendix -and (Test-Path $Appendix)) {
    $apx = [System.IO.File]::ReadAllText($Appendix, $utf8NoBom)   # UTF-8 read (Get-Content defaults to ANSI on PS 5.1 and mangles em/en-dashes)
    $apx = [regex]::Replace($apx, '(?m)^(#{1,6}) ', '#$1 ')   # +1 level to every ATX heading
    $apx = "\newpage`r`n`r`n" + $apx                          # page break before the appendix
    $ApxTmp = Join-Path $Tmp "lt_appendix_demoted.md"
    [System.IO.File]::WriteAllText($ApxTmp, $apx, $utf8NoBom)
    $Inputs += $ApxTmp
    Write-Host "[ OK ] appendix headings demoted -> $ApxTmp"
}

# --- render ---
Write-Host "Building PDF -> $Output" -ForegroundColor Cyan
& pandoc @Inputs `
    --pdf-engine=xelatex `
    --metadata-file="$MetadataPath" `
    --include-in-header="$HeaderPath" `
    --shift-heading-level-by=-1 `
    --output="$Output"

# --- success check: EXISTS *and* actually rewritten by this run ---
if (-not (Test-Path $Output)) {
    Write-Host "=== BUILD FAILED === (no output produced; see xelatex errors above)" -ForegroundColor Red
    exit 1
}
$PostBuildStamp = (Get-Item $Output).LastWriteTime
if ($PreBuildStamp -and ($PostBuildStamp -le $PreBuildStamp)) {
    Write-Host "=== BUILD FAILED === STALE OUTPUT" -ForegroundColor Red
    Write-Host ("The PDF on disk was NOT rewritten by this run (stamp unchanged: {0})." -f $PostBuildStamp) -ForegroundColor Red
    Write-Host "The usual cause is that the PDF is open in a viewer, so the write was denied." -ForegroundColor Red
    Write-Host "Close the PDF and re-run. Do NOT ship this file - it is the previous build." -ForegroundColor Red
    exit 1
}
$kb = [math]::Round((Get-Item $Output).Length / 1KB, 1)
Write-Host "=== SUCCESS ===" -ForegroundColor Green
Write-Host ("PDF: {0}  ({1} KB, modified {2})" -f $Output, $kb, $PostBuildStamp)
Write-Host "Stale-output guard: PASSED (file rewritten by this run)."
