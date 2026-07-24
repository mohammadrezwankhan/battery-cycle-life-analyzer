.PHONY: test demo clean

test:
	python -m pytest tests/ -v

demo:
	python -m bcla --model all

notebook:
	jupyter nbconvert --to notebook --execute notebooks/demo.ipynb --output notebooks/demo_executed.ipynb

clean:
	rm -rf __pycache__ .pytest_cache bcla/__pycache__ tests/__pycache__
	rm -rf *.egg-info dist build
	rm -f bcla_demo.png
