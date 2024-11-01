import datetime
import os
from fastapi import Depends, File, Query, Response, UploadFile
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select, text

from auth import get_user
from config import Settings, get_settings
from database import get_db
from database.models import Files, Users
from database.mongodb_models import DBFile, User
from models import CurrentUser
from utils import get_file_md5, resp_err, resp_succ
from . import router

from api import cos
import utils


@router.get("/all")
async def get_all_files(
    search: str | None = Query(None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1),
    usr: CurrentUser = Depends(get_user),
    db: Session = Depends(get_db),
):
    query = select(Files).where(Files.uid == usr.user.uid)
    if search:
        query = query.where(text(f"name like '%{search}%'"))
    total = db.exec(select(text("count(*)")).select_from(query.subquery())).one()
    files = db.exec(query.offset((page - 1) * size).limit(size)).all()
    return resp_succ([file.to_resp() for file in files], total=total)


@router.post("/")
async def create_file(
    file_data: list[UploadFile] = File(..., alias="file[]"),
    usr: CurrentUser = Depends(get_user),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
):
    files = {}
    errors = []

    for file in file_data:
        try:
            file_md5 = get_file_md5(file.file)
            file.file.seek(0)

            file_type = (
                file.content_type.split("/")[-1] if file.content_type else "unknown"
            )

            file_name = f"{file_md5}.{file.filename}"
            temp_dir = os.path.join(settings.temp_dir, file_name)
            if not os.path.exists(os.path.dirname(temp_dir)):
                os.makedirs(os.path.dirname(temp_dir), exist_ok=True)
            # 保存文件
            with open(temp_dir, "wb") as f:
                f.write(file.file.read())
                f.flush()
                f.close()
            file_size = os.path.getsize(temp_dir)
            # 上传文件
            cos_path = f"users/{usr.user.uid}/{datetime.datetime.now().strftime('%Y/%m')}/{file_name}"

            res = cos.upload_file(temp_dir, cos_path)
            # {'Content-Length': '0', 'Connection': 'keep-alive', 'Date': 'Sun, 29 Sep 2024 13:14:07 GMT', 'ETag': '"d41d8cd98f00b204e9800998ecf8427e"', 'Server': 'tencent-cos', 'x-cos-hash-crc64ecma': '0', 'x-cos-request-id': 'NjZmOTUyOWZfOTIxMDcxMDlfNDUxNV8xOWQ3NGQx', 'x-cos-storage-class': 'STANDARD'}
            file_id = utils.generate_uid("file")
            file_db = Files(
                id=file_id,
                name=file.filename or file_name,
                size=file_size,
                path=cos_path,
                type=file_type,
                uid=usr.user.uid,
                etag=res["ETag"],
            )
            db.add(file_db)
            db.commit()
            db.refresh(file_db)
            files[file.filename] = file_db.to_resp()
        except Exception as e:
            errors.append(file.filename)

    return resp_succ({"errors": errors, "files": files})


@router.get("/avatar/{uid}")
async def get_avatar(uid: str):
    user = await User.get(uid)
    if not user:
        return resp_err(detail="用户不存在", code=404)
    # file = db.exec(select(Files).where(Files.id == user.avatar_id)).one_or_none()
    file = await DBFile.get(user.avatar_id)
    if file:
        avatar_path = file.path
    else:
        avatar_path = f"/users/avatar/default/{int(str(user.id), 16)%39+1}.png"

    file = cos.get_file(avatar_path)
    if not file:
        return resp_err(detail="文件不存在", code=404)
    res = Response(content=file, media_type="image/jpeg")
    res.headers["Content-Disposition"] = (
        f"filename={str(user.id).encode('utf-8').decode('latin-1')}"
    )
    return res


@router.get("/{file_id}")
async def get_file(
    file_id: str,
    db: Session = Depends(get_db),
):
    file = db.get(Files, file_id)
    if not file:
        return resp_err(detail="文件不存在", code=404)
    file_type = file.type
    file_name = file.name

    file_info = cos.file_exists(file.path)
    if file_info:
        return StreamingResponse(
            cos.get_file_stream(file.path),
            media_type=file_type,
            headers={
                "Content-Disposition": f"filename={file_name.encode('utf-8').decode('latin-1')}",
                "Content-Type": file_info["Content-Type"],
                "Content-Length": file_info["Content-Length"],
            },
        )
    else:
        return resp_err(detail="文件不存在", code=404)


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    db: Session = Depends(get_db),
):
    file = db.get(Files, file_id)
    if not file:
        return resp_err(detail="文件不存在", code=404)
    res = cos.delete_file(file.path)
    print(res)
    if res:
        db.delete(file)
        db.commit()
        return resp_succ()
    else:
        return resp_err(detail="文件删除失败", code=500)