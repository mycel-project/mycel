from typing import Union
from bs4 import BeautifulSoup, Tag, NavigableString, Comment

from ..utils.node_builders import create_root, create_text, create_element

from ..nodes import Root, Element, Text, Comment as AstComment

class HtmlParser:
    def parse(self, html: str) -> Root:
        soup = BeautifulSoup(html, "html.parser")
        self.supported_tags = ["html", "body", "header", "nav", "h1", "h2", "h3", "h4", "h5", "h6", "div", "p", "span", "a", "li","ul", "strong", "section", "article", "main", "footer", "em", "b", "br", "code", "pre", "blockquote", "ol", "img", "figure", "figcaption"]
        # PLUTOT FAIRE BLACKLIST, VIRER TOUT CE QUI EST DANS LA BLACKLIST (script, style, iframe, head, form, input/button, ...)
        children = [
            self._parse_node(child) 
            for child in soup.children 
            if self._is_valid_node(child)
        ]
        
        return create_root(children)

    def _parse_node(self, bs_node) -> Union[Element, Text, None]: # No AstComment handle at the moment
        
        if isinstance(bs_node, NavigableString):

            if isinstance(bs_node, Comment):
                return None
            else:
                return create_text(str(bs_node))


        elif isinstance(bs_node, Tag):
            if not bs_node.name in self.supported_tags:
                print(bs_node.name)
                return None
            children = [
                self._parse_node(child)
                for child in bs_node.children
                if self._is_valid_node(child)
            ]
            
            return create_element(
                tag=bs_node.name,
                children=children,
                properties=dict(bs_node.attrs)
            )
    
    def _is_valid_node(self, node) -> bool:
        if isinstance(node, NavigableString):
            return str(node).strip() != ""
        return True
