import csv
from collections.abc import Iterable
from io import BytesIO, StringIO
from math import ceil
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.contract import Contract
from app.models.user import User, UserRole
from app.schemas.contract import (
    ContractDashboard,
    ContractPage,
    ContractRead,
    ContractUpdate,
)
from app.services.contract_import_service import import_contracts, persist_upload

router = APIRouter()

EXPORT_COLUMNS = [
    ("numero_contrato", "Contrato"),
    ("fornecedor", "Fornecedor"),
    ("cnpj", "CNPJ"),
    ("secretaria", "Secretaria"),
    ("fiscal", "Fiscal"),
    ("fim_vigencia", "Vencimento"),
    ("dias_para_vencimento", "Dias restantes"),
    ("status", "Status"),
    ("valor_total", "Valor total"),
]


def _serialize(items: Iterable[Contract]) -> list[ContractRead]:
    return [ContractRead.model_validate(item) for item in items]


def _get_contract(db: Session, contract_id: UUID) -> Contract:
    contract = db.get(Contract, contract_id)
    if contract is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrato nao encontrado")
    return contract


def _filtered_stmt(
    *,
    vencendo_em_30: bool = False,
    secretaria: str | None = None,
    status_filter: str | None = None,
    fornecedor: str | None = None,
):
    stmt = select(Contract)
    conditions = []
    if vencendo_em_30:
        conditions.extend([Contract.dias_para_vencimento >= 0, Contract.dias_para_vencimento <= 30])
    if secretaria:
        conditions.append(Contract.secretaria.ilike(f"%{secretaria}%"))
    if status_filter:
        conditions.append(Contract.status == status_filter)
    if fornecedor:
        term = f"%{fornecedor}%"
        conditions.append(or_(Contract.fornecedor.ilike(term), Contract.cnpj.ilike(term)))
    if conditions:
        stmt = stmt.where(*conditions)
    return stmt


def _contract_export_rows(contracts: Iterable[Contract]) -> list[list[str]]:
    rows = []
    for contract in contracts:
        row = []
        for field, _label in EXPORT_COLUMNS:
            value = getattr(contract, field)
            row.append("" if value is None else str(value))
        rows.append(row)
    return rows


@router.post("/import", status_code=status.HTTP_201_CREATED)
async def import_contracts_endpoint(
    current_user: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.gestor))],
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
) -> dict:
    try:
        path = await persist_upload(file.filename or "contratos.xlsx", await file.read())
        result = import_contracts(path, db, usuario=current_user.email)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    result.pop("contracts", None)
    return result


@router.get("/dashboard", response_model=ContractDashboard)
def contracts_dashboard(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> ContractDashboard:
    vencendo_30 = select(func.count(Contract.id)).where(
        Contract.dias_para_vencimento >= 0,
        Contract.dias_para_vencimento <= 30,
    )
    vencendo_15 = select(func.count(Contract.id)).where(
        Contract.dias_para_vencimento >= 0,
        Contract.dias_para_vencimento <= 15,
    )
    vencidos = select(func.count(Contract.id)).where(Contract.dias_para_vencimento < 0)
    ativos = select(func.count(Contract.id)).where(Contract.status == "ativo")
    valor = select(func.coalesce(func.sum(Contract.valor_total), 0))
    return ContractDashboard(
        contratos_ativos=int(db.scalar(ativos) or 0),
        vencendo_em_30=int(db.scalar(vencendo_30) or 0),
        vencendo_em_15=int(db.scalar(vencendo_15) or 0),
        vencidos=int(db.scalar(vencidos) or 0),
        valor_total_contratado=db.scalar(valor) or 0,
    )


@router.get("/export/csv")
def export_contracts_csv(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    vencendo_em_30: bool = False,
    secretaria: Annotated[str | None, Query(max_length=120)] = None,
    status_filter: Annotated[str | None, Query(alias="status", max_length=50)] = None,
    fornecedor: Annotated[str | None, Query(max_length=160)] = None,
) -> StreamingResponse:
    contracts = db.scalars(
        _filtered_stmt(
            vencendo_em_30=vencendo_em_30,
            secretaria=secretaria,
            status_filter=status_filter,
            fornecedor=fornecedor,
        ).order_by(Contract.fim_vigencia.asc().nulls_last())
    )
    buffer = StringIO()
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow([label for _field, label in EXPORT_COLUMNS])
    writer.writerows(_contract_export_rows(contracts))
    content = buffer.getvalue().encode("utf-8-sig")
    return StreamingResponse(
        BytesIO(content),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="contratos.csv"'},
    )


@router.get("/export/xlsx")
def export_contracts_xlsx(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    vencendo_em_30: bool = False,
    secretaria: Annotated[str | None, Query(max_length=120)] = None,
    status_filter: Annotated[str | None, Query(alias="status", max_length=50)] = None,
    fornecedor: Annotated[str | None, Query(max_length=160)] = None,
) -> StreamingResponse:
    contracts = db.scalars(
        _filtered_stmt(
            vencendo_em_30=vencendo_em_30,
            secretaria=secretaria,
            status_filter=status_filter,
            fornecedor=fornecedor,
        ).order_by(Contract.fim_vigencia.asc().nulls_last())
    )
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Contratos"
    sheet.append([label for _field, label in EXPORT_COLUMNS])
    for row in _contract_export_rows(contracts):
        sheet.append(row)
    for column_cells in sheet.columns:
        max_length = max(len(str(cell.value or "")) for cell in column_cells)
        sheet.column_dimensions[column_cells[0].column_letter].width = min(max(max_length + 2, 12), 45)
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="contratos.xlsx"'},
    )


@router.get("/export/pdf")
def export_contracts_pdf(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    vencendo_em_30: bool = False,
    secretaria: Annotated[str | None, Query(max_length=120)] = None,
    status_filter: Annotated[str | None, Query(alias="status", max_length=50)] = None,
    fornecedor: Annotated[str | None, Query(max_length=160)] = None,
) -> StreamingResponse:
    contracts = list(
        db.scalars(
            _filtered_stmt(
                vencendo_em_30=vencendo_em_30,
                secretaria=secretaria,
                status_filter=status_filter,
                fornecedor=fornecedor,
            )
            .order_by(Contract.fim_vigencia.asc().nulls_last())
            .limit(500)
        )
    )
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), title="Relatorio de Contratos")
    styles = getSampleStyleSheet()
    story = [Paragraph("Relatorio de Contratos", styles["Title"])]
    table_data = [[label for _field, label in EXPORT_COLUMNS[:8]]]
    table_data.extend([row[:8] for row in _contract_export_rows(contracts)[:500]])
    table = Table(table_data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F766E")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ]
        )
    )
    story.append(table)
    doc.build(story)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="contratos.pdf"'},
    )


@router.get("", response_model=ContractPage)
def list_contracts(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    vencendo_em_30: bool = False,
    secretaria: Annotated[str | None, Query(max_length=120)] = None,
    status_filter: Annotated[str | None, Query(alias="status", max_length=50)] = None,
    fornecedor: Annotated[str | None, Query(max_length=160)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ContractPage:
    stmt = _filtered_stmt(
        vencendo_em_30=vencendo_em_30,
        secretaria=secretaria,
        status_filter=status_filter,
        fornecedor=fornecedor,
    )
    count_stmt = stmt.with_only_columns(func.count(Contract.id)).order_by(None)
    total = int(db.scalar(count_stmt) or 0)
    items = db.scalars(
        stmt.order_by(Contract.fim_vigencia.asc().nulls_last())
        .limit(limit)
        .offset((page - 1) * limit)
    )
    return ContractPage(
        items=_serialize(items),
        total=total,
        page=page,
        limit=limit,
        pages=max(1, ceil(total / limit)) if total else 1,
    )


@router.get("/{contract_id}", response_model=ContractRead)
def get_contract(
    contract_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> ContractRead:
    return ContractRead.model_validate(_get_contract(db, contract_id))


@router.put("/{contract_id}", response_model=ContractRead)
def update_contract(
    contract_id: UUID,
    payload: ContractUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.gestor))],
) -> ContractRead:
    contract = _get_contract(db, contract_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(contract, field, value)
    if payload.fim_vigencia is not None:
        from app.services.contract_import_service import calculate_days_to_expiration

        contract.dias_para_vencimento = calculate_days_to_expiration(payload.fim_vigencia)
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return ContractRead.model_validate(contract)


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract(
    contract_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.admin))],
) -> None:
    contract = _get_contract(db, contract_id)
    db.delete(contract)
    db.commit()
