.PHONY: test validate-skills demo

test:
	./tests/test-shell.sh
	python3 ./tests/test-repository.py

validate-skills:
	python3 ./tests/test-repository.py --skills-only

demo:
	node ./skills/technical-deck/scripts/new_technical_deck.mjs --output=examples/technical-diagram-demo.pptx
	python3 ./skills/technical-deck/scripts/validate_pptx.py examples/technical-diagram-demo.pptx
