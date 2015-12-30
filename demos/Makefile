

all: out/demo.pdf out/demo.tex out/demo.html out/demo.md out/demo.epub

out/demo.pdf out/demo.tex: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< --filter pandoc-eqnos -o $@

out/demo.html: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< -t html --filter pandoc-eqnos --standalone --mathml -o $@

out/demo.epub: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< -t epub3 --filter pandoc-eqnos -o $@

out/demo.md: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< -t markdown --filter pandoc-eqnos -o $@

out/demo.json: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< -t json -o $@

restore: clean
	git checkout out/demo.epub
	git checkout out/demo.html
	git checkout out/demo.md
	git checkout out/demo.pdf
	git checkout out/demo.tex


.PHONY: clean

clean:
	rm -rf out
