"""Admin panel routes for uploaded documents (.md, .pdf, .docx) and who may read them.

Admin and super admin only (``knowledge_manage.admin_roles``), checked here from the verified identity.
The gateway exposes them under ``/chatbot/v1/knowledge/manage/``.
"""

from __future__ import annotations

import asyncio
from typing import Optional
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile
from pydantic import BaseModel, Field

from app.config.settings import get_settings
from app.knowledge import manage
from app.services.auth import CallerScope, require_knowledge_admin

router = APIRouter(prefix="/knowledge/manage", tags=["knowledge-manage"])


class AccessUpdate(BaseModel):
    # ["all"] or tenant names.
    tenants: list[str] = Field(min_length=1)
    exclude_tenants: list[str] = Field(default_factory=list)
    # None keeps the current roles; [] opens the document to every role.
    roles: Optional[list[str]] = None


def _http(e: manage.ManageError) -> HTTPException:
    return HTTPException(status_code=e.status, detail=e.message)


@router.get("/documents")
async def list_documents(_: CallerScope = Depends(require_knowledge_admin)) -> dict:
    try:
        return {"documents": await asyncio.to_thread(manage.list_documents)}
    except manage.ManageError as e:
        raise _http(e) from e


@router.post("/documents")
async def upload_document(
    file: UploadFile = File(...),
    tenants: str = Form(..., description='"all" or tenant names separated by commas'),
    exclude_tenants: Optional[str] = Form(None, description="With all tenants only, separated by commas"),
    doc_id: Optional[str] = Form(None, description="Default: taken from the file (front matter or name)"),
    title: Optional[str] = Form(None),
    routes: Optional[str] = Form(None, description="Admin screens the document belongs to, separated by commas"),
    roles: Optional[str] = Form(None, description="Empty: every role"),
    sports: Optional[str] = Form(None, description="Empty: every sport"),
    scope: CallerScope = Depends(require_knowledge_admin),
) -> dict:
    limit = int(get_settings().knowledge_manage.max_file_mb * 1024 * 1024)
    data = await file.read(limit + 1)  # one byte more, so an oversize file is noticed without reading it all
    try:
        return await asyncio.to_thread(
            manage.upload, scope, file.filename or "", data,
            tenants=tenants, exclude_tenants=exclude_tenants, doc_id=doc_id, title=title,
            routes=routes, roles=roles, sports=sports,
        )
    except manage.ManageError as e:
        raise _http(e) from e


@router.patch("/documents/{doc_id}")
async def update_access(doc_id: str, body: AccessUpdate, scope: CallerScope = Depends(require_knowledge_admin)) -> dict:
    try:
        document = await asyncio.to_thread(
            manage.set_access, scope, doc_id.lower(),
            tenants=body.tenants, exclude_tenants=body.exclude_tenants, roles=body.roles,
        )
    except manage.ManageError as e:
        raise _http(e) from e
    return {"document": document}


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, scope: CallerScope = Depends(require_knowledge_admin)) -> dict:
    try:
        await asyncio.to_thread(manage.delete, scope, doc_id.lower())
    except manage.ManageError as e:
        raise _http(e) from e
    return {"doc_id": doc_id.lower(), "deleted": True}


@router.get("/documents/{doc_id}/file")
async def download_document(doc_id: str, _: CallerScope = Depends(require_knowledge_admin)) -> Response:
    try:
        name, content_type, data = await asyncio.to_thread(manage.original_file, doc_id.lower())
    except manage.ManageError as e:
        raise _http(e) from e
    ascii_name = name.encode("ascii", "ignore").decode().replace('"', "").strip() or "document"
    disposition = f"attachment; filename=\"{ascii_name}\"; filename*=UTF-8''{quote(name)}"
    return Response(content=data, media_type=content_type, headers={"Content-Disposition": disposition})
