#!/bin/bash
# usage: report_pdf.sh [report.md] [out.pdf]; md -> HTML (pandoc, Typora GitHub theme) -> PDF (Chrome, A4).
set -e
md=${1:-report/report.md}; out=${2:-${md%.md}.pdf}
root=$(cd "$(dirname "$md")" && pwd)
here=$(cd "$(dirname "$0")" && pwd)/report
html=$(mktemp -d)/report.html
{ echo "<style>"; cat "$here/typora-github.css"; echo '@page{size:A4;margin:20mm 13mm} html{font-size:16px !important} body{font-family:"Open Sans","Apple SD Gothic Neo","Helvetica Neue",Helvetica,Arial,sans-serif} #write{max-width:none;padding:0;zoom:0.86} img{max-width:100%} table{width:100%} section.level3{break-inside:avoid} h2,h3{break-after:avoid}'; echo "</style>"; } > /tmp/report_head.html
pandoc "$md" -s --section-divs --template "$here/template.html" -f gfm -t html -H /tmp/report_head.html -B "$here/before.html" -A "$here/after.html" --metadata pagetitle=" " -o "$html"
sed -i '' "s|src=\"\.\./|src=\"file://$root/../|g; s|src=\"\./|src=\"file://$root/|g" "$html"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --no-pdf-header-footer --print-to-pdf="$out" "file://$html" 2>/dev/null
rm -rf "$(dirname "$html")" /tmp/report_head.html
echo "$out ($(pdfinfo "$out" | awk '/Pages/{print $2}') pages)"
