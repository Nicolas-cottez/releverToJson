import argparse
import json
import sys
from pathlib import Path
import fitz


def extract_words(pdf_path):
    # ouverture
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Erreur ouverture PDF : {e}", file=sys.stderr)
        sys.exit(1)

    pages = []
    total = 0
    empty_pages = 0

    # page par page
    for i in range(len(doc)):
        page = doc[i]
        words_raw = page.get_text("words")

        words = [{
            "text": w[4],
            "x0": round(w[0], 2),
            "y0": round(w[1], 2),
            "x1": round(w[2], 2),
            "y1": round(w[3], 2)
        } for w in words_raw]

        total += len(words)
        if len(words) == 0:
            empty_pages += 1

        pages.append({
            "page": i + 1,
            "width": round(page.rect.width, 2),
            "height": round(page.rect.height, 2),
            "words": words
        })

    doc.close()

    scanned = total < 20 or empty_pages >= 2

    return {
        "pdf_path": str(pdf_path),
        "pages": pages,
        "diagnostics": {
            "is_scanned": scanned,
            "total_words": total
        }
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True)
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"Fichier non trouvé : {pdf_path}", file=sys.stderr)
        sys.exit(1)

    result = extract_words(pdf_path)

    # STOP si PDF scanné
    if result["diagnostics"]["is_scanned"]:
        print("PDF non exploitable : aucun texte détecté (document scanné ou image).", file=sys.stderr)
        sys.exit(2)

    out_dir = Path("json/raw")
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / f"{pdf_path.stem}.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"{result['diagnostics']['total_words']} mots extraits → {out_path}")


if __name__ == "__main__":
    main()
