cc = /usr/local/apps/tex_live/current/bin/x86_64-linux/pdflatex

default: pdf

pdf:  report.tex
	$(cc) report.tex
	$(cc) report.tex

clean:
	-@rm -f *.aux
	-@rm -f *.log
	-@rm -f *.pdf
	-@rm -f *.toc
