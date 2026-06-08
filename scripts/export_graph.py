"""Export the compiled workflow as a Mermaid diagram and a PNG.

Run after changing the graph topology to refresh the architecture diagram:

    python scripts/export_graph.py
"""

from pathlib import Path

from support_agent.logger import get_logger
from support_agent.workflow.graph import get_workflow

logger = get_logger("scripts.export_graph")

DOCS_DIR = Path(__file__).resolve().parents[1] / "docs"


def main() -> None:
    DOCS_DIR.mkdir(exist_ok=True)
    graph = get_workflow().get_graph()

    mermaid_path = DOCS_DIR / "architecture.mmd"
    mermaid_path.write_text(graph.draw_mermaid(), encoding="utf-8")
    logger.info("wrote %s", mermaid_path)

    try:
        png_path = DOCS_DIR / "architecture.png"
        png_path.write_bytes(graph.draw_mermaid_png())
        logger.info("wrote %s", png_path)
    except Exception as exc:  # rendering via mermaid.ink needs network
        logger.warning("PNG render skipped: %s", exc)


if __name__ == "__main__":
    main()
