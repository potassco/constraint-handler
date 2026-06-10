def pytest_configure(config):
    config.option.benchmark_quiet = True
    config.option.benchmark_min_rounds = 1
