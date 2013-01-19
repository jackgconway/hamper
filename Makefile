dev:
	rm hamper/plugins/dropin.cache
	PYTHONPATH=.:$$PYTHONPATH python scripts/hamper
