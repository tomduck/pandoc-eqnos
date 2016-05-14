

all: out/demo.pdf out/demo.tex out/demo.html out/demo.md out/demo.epub \
     out/demo2.pdf out/demo2.tex out/demo2.html out/demo2.md out/demo2.epub \
     out/demo3.pdf out/demo3.tex out/demo3.html out/demo3.md out/demo3.epub

out/%.pdf: %.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< --filter pandoc-eqnos --variable geometry:margin=1in -o $@

out/%.tex: %.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< --filter pandoc-eqnos -o $@

out/%.html: %.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< -t html --filter pandoc-eqnos --standalone --mathml -o $@

out/%.epub: %.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< -t epub3 --filter pandoc-eqnos -o $@

out/%.md: %.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< -t markdown --filter pandoc-eqnos -o $@

out/%.json: %.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< -t json -o $@

restore: clean
	git checkout out/demo.epub
	git checkout out/demo.html
	git checkout out/demo.md
	git checkout out/demo.pdf
	git checkout out/demo.tex

	git checkout out/demo2.epub
	git checkout out/demo2.html
	git checkout out/demo2.md
	git checkout out/demo2.pdf
	git checkout out/demo2.tex

	git checkout out/demo3.epub
	git checkout out/demo3.html
	git checkout out/demo3.md
	git checkout out/demo3.pdf
	git checkout out/demo3.tex

.PHONY: clean

clean:
	rm -rf out
