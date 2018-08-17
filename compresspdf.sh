#!/bin/bash

for fin in "$@"; do
	ext="${fin##*.}"
	if [ "$ext" == "pdf" ]; then
		fout="${fin%.*}_light.pdf"
		echo "$fin > $fout"

		gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/default -dNOPAUSE -dQUIET -dBATCH -sOutputFile=$fout $fin
	else
		echo "$fin is not a pdf file"
	fi
done
