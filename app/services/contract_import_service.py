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
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.models.contract import Contract, ContractImportLog

FIELD_ALIASES = {
    "tipo": {"tipo", "tipo_instrumento", "tipo_registro"},
    "status": {"status", "situacao"},
    "numero_contrato": {
        "contrato",
        "numero",
        "numero_contrato",
        "n_contrato",
        "no_contrato",
        "ata",
        "numero_ata",
    },
    "numero_aditivo": {"aditivo", "numero_aditivo", "n_aditivo"},
    "fornecedor": {"fornecedor", "contratada", "empresa", "detentor"},
    "cnpj": {"cnpj", "cnpj_fornecedor"},
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
    "valor_total": {
        "valor",
        "valor_total",
        "valor_contrato",
        "valor_total_contrato",
        "valor_total_ata",
    },
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

    atualizados: int = 0
    duplicados: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "importados": self.importados,
            "atualizados": self.atualizados,
            "duplicados": self.duplicados,
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
    return parse_date(dates[-2]), parse_date(dates[-1])


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
    if raw.empty:
        raise ValueError("A planilha esta vazia")
    header_index = _detect_header_row(raw)
    headers = clean_headers(list(raw.iloc[header_index]))
    frame = raw.iloc[header_index + 1 :].copy()
    frame.columns = headers
    frame = frame.reset_index(drop=True)
    frame.attrs["header_index"] = header_index
    return frame


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
    if "ata" in row and not _is_empty(row.get("ata")):
        data.setdefault("tipo", "ata")
    inferred_type = (
        "ata" if re.match(r"^ata\b", str(data.get("numero_contrato") or ""), re.I) else "contrato"
    )
    kind = normalize_key(data.get("tipo")) or inferred_type
    if kind not in {"contrato", "ata"}:
        raise ValueError("Tipo deve ser contrato ou ata")
    fornecedor, cnpj = extract_cnpj(data.get("fornecedor"))
    if not _is_empty(data.get("cnpj")):
        digits = re.sub(r"\D", "", str(data["cnpj"]))
        if len(digits) != 14:
            raise ValueError("CNPJ deve conter 14 digitos; use a celula como texto")
        cnpj = digits
    secretario, secretario_cpf = extract_cpf(data.get("secretario"))
    gestor, gestor_cpf = extract_cpf(data.get("gestor"))
    fiscal, fiscal_cpf = extract_cpf(data.get("fiscal"))
    inicio_periodo, fim_periodo = parse_period(data.get("vigencia_texto"))
    inicio = parse_date(data.get("inicio_vigencia")) or inicio_periodo
    fim = parse_date(data.get("fim_vigencia")) or fim_periodo

    payload = {
        "tipo": kind,
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
    if payload["valor_total"] is not None and payload["valor_total"] < 0:
        raise ValueError("Valor nao pode ser negativo")
    if not _is_empty(data.get("valor_total")) and payload["valor_total"] is None:
        raise ValueError("Valor nao reconhecido; corrija a celula antes de importar")
    for field in (
        "inicio_vigencia",
        "fim_vigencia",
        "data_os",
        "data_assinatura",
        "data_publicacao",
    ):
        if not _is_empty(data.get(field)) and parse_date(data[field]) is None:
            raise ValueError(f"Data nao reconhecida em {field}")
    if inicio and fim and fim < inicio:
        raise ValueError("Vencimento anterior ao inicio da vigencia")
    if secretario_cpf and not payload["observacao"]:
        payload["observacao"] = f"CPF secretario: {secretario_cpf}"
    if not any(
        payload.get(key) for key in ("numero_contrato", "fornecedor", "objeto", "fim_vigencia")
    ):
        return None
    return payload


def _clean_text(value: Any, max_length: int | None = None) -> str | None:
    if _is_empty(value):
        return None
    text = re.sub(r"\s+", " ", str(value).strip())
    return text[:max_length] if max_length else text


def contract_identity(record) -> tuple | None:
    """Conservative match: type, number, supplier, department and amendment."""
    get = record.get if isinstance(record, dict) else lambda name: getattr(record, name, None)
    number = re.sub(r"^ata\s+", "", str(get("numero_contrato") or ""), flags=re.I)
    supplier = re.sub(r"\D", "", get("cnpj") or "") or get("fornecedor")
    if not number.strip() or not supplier:
        return None
    amendment = normalize_key(get("numero_aditivo"))
    if amendment in {"contrato", "ata"}:
        amendment = ""
    return (
        get("tipo") or "contrato",
        normalize_key(number),
        normalize_key(supplier),
        normalize_key(get("secretaria")),
        amendment,
    )


def import_contracts(
    file_path: str | Path,
    db: Session | None = None,
    *,
    usuario: str | None = None,
    modo: str = "ignorar",
    preview: bool = False,
) -> dict[str, Any]:
    if modo not in {"ignorar", "atualizar"}:
        raise ValueError("Modo deve ser ignorar ou atualizar")
    path = Path(file_path)
    frame = _read_spreadsheet(path)
    result = ImportContractResult(0, 0, 0, 0, 0, [])
    created: list[Contract] = []
    sample = []
    # Serialize competing imports in PostgreSQL without changing existing rows.
    if db is not None and not preview and db.get_bind().dialect.name == "postgresql":
        db.execute(text("SELECT pg_advisory_xact_lock(71420261027)"))
    known: dict[tuple, list] = {}
    if db is not None:
        for existing in db.scalars(select(Contract)):
            key = contract_identity(existing)
            if key:
                known.setdefault(key, []).append(existing)
    seen = set()
    for index, raw_row in frame.iterrows():
        result.linhas_processadas += 1
        line = int(index) + int(frame.attrs.get("header_index", 0)) + 2
        try:
            payload = _payload_from_row(raw_row.to_dict())
            if payload is None:
                result.ignorados += 1
                continue
            key = contract_identity(payload)
            if key is None:
                raise ValueError(
                    "Informe numero e fornecedor para identificar o registro com seguranca"
                )
            matches = known.get(key, [])
            # Enrich a previously simplified import without creating a second instrument.
            # Never replace a known amendment, or choose between ambiguous existing rows.
            if not matches and modo == "atualizar" and key[-1]:
                matches = [
                    candidate
                    for candidate in known.get((*key[:-1], ""), [])
                    if contract_identity(candidate)[-1] == ""
                ]
            action = "novo"
            if key in seen:
                result.duplicados += 1
                result.ignorados += 1
                action = "repetido_na_planilha"
            elif matches:
                result.duplicados += 1
                if modo == "atualizar" and len(matches) == 1:
                    action = "atualizar"
                    result.atualizados += 1
                    if not preview:
                        existing = matches[0]
                        if (
                            payload["fim_vigencia"]
                            and payload["fim_vigencia"] != existing.fim_vigencia
                        ):
                            for flag in ("alerta_30", "alerta_15", "alerta_07", "alerta_01"):
                                setattr(existing, flag, False)
                        for field, value in payload.items():
                            # Blank cells never erase existing values or administrative status.
                            if value is not None and field != "status":
                                setattr(existing, field, value)
                        known[key] = [existing]
                else:
                    action = "duplicado_ambiguo" if len(matches) > 1 else "ignorar_existente"
                    result.ignorados += 1
            else:
                result.importados += 1
                if not preview:
                    contract = Contract(**payload)
                    if db is not None:
                        db.add(contract)
                    created.append(contract)
            seen.add(key)
            if len(sample) < 50:
                sample.append(
                    {
                        "linha": line,
                        "acao": action,
                        "tipo": payload["tipo"],
                        "numero": payload["numero_contrato"],
                        "fornecedor": payload["fornecedor"],
                        "vencimento": payload["fim_vigencia"],
                        "valor": payload["valor_total"],
                    }
                )
        except ValueError as exc:
            result.erros += 1
            result.linhas_com_erro += 1
            result.detalhes_erro.append({"linha": line, "erro": str(exc)})
    if db is not None and not preview:
        db.add(
            ContractImportLog(
                arquivo=path.name,
                usuario=usuario,
                linhas_processadas=result.linhas_processadas,
                linhas_importadas=result.importados,
                linhas_com_erro=result.linhas_com_erro,
                detalhes_erro=json.dumps(
                    {
                        "erros": result.detalhes_erro,
                        "atualizados": result.atualizados,
                        "duplicados": result.duplicados,
                        "modo": modo,
                    },
                    ensure_ascii=False,
                ),
            )
        )
        db.commit()
    response = result.as_dict()
    response["contracts"] = created
    response["previa"] = sample
    response["simulacao"] = preview
    return response


async def persist_upload(filename: str, content: bytes) -> Path:
    suffix = Path(filename).suffix.lower()
    if suffix not in {".xls", ".xlsx"}:
        raise ValueError("Arquivo deve ser .xls ou .xlsx")
    safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", Path(filename).name)
    path = Path(tempfile.gettempdir()) / f"fiscalbot_{datetime.utcnow():%Y%m%d%H%M%S%f}_{safe_name}"
    path.write_bytes(content)
    return path
