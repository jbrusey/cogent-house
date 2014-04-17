# all: $(rnwfile).pdf

# $(rnwfile).tex: $(rnwfile).rrst
#   Rscript -e "library(knitr); knit('$(rnwfile).Rnw')"

# clean:
#   -rm *.log *.aux


all:
	Rscript -e "library(knitr); knit('testReport.rrst')"
	rst2html.py "testReport.rst" > "testReport.html"