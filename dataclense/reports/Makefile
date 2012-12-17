output = .output
rnwfile = YieldReport
backup = .backup

SWEAVE = R CMD Sweave


all: $(rnwfile).pdf

pdf: $(rnwfile).pdf

$(rnwfile).pdf: $(rnwfile).tex
	pdflatex $(rnwfile).tex

$(rnwfile).tex: $(rnwfile).Rnw
	R CMD Sweave $(rnwfile).Rnw

clean:
	-rm *.tex *.log *.aux


#	#-mkdir $(output)
#	#-cp *.sty $(output)
#	#-mv *.tex *.pdf *.eps $(output)

# all:
# 	$(SWEAVE)
#     	# #R CMD Sweave $(rnwfile).Rnw
# 	# #R CMD Sweave YieldReport.Rnw
# 	# $(SWEAVE) YieldReport.Rnw
#     	# -mkdir $(output)
#     	# -cp *.sty $(output)
#     	# -mv *.tex *.pdf *.eps $(output)
#     	# cd $(output); texify --run-viewer --pdf $(rnwfile).tex 

# tex:
#     	cd $(output); texify --run-viewer --pdf $(rnwfile).tex

# clean:
#     	-rm $(output)/*

# backup:
#     	-mkdir $(backup)
#     	cp  $(output)/$(rnwfile).pdf $(backup)/$(rnwfile).pdf