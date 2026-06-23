import os
import shutil
from fastapi import APIRouter, UploadFile, File
from services.rag import add_document, list_documents, delete_document, UPLOAD_DIR

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename:
        return {"error": "文件名不能为空"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".txt", ".pdf", ".docx"):
        return {"error": f"不支持的文件类型: {ext}，仅支持 txt、pdf 和 docx"}

    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        count = add_document(filepath, file.filename)
    except Exception as e:
        return {"error": f"文档处理失败: {str(e)}"}

    return {"message": f"上传成功", "filename": file.filename, "chunks": count}


@router.get("/list")
async def list_all():
    return {"documents": list_documents()}


@router.delete("/{filename}")
async def remove(filename: str):
    # Delete from vector DB
    ok = delete_document(filename)
    # Delete file
    filepath = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    if ok:
        return {"message": f"已删除 {filename}"}
    return {"error": "文档不存在"}
