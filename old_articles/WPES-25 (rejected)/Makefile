
TEX = main.tex Texts/*.tex schema/*.tex
ISPELLPAT = -ktexskip1 +cref,Cref,url

all: main.pdf

main.pdf: ${TEX} bib.bib
	latexmk -pdf main.tex

spelling: ${TEX}
	for file in ${TEX}; do \
          ispell -t ${ISPELLPAT} -b -d american -p ./paper.dict $$file; \
        done

clean:
	rm -f *.tex.bak Texts/*.tex.bak
	latexmk -pdf -c main.tex

distclean: clean
	latexmk -pdf -C main.tex

