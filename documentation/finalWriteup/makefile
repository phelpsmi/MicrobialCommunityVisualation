

default: pdf

pdf: analysis.PNG Comparison.PNG loading.PNG report.tex
	pdflatex report.tex
	pdflatex report.tex

clean:
	-@rm -f *.aux
	-@rm -f *.log
	-@rm -f *.pdf
	-@rm -f *.toc
