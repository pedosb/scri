#####
# Autor: Pedro Batista
# Data: 10/04/2011
#####

LATEX = latex
BIBTEX = bibtex
DVIPDF = dvipdf
RM = rm -f

MAIN = relatorio
TARGET = $(MAIN).pdf
DVI = $(MAIN).dvi

SOURCE = $(MAIN).tex \
		 bibliografia.bib

all : $(TARGET)

$(TARGET) : $(DVI)
	$(DVIPDF) $(MAIN)

$(DVI) : $(SOURCE)
	$(LATEX) $(MAIN)
	-$(BIBTEX) $(MAIN)
	$(LATEX) $(MAIN)
	$(LATEX) $(MAIN)

clean :
	$(RM) $(MAIN)\.{aux,bbl,blg,dvi,log,out} *~

distclean :
	$(RM) $(TARGET)
