.PHONY: venv
venv:
	# rpm-lockfile-prototype depends on dnf bindings (the python3-dnf package on fedora)
	#   => need --system-site-packages
	if command -v uv; then \
		uv venv --system-site-packages --clear; \
		uv pip install -r requirements-dev.txt; \
	else \
		if command -v virtualenv; then \
			virtualenv --system-site-packages --clear .venv; \
		else \
			python3 -m venv --system-site-packages --clear .venv; \
		fi; \
		.venv/bin/pip install -r requirements-dev.txt; \
	fi

.PHONY: rpms.lock.yaml
rpms.lock.yaml:
	.venv/bin/rpm-lockfile-prototype deps/rpm/rpms.in.yaml --outfile deps/rpm/rpms.lock.yaml
