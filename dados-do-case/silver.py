import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

RAW_PATH = Path(__file__).parent / "leads_raw.json"
BRONZE_PATH = Path(__file__).parent / "bronze" / "leads_bronze.json"
SILVER_DIR = Path(__file__).parent / "silver"
SILVER_PATH = SILVER_DIR / "leads_clean.json"

GEMINI_MODEL = "gemini-3.6-flash"
SEGMENT_PROMPT = """Classifique a intenção de compra do lead a partir da mensagem abaixo em exatamente uma palavra: hot, warm ou cold.
- hot = quer comprar / urgente
- warm = comparando fornecedores / decisão futura
- cold = só pesquisando, sem intenção de compra próxima

Mensagem: "{message}"

Responda apenas com a palavra (hot, warm ou cold), sem explicação, sem pontuação."""

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

HOT_KEYWORDS = ["contratar", "comprar", "assinar", "fechar", "urgente", "urgência", "agora", "hoje", "demo"]
WARM_KEYWORDS = ["comparando", "decisão", "decidir", "mês que vem", "avaliando", "orçamento", "preço", "preco"]
COLD_KEYWORDS = ["só ", "pesquisando", "sem pressa", "faculdade", "curiosidade", "apenas"]

DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y", "%b %d, %Y"]


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def normalize_email(value):
    if not value:
        return None
    cleaned = value.strip().lower()
    if not EMAIL_RE.match(cleaned):
        return None
    return cleaned


def normalize_name(row):
    raw = row.get("name") or row.get("nome")
    if not raw or not raw.strip():
        return None
    return " ".join(raw.strip().split()).title()


def normalize_phone(value):
    if not value:
        return None
    digits = re.sub(r"\D", "", value)
    if digits.startswith("55") and len(digits) in (12, 13):
        core = digits
    elif len(digits) in (10, 11):
        core = "55" + digits
    else:
        return None
    return "+" + core


def normalize_company(value):
    if not value or not value.strip():
        return None
    return value.strip()


def normalize_source(value):
    if not value or not value.strip():
        return None
    return value.strip()


def normalize_created_at(value):
    if not value:
        return None
    raw = value.strip()
    if re.fullmatch(r"\d{9,10}", raw):
        try:
            return datetime.fromtimestamp(int(raw), tz=timezone.utc).date().isoformat()
        except (OverflowError, OSError, ValueError):
            return None
    if "T" in raw:
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00")).date().isoformat()
        except ValueError:
            pass
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def classify_segment_rules(message):
    if not message or not message.strip():
        return "unknown"
    text = message.lower()
    if any(k in text for k in HOT_KEYWORDS):
        return "hot"
    if any(k in text for k in WARM_KEYWORDS):
        return "warm"
    if any(k in text for k in COLD_KEYWORDS):
        return "cold"
    return "unknown"


def make_ai_classifier():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[aviso] GEMINI_API_KEY ausente — usando classificador por regras.")
        return classify_segment_rules

    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_MODEL)

    def classify_segment_ai(message):
        if not message or not message.strip():
            return "unknown"
        try:
            response = model.generate_content(SEGMENT_PROMPT.format(message=message.strip()))
            label = response.text.strip().lower()
            if label in ("hot", "warm", "cold"):
                return label
            return classify_segment_rules(message)
        except Exception as exc:
            print(f"[aviso] chamada Gemini falhou ({exc}) — usando regras pra essa mensagem.")
            return classify_segment_rules(message)

    return classify_segment_ai


def normalize_row(row):
    return {
        "_row_id": row["_row_id"],
        "email": normalize_email(row.get("email")),
        "email_raw": row.get("email"),
        "name": normalize_name(row),
        "phone": normalize_phone(row.get("phone")),
        "company": normalize_company(row.get("company")),
        "source": normalize_source(row.get("source")),
        "created_at": normalize_created_at(row.get("created_at")),
        "message": row.get("message"),
    }


def split_valid_rejected(bronze_rows, raw_records):
    valid, rejected = [], []
    for row in bronze_rows:
        norm = normalize_row(row)
        if norm["email"]:
            valid.append(norm)
        else:
            reason = "email ausente" if not row.get("email") else f"email inválido: {row.get('email').strip()}"
            rejected.append({"reason": reason, "raw": raw_records[row["_row_id"]]})
    return valid, rejected


def group_by_email(valid_rows):
    groups = {}
    for row in valid_rows:
        groups.setdefault(row["email"], []).append(row)
    return groups


def merge_group(rows):
    ordered = sorted(rows, key=lambda r: (r["created_at"] or "", r["_row_id"]))
    merged = {}
    for row in ordered:
        for key in ("name", "phone", "company", "source", "created_at", "message"):
            value = row.get(key)
            if value:
                merged[key] = value
    return merged


def build_leads(groups, classify_fn):
    leads = []
    duplicates_removed = 0
    for email, rows in groups.items():
        if len(rows) > 1:
            duplicates_removed += len(rows) - 1
        merged = merge_group(rows)
        leads.append({
            "email": email,
            "name": merged.get("name"),
            "phone": merged.get("phone"),
            "company": merged.get("company"),
            "source": merged.get("source"),
            "created_at": merged.get("created_at"),
            "segment": classify_fn(merged.get("message")),
        })
    return leads, duplicates_removed


def validate_output(bronze_rows, valid_rows, rejected_rows, leads, duplicates_removed):
    received = len(bronze_rows)
    assert received == len(valid_rows) + len(rejected_rows), "received != valid + rejected"
    assert len(leads) == len(valid_rows) - duplicates_removed, "leads != valid - duplicates_removed"
    emails = [lead["email"] for lead in leads]
    assert len(emails) == len(set(emails)), "email duplicado sobrou no output final"
    allowed_segments = {"hot", "warm", "cold", "unknown"}
    expected_keys = {"email", "name", "phone", "company", "source", "created_at", "segment"}
    for lead in leads:
        assert set(lead.keys()) == expected_keys, f"schema de lead incorreto: {lead.keys()}"
        assert lead["segment"] in allowed_segments, f"segment inválido: {lead['segment']}"
    for rej in rejected_rows:
        assert set(rej.keys()) == {"reason", "raw"}, "schema de rejected incorreto"


def validate_against_case_schema(output):
    """Confere o output final contra o contrato literal do case.md (tipos, chaves, valores)."""
    assert set(output.keys()) == {"leads", "rejected", "summary"}, "top-level deve ter exatamente leads/rejected/summary"

    lead_keys = {"email", "name", "phone", "company", "source", "created_at", "segment"}
    nullable_str_fields = ("name", "phone", "company", "source", "created_at")
    date_re = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    seen_emails = set()
    for lead in output["leads"]:
        assert set(lead.keys()) == lead_keys, f"lead com chaves erradas: {lead.keys()}"
        assert isinstance(lead["email"], str) and lead["email"], "email deve ser string não-vazia"
        assert lead["email"] == lead["email"].strip().lower(), "email deve estar minúsculo e sem espaços"
        assert EMAIL_RE.match(lead["email"]), f"email não parece válido: {lead['email']}"
        assert lead["email"] not in seen_emails, f"email duplicado no output: {lead['email']}"
        seen_emails.add(lead["email"])
        for field in nullable_str_fields:
            assert lead[field] is None or isinstance(lead[field], str), f"{field} deve ser string ou null"
        if lead["created_at"] is not None:
            assert date_re.match(lead["created_at"]), f"created_at fora do formato ISO: {lead['created_at']}"
        assert lead["segment"] in {"hot", "warm", "cold", "unknown"}, f"segment inválido: {lead['segment']}"

    for rej in output["rejected"]:
        assert set(rej.keys()) == {"reason", "raw"}, f"rejected com chaves erradas: {rej.keys()}"
        assert isinstance(rej["reason"], str) and rej["reason"], "reason deve ser string não-vazia"
        assert isinstance(rej["raw"], dict), "raw deve ser objeto"

    summary_keys = {"received", "valid", "duplicates_removed", "rejected"}
    assert set(output["summary"].keys()) == summary_keys, "summary com chaves erradas"
    for key in summary_keys:
        assert isinstance(output["summary"][key], int), f"summary.{key} deve ser inteiro"


if __name__ == "__main__":
    bronze_rows = load_json(BRONZE_PATH)
    raw_records = load_json(RAW_PATH)
    valid_rows, rejected_rows = split_valid_rejected(bronze_rows, raw_records)
    groups = group_by_email(valid_rows)
    classify_fn = make_ai_classifier()
    leads, duplicates_removed = build_leads(groups, classify_fn)

    validate_output(bronze_rows, valid_rows, rejected_rows, leads, duplicates_removed)

    output = {
        "leads": leads,
        "rejected": rejected_rows,
        "summary": {
            "received": len(bronze_rows),
            "valid": len(valid_rows),
            "duplicates_removed": duplicates_removed,
            "rejected": len(rejected_rows),
        },
    }

    SILVER_DIR.mkdir(exist_ok=True)
    with open(SILVER_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    written = load_json(SILVER_PATH)
    validate_against_case_schema(written)
    print("schema check: OK — leads_clean.json bate com o contrato do case.md")

    print(json.dumps(output["summary"], ensure_ascii=False, indent=2))
    print(json.dumps(output["leads"], ensure_ascii=False, indent=2))
