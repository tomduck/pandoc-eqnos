
extensions = .pdf .html .epub .tex .docx .json .md

all: $(addprefix out/demo,$(extensions)) \
     $(addprefix out/demo2,$(extensions)) \
     $(addprefix out/demo3,$(extensions))

out/%.pdf: %.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< --filter pandoc-eqnos --variable urlcolor=blue -o $@

out/%.html: %.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< --filter pandoc-eqnos --standalone --mathml -o $@

out/%.epub: %.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< -t epub3 --filter pandoc-eqnos -o $@

out/%.tex: %.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< --filter pandoc-eqnos -o $@

out/%.docx: %.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< --filter pandoc-eqnos -o $@

out/%.json: %.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< --filter pandoc-eqnos -o $@

out/%.md: %.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< --filter pandoc-eqnos -o $@

restore: clean
	for ext in $(extensions) ; do \
    git checkout out/demo.$$ext ; \
    done

	for ext in $(extensions) ; do \
    git checkout out/demo2.$$ext ; \
    done

	for ext in $(extensions) ; do \
    git checkout out/demo3.$$ext ; \
    done

.PHONY: clean

clean:
	rm -rf out
