
This directory contains regression tests.  Running `make` produces out/demo-*.pdf files that you may inspect visually.  Versioned pandoc executables must on your path (see the Makefile).

Note that equation number locations are different for piped processing because the filter is unaware that the target format is ultimately tex (it is asked to provide json).  Also, the spacing in the output pdf files varies because of pandoc.  Everything else should visually remain the same.
