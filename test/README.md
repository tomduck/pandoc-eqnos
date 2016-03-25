
This directory contains regression tests.  Running `make` produces out/demo-*.pdf files that you may inspect visually.  Note that the Makefile expects specific numbered pandoc targets (e.g., pandoc-1.17.0.2) are available from the shell.  You will likely have to adapt the Makefile to use what is available on your system.

Note that equation number locations are different for piped processing because the filter is unaware that the target format is ultimately tex (it is asked to provide json).  Also, the spacing in the output pdf files varies because of pandoc.  Everything else should visually remain the same.
