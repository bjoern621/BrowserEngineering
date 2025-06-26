import time
import unittest
from src.css_parser.descendant_selector import DescendantSelector
from src.css_parser.tag_selector import TagSelector
from src.nodes.tag_element import TAGElement


def build_deep_tree(depth: int):
    """
    Builds a deep DOM tree structure with the specified depth.
    It looks like this:
    ```
    <div>
        <div>
            <div>
                ...
            </div>
        </div>
    </div>
    ```"""

    root = TAGElement("div", None, {})
    node = root
    for _ in range(depth - 1):
        child = TAGElement("div", node, {})
        node.children.append(child)
        node = child
    return root, node


# Don't know how to run but the test works
@unittest.skip("Performance test")
class TestDescendantSelectorPerformance(unittest.TestCase):

    def test_runtime(self):
        for depth in [
            10,
            20,
            22,
            24,
            26,
            50,
            500,
            5_000,
            50_000,
            500_000,
            5_000_000,
        ]:
            _root, leaf = build_deep_tree(depth)

            # Old Impl
            # selector = TagSelector("div")
            # for _ in range(depth):
            #     descendant = TagSelector("div")
            #     selector = DescendantSelector(selector, descendant)

            # New Impl
            selector = DescendantSelector([TagSelector("div") for _ in range(depth)])

            start = time.time()
            selector.matches(leaf)
            elapsed = time.time() - start

            print(f"Time: {elapsed:.4f} seconds (d={depth})")


if __name__ == "__main__":
    TestDescendantSelectorPerformance().test_runtime()
