from src.models.node import Node
from src.models.node_content import NodeContent
from src.models.node_data import NodeData
import time

from src.services.node_format_service import NodeFormatService

def test_emphasize_region():
    now = int(time.time() * 1000)

    node = Node(
        id=1,
        collection_id=1,
        type=0,
        created_at=now,
        updated_at=now,
        due=now,
        data=NodeData(),
        content=NodeContent.from_input({
            "0": """
SuperMemo (from Super Memory) is a learning method and software package developed by SuperMemo World and SuperMemo R&D with Piotr Woźniak in Poland from 1985 to the present. It is based on research into long-term memory, and is a practical application of the spaced repetition learning method that has been proposed for efficient instruction by a number of psychologists as early as in the 1930s.
The method is available as a computer program for Windows, Windows CE, Windows Mobile (Pocket PC), Palm OS (PalmPilot), etc.
...Course...
software by the same company (SuperMemo World) can also be used in a web browser or even without a computer.[4]
The desktop version of SuperMemo started as a flashcard software (SuperMemo 1.0 (1987)).[5] It has supported incremental reading since SuperMemo 10 (2000).[6]"""
        })
    )

    service = NodeFormatService()
    formatted_node = service.emphasize_region(node, """It is based on research into long-term memory, and is a practical application of the spaced repetition learning method that has been proposed for efficient instruction by a number of psychologists as early as in the 1930s.
The method is available as a computer program for Windows, Windows CE, Windows Mobile (Pocket PC), Palm OS (PalmPilot), etc.""" )
    formatted_node = service.emphasize_region(formatted_node, """...Course...
software by the same company (SuperMemo World) can also be used in a web browser or even without a computer.[4]
The desktop version of SuperMemo started as a flashcard software (SuperMemo 1.0 (1987)).[5] It has supported incremental reading since SuperMemo 10 (2000).[6]""" )
    print()
    print()
    print(formatted_node.content.fields["0"].strip())
