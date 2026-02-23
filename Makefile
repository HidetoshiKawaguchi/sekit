release:
	rm -rf dist build *.egg-info
	uv build
	uv run twine upload dist/*.whl dist/*.tar.gz

release-test:
	rm -rf dist build *.egg-info
	uv build
	uv run twine upload --repository testpypi dist/*.whl dist/*.tar.gz
