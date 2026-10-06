AUX_DIR="auxiliary-files"
OUTPUT_DIR="output-files"
TARGET=main.tex

all:
	mkdir -p $(OUTPUT_DIR)
	latexmk -pdflatex='xelatex' -file-line-error -pdf -output-directory=$(OUTPUT_DIR)\
		$(TARGET)

clean:
	rm -rf $(OUTPUT_DIR)
