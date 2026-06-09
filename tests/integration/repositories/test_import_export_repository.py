from datetime import datetime, timezone
from src.models.export import FullExport, CollectionExport

def test_repo_export_and_import(import_export_repo, create_user, create_col, create_node, user_service):
    user_source, _ = create_user()
    col1 = create_col(user_id=user_source.id)
    col2 = create_col(user_id=user_source.id)
    for i in range(3):
        create_node(col_id=col1.id, user_id=user_source.id, content=f"col1_node_{i}")
    for i in range(2):
        create_node(col_id=col2.id, user_id=user_source.id, content=f"col2_node_{i}")

    raw_source_data = import_export_repo.get_full_user_data(user_source.id)
    collections_export = []
    for col in raw_source_data["collections"]:
        nodes = [n for n in raw_source_data["nodes"] if n.collection_id == col.id]
        collections_export.append(CollectionExport(**col.model_dump(), nodes=nodes, reviews=[]))

    export_payload = FullExport(
        version="1.0",
        exported_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        user=raw_source_data["user"],
        collections=collections_export
    )

    user_service.delete_user(user_source.id)

    user_target, _ = create_user()
    
    export_payload.user.id = user_target.id 
    
    import_export_repo.import_full_user_data(export_payload)

    target_data = import_export_repo.get_full_user_data(user_target.id)

    assert target_data["user"].id == user_target.id
    assert len(target_data["collections"]) == 2
    assert len(target_data["nodes"]) == 5
    
    source_node_ids = {n.id for n in raw_source_data["nodes"]}
    target_node_ids = {n.id for n in target_data["nodes"]}
    assert source_node_ids == target_node_ids
