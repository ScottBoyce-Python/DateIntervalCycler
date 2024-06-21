import pytest


def pytest_addoption(parser: pytest.Parser):
    parser.addoption("--run-slow-skip", action="store_true", help="Run tests marked as skipped")


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config: pytest.Config, items: list):
    # pytest --run-slow-skip
    #                     -> run skipped functions and skip subset functions
    if config.getoption("--run-slow-skip"):
        for item in items:
            if "slow_skip" in item.keywords:
                item.own_markers = [marker for marker in item.own_markers if marker.name not in ("skip", "skipif")]
            if "subset" in item.keywords:
                item.add_marker(
                    pytest.mark.skip(reason="--run-slow-skip option disables subset tests cuz they are redundant.")
                )  # or could just delete the item from items list with pop_item_words()


# def pop_item_words(markers: list[str], items: list):
#     drop = []
#     for it, item in enumerate(items):
#         for marker in markers:
#             if marker in item.keywords:
#                 drop.append(it)
#     if drop:
#         drop = drop[::-1]
#         for it in drop:
#             items.pop(it)
