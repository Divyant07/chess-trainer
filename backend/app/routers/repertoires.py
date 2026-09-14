from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.repertoire import Node, Repertoire
from app.models.training import TrainingStats
from app.schemas.repertoire import NodeCreate, NodeOut, RepertoireCreate, RepertoireOut
from app.services.chess_logic import STARTING_FEN, IllegalMoveError, apply_move

router = APIRouter(prefix="/repertoires", tags=["repertoires"])


@router.post("", response_model=RepertoireOut)
def create_repertoire(payload: RepertoireCreate, db: Session = Depends(get_db)):
    if payload.color not in ("white", "black"):
        raise HTTPException(400, "color must be 'white' or 'black'")

    repertoire = Repertoire(name=payload.name, color=payload.color)
    db.add(repertoire)
    db.commit()
    db.refresh(repertoire)

    # Every repertoire gets a root node at the starting position, with no
    # move leading into it -- this is what nodes hang off of.
    root = Node(repertoire_id=repertoire.id, parent_id=None, fen=STARTING_FEN, depth=0)
    db.add(root)
    db.commit()

    return repertoire


@router.get("", response_model=list[RepertoireOut])
def list_repertoires(db: Session = Depends(get_db)):
    return db.query(Repertoire).all()


@router.get("/{repertoire_id}", response_model=RepertoireOut)
def get_repertoire(repertoire_id: int, db: Session = Depends(get_db)):
    repertoire = db.get(Repertoire, repertoire_id)
    if not repertoire:
        raise HTTPException(404, "Repertoire not found")
    return repertoire


@router.get("/{repertoire_id}/nodes", response_model=list[NodeOut])
def list_nodes(repertoire_id: int, db: Session = Depends(get_db)):
    """Returns the full flat list of nodes; frontend reassembles the tree
    client-side using parent_id, which is simpler than recursive queries
    for a tree of this size."""
    repertoire = db.get(Repertoire, repertoire_id)
    if not repertoire:
        raise HTTPException(404, "Repertoire not found")
    return db.query(Node).filter(Node.repertoire_id == repertoire_id).all()


@router.post("/{repertoire_id}/nodes", response_model=NodeOut)
def add_node(repertoire_id: int, payload: NodeCreate, db: Session = Depends(get_db)):
    repertoire = db.get(Repertoire, repertoire_id)
    if not repertoire:
        raise HTTPException(404, "Repertoire not found")

    if payload.parent_id is None:
        parent = db.query(Node).filter(
            Node.repertoire_id == repertoire_id, Node.parent_id.is_(None)
        ).first()
    else:
        parent = db.get(Node, payload.parent_id)

    if not parent or parent.repertoire_id != repertoire_id:
        raise HTTPException(404, "Parent node not found in this repertoire")

    try:
        result = apply_move(parent.fen, payload.move)
    except IllegalMoveError as exc:
        raise HTTPException(400, str(exc)) from exc

    node = Node(
        repertoire_id=repertoire_id,
        parent_id=parent.id,
        fen=result["fen"],
        move_san=result["san"],
        move_uci=result["uci"],
        comment=payload.comment,
        depth=parent.depth + 1,
    )
    db.add(node)
    db.commit()
    db.refresh(node)

    # Every learnable node (i.e. every node except root) gets a training
    # stats row immediately, with next_review_at defaulting to "now" --
    # this puts it straight into the due queue for the trainer.
    stats = TrainingStats(node_id=node.id)
    db.add(stats)
    db.commit()

    return node


@router.delete("/{repertoire_id}/nodes/{node_id}")
def delete_node(repertoire_id: int, node_id: int, db: Session = Depends(get_db)):
    node = db.get(Node, node_id)
    if not node or node.repertoire_id != repertoire_id:
        raise HTTPException(404, "Node not found")
    if node.parent_id is None:
        raise HTTPException(400, "Cannot delete the root node")

    db.delete(node)  # cascades to children via relationship config
    db.commit()
    return {"deleted": node_id}