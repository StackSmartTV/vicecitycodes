.PHONY: feed test

feed:
	python3 -m sitegen.build

test:
	python3 -m unittest discover -s tests -v
