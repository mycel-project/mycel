from src.ast.contracts import Literal

class TestNodes:
    def test_node(self):
        lit = Literal(type="test")
        assert lit.type=="test"
