from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import Settings
from app.schemas.document import DocumentTextRequest
from app.schemas.rag import AskRequest
from app.services.rag import RAGService


def load_json(path: Path) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON array in {path}")
    return data


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run local RAG eval with fixture documents.")
    parser.add_argument(
        "--documents",
        default="eval/fixtures/sample_documents.json",
        help="Path to the sample document fixture JSON.",
    )
    parser.add_argument(
        "--questions",
        default="eval/test_questions.json",
        help="Path to the test question JSON.",
    )
    parser.add_argument(
        "--golden-set",
        default="eval/golden_set.json",
        help="Path to the golden set JSON.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Default top_k used for evaluation requests.",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Optional path to save the eval result JSON.",
    )
    return parser


def ingest_documents(service: RAGService, documents: list[dict[str, object]]) -> None:
    for item in documents:
        service.ingest_text(
            DocumentTextRequest(
                title=str(item["title"]),
                source=str(item.get("source") or ""),
                tags=[str(tag) for tag in item.get("tags", [])],
                text=str(item["text"]),
            )
        )


def run_question_set(
    service: RAGService,
    questions: list[dict[str, object]],
    default_top_k: int,
) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for item in questions:
        response = service.ask(
            AskRequest(
                question=str(item["question"]),
                top_k=int(item.get("top_k", default_top_k)),
                return_debug=True,
            )
        )
        top_title = response.citations[0].title if response.citations else None
        best_score = response.debug.best_score if response.debug is not None else None
        result = {
            "question": item["question"],
            "status": response.status,
            "top_title": top_title,
            "best_score": best_score,
            "note": item.get("note"),
        }
        results.append(result)
    return results


def evaluate_golden_set(
    service: RAGService,
    golden_set: list[dict[str, object]],
    default_top_k: int,
) -> list[dict[str, object]]:
    evaluations: list[dict[str, object]] = []
    for item in golden_set:
        response = service.ask(
            AskRequest(
                question=str(item["question"]),
                top_k=int(item.get("top_k", default_top_k)),
                return_debug=True,
            )
        )
        expected_status = str(item["expected_status"])
        expected_titles = [str(title) for title in item.get("expected_titles", [])]
        observed_titles = [citation.title for citation in response.citations]
        matched_title = not expected_titles or any(
            title in observed_titles for title in expected_titles
        )
        passed = response.status == expected_status and matched_title
        evaluations.append(
            {
                "question": item["question"],
                "expected_status": expected_status,
                "observed_status": response.status,
                "expected_titles": expected_titles,
                "observed_titles": observed_titles,
                "best_score": response.debug.best_score if response.debug else None,
                "passed": passed,
                "note": item.get("note"),
            }
        )
    return evaluations


def print_question_results(results: list[dict[str, object]]) -> None:
    print("== Test Questions ==")
    for item in results:
        print(
            f"- {item['question']} | status={item['status']} | "
            f"top_title={item['top_title']} | best_score={item['best_score']}"
        )


def print_golden_summary(results: list[dict[str, object]]) -> None:
    passed_count = sum(1 for item in results if item["passed"])
    total = len(results)
    print("\n== Golden Set ==")
    for item in results:
        status = "PASS" if item["passed"] else "FAIL"
        print(
            f"- [{status}] {item['question']} | expected={item['expected_status']} | "
            f"observed={item['observed_status']} | expected_titles={item['expected_titles']} | "
            f"observed_titles={item['observed_titles']} | best_score={item['best_score']}"
        )
    print(f"\nSummary: {passed_count}/{total} passed")


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    documents = load_json(PROJECT_ROOT / args.documents)
    questions = load_json(PROJECT_ROOT / args.questions)
    golden_set = load_json(PROJECT_ROOT / args.golden_set)

    with TemporaryDirectory() as temp_dir:
        settings = Settings(
            app_name="RAG Knowledge Assistant Eval",
            qdrant_path=f"{temp_dir}/qdrant",
            openai_api_key=None,
            openai_base_url=None,
        )
        service = RAGService(settings)
        try:
            ingest_documents(service, documents)
            question_results = run_question_set(service, questions, args.top_k)
            golden_results = evaluate_golden_set(service, golden_set, args.top_k)
        finally:
            service.close()

    print_question_results(question_results)
    print_golden_summary(golden_results)
    if args.output:
        output_path = PROJECT_ROOT / args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as file:
            json.dump(
                {
                    "question_results": question_results,
                    "golden_results": golden_results,
                    "summary": {
                        "passed": sum(1 for item in golden_results if item["passed"]),
                        "total": len(golden_results),
                    },
                },
                file,
                ensure_ascii=False,
                indent=2,
            )
        print(f"\nSaved eval result to {output_path}")
    return 0 if all(item["passed"] for item in golden_results) else 1


if __name__ == "__main__":
    sys.exit(main())
