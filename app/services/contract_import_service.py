import json
import re
import tempfile
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from app.models.contract import Contract, ContractImportLog


FIELD_ALIASES = {
    "status": {"status", "situacao"},
    "numero_contrato": {"contrato", "numero", "numero_contrato", "n_contrato", "no_contrato"},
    "numero_aditivo": {"aditivo", "numero_aditivo", "n_aditivo"},
    "fornecedor": {"fornecedor", "contratada", "empresa"},
    "secretaria": {"secretaria", "unidade", "orgao"},
    "secretario": {"secretario", "secretaria_responsavel"},
    "gestor": {"gestor", "gestor_contrato"},
    "fiscal": {"fiscal", "fiscal_contrato"},
    "objeto": {"objeto", "descricao"},
    "vigencia_texto": {"vigencia", "periodo", "periodo_vigencia", "prazo"},
    "inicio_vigencia": {"inicio", "inicio_vigencia", "data_inicio"},
    "fim_vigencia": {
        "fim",
        "termino",
        "termino_da_vigencia",
        "fim_vigencia",
        "data_fim",
        "vencimento",
    },
    "data_os": {"data_os", "data_da_os", "ordem_servico", "data_ordem_servico"},
    "processo_administrativo": {"processo_administrativo", "processo_adm"},
    "processo_execucao": {"processo_execucao", "processo_exec"},
    "audesp_licitacao": {"audesp_licitacao", "audesp_lic"},
    "audesp_ajuste": {"audesp_ajuste", "ajuste_audesp"},
    "modalidade": {"modalidade", "modalidade_licitacao"},
    "valor_total": {"valor", "valor_total", "valor_contrato", "valor_total_contrato"},
    "data_assinatura": {"data_assinatura", "assinatura"},
    "data_publicacao": {"data_publicacao", "data_de_publicacao", "publicacao"},
    "observacao": {"observacao", "observacoes", "obs"},
}


@dataclass
class ImportContractResult:
    importados: int
    ignorados: int
    erros: int
    linhas_processadas: int
    linhas_com_erro: int
    detalhes_erro: list[dict[str, str | int]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "importados": self.importados,
            "ignorados": self.ignorados,
            "erros": self.erros,
            "linhas_processadas": self.linhas_processadas,
            "linhas_com_erro": self.linhas_com_erro,
            "detalhes_erro": self.detalhes_erro,
        }


def normalize_key(value: Any) -> str:
    text = str(value or "").replace("\n", " ").replace("\r", " ").strip().lower()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def clean_headers(headers: list[Any]) -> list[str]:
    seen: dict[str, int] = {}
    cleaned = []
    for header in headers:
        base = normalize_key(header) or "coluna"
        count = seen.get(base, 0)
        seen[base] = count + 1
        cleaned.append(base if count == 0 else f"{base}_{count + 1}")
    return cleaned


def parse_date(value: Any) -> date | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text or text.lower() in {"nan", "nat", "-"}:
        return None
    parsed = pd.to_datetime(text, dayfirst=True, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date()


def parse_money(value: Any) -> Decimal | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, int | float | Decimal):
        return Decimal(str(value)).quantize(Decimal("0.01"))
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None
    normalized = re.sub(r"[^\d,.-]", "", text)
    if "," in normalized:
        normalized = normalized.replace(".", "").replace(",", ".")
    try:
        return Decimal(normalized).quantize(Decimal("0.01"))
    except InvalidOperation:
        return None


def extract_cpf(value: Any) -> tuple[str | None, str | None]:
    text = str(value or "").strip()
    match = re.search(r"\bCPF\b.*?([\d.\-]{11,14})", text, flags=re.IGNORECASE)
    if not match:
        return (text or None), None
    cpf = re.sub(r"\D", "", match.group(1))
    nome = text[: match.start()].strip(" -:")
    return (nome or None), cpf or None


def extract_cnpj(value: Any) -> tuple[str | None, str | None]:
    text = str(value or "").strip()
    match = re.search(r"\bCNPJ\b.*?([\d./-]{14,18})", text, flags=re.IGNORECASE)
    if not match:
        digits = re.sub(r"\D", "", text)
        return (text or None), digits if len(digits) == 14 else None
    cnpj = re.sub(r"\D", "", match.group(1))
    nome = text[: match.start()].strip(" -:")
    return (nome or None), cnpj or None


def parse_period(value: Any) -> tuple[date | None, date | None]:
    text = str(value or "").strip()
    dates = re.findall(r"\d{1,2}/\d{1,2}/\d{2,4}", text)
    if len(dates) < 2:
        return None, None
    return parse_date(dates[0]), parse_date(dates[1])


def calculate_days_to_expiration(end_date: date | None, today: date | None = None) -> int | None:
    if end_date is None:
        return None
    return (end_date - (today or date.today())).days


def _read_spreadsheet(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix not in {".xls", ".xlsx"}:
        raise ValueError("Arquivo deve ser .xls ou .xlsx")
    engine = "xlrd" if suffix == ".xls" else "openpyxl"
    raw = pd.read_excel(path, engine=engine, dtype=object, header=None)
    header_index = _detect_header_row(raw)
    headers = clean_headers(list(raw.iloc[header_index]))
    frame = raw.iloc[header_index + 1 :].copy()
    frame.columns = headers
    return frame.reset_index(drop=True)


def _detect_header_row(frame: pd.DataFrame) -> int:
    required = {"contrato", "fornecedor", "objeto"}
    best_index = 0
    best_score = -1
    for index in range(min(20, len(frame))):
        keys = set(clean_headers(list(frame.iloc[index])))
        score = len(required & keys)
        if score > best_score:
            best_score = score
            best_index = index
        if required <= keys:
            return index
    return best_index


def _canonical_row(row: dict[str, Any]) -> dict[str, Any]:
    canonical: dict[str, Any] = {}
    for field, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            if alias in row and not _is_empty(row[alias]):
                canonical[field] = row[alias]
                break
    return canonical


def _is_empty(value: Any) -> bool:
    return value is None or (isinstance(value, float) and pd.isna(value)) or not str(value).strip()


def _is_section_title(row: dict[str, Any]) -> bool:
    values = [str(value).strip() for value in row.values() if not _is_empty(value)]
    if not values:
        return True
    joined = " ".join(values).upper()
    if "CONTRATOS COM VENCIMENTO" in joined:
        return True
    return len(values) == 1 and not re.search(r"\d", values[0])


def _payload_from_row(row: dict[str, Any]) -> dict[str, Any] | None:
    if _is_section_title(row):
        return None
    data = _canonical_row(row)
    fornecedor, cnpj = extract_cnpj(data.get("fornecedor"))
    secretario, secretario_cpf = extract_cpf(data.get("secretario"))
    gestor, gestor_cpf = extract_cpf(data.get("gestor"))
    fiscal, fiscal_cpf = extract_cpf(data.get("fiscal"))
    inicio_periodo, fim_periodo = parse_period(data.get("vigencia_texto"))
    inicio = parse_date(data.get("inicio_vigencia")) or inicio_periodo
    fim = parse_date(data.get("fim_vigencia")) or fim_periodo

    payload = {
        "status": str(data.get("status") or "ativo").strip()[:50],
        "numero_contrato": _clean_text(data.get("numero_contrato"), 50),
        "numero_aditivo": _clean_text(data.get("numero_aditivo"), 50),
        "fornecedor": fornecedor,
        "cnpj": cnpj,
        "secretaria": _clean_text(data.get("secretaria"), 120),
        "secretario": secretario,
        "gestor": gestor,
        "gestor_cpf": gestor_cpf,
        "fiscal": fiscal,
        "fiscal_cpf": fiscal_cpf,
        "objeto": _clean_text(data.get("objeto")),
        "vigencia_texto": _clean_text(data.get("vigencia_texto")),
        "inicio_vigencia": inicio,
        "fim_vigencia": fim,
        "data_os": parse_date(data.get("data_os")),
        "processo_administrativo": _clean_text(data.get("processo_administrativo"), 80),
        "processo_execucao": _clean_text(data.get("processo_execucao"), 80),
        "audesp_licitacao": _clean_text(data.get("audesp_licitacao"), 80),
        "audesp_ajuste": _clean_text(data.get("audesp_ajuste")),
        "modalidade": _clean_text(data.get("modalidade"), 100),
        "valor_total": parse_money(data.get("valor_total")),
        "data_assinatura": parse_date(data.get("data_assinatura")),
        "data_publicacao": parse_date(data.get("data_publicacao")),
        "observacao": _clean_text(data.get("observacao")),
        "dias_para_vencimento": calculate_days_to_expiration(fim),
    }
    if secretario_cpf and not payload["observacao"]:
        payload["observacao"] = f"CPF secretario: {secretario_cpf}"
    if not any(payload.get(key) for key in ("numero_contrato", "fornecedor", "objeto", "fim_vigencia")):
        return None
    return payload


def _clean_text(value: Any, max_length: int | None = None) -> str | None:
    if _is_empty(value):
        return None
    text = re.sub(r"\s+", " ", str(value).strip())
    return text[:max_length] if max_length else text


def import_contracts(
    file_path: str | Path,
    db: Session | None = None,
    *,
    usuario: str | None = None,
) -> dict[str, Any]:
    path = Path(file_path)
    frame = _read_spreadsheet(path)
    result = ImportContractResult(0, 0, 0, 0, 0, [])
    created: list[Contract] = []

    for index, raw_row in frame.iterrows():
        result.linhas_processadas += 1
        try:
            payload = _payload_from_row(raw_row.to_dict())
            if payload is None:
                result.ignorados += 1
                continue
            contract = Contract(**payload)
            if db is not None:
                db.add(contract)
            created.append(contract)
            result.importados += 1
        except Exception as exc:
            result.erros += 1
            result.linhas_com_erro += 1
            result.detalhes_erro.append({"linha": int(index) + 2, "erro": str(exc)})

    if db is not None:
        db.add(
            ContractImportLog(
                arquivo=path.name,
                usuario=usuario,
                linhas_processadas=result.linhas_processadas,
                linhas_importadas=result.importados,
                linhas_com_erro=result.linhas_com_erro,
                detalhes_erro=json.dumps(result.detalhes_erro, ensure_ascii=False),
            )
        )
        db.commit()

    payload = result.as_dict()
    payload["contracts"] = created
    return payload


async def persist_upload(filename: str, content: bytes) -> Path:
    suffix = Path(filename).suffix.lower()
    if suffix not in {".xls", ".xlsx"}:
        raise ValueError("Arquivo deve ser .xls ou .xlsx")
    safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", Path(filename).name)
    path = Path(tempfile.gettempdir()) / f"fiscalbot_{datetime.utcnow():%Y%m%d%H%M%S%f}_{safe_name}"
    path.write_bytes(content)
    return path
