from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, Relationship


class Users(SQLModel, table=True):
    id: str = Field(primary_key=True, nullable=False, description="用户ID")
    name: str = Field(description="用户名称")
    email: Optional[str] = Field(description="用户邮箱")
    phone: Optional[str] = Field(description="用户电话")
    hashed_password: Optional[str] = Field(description="用户密码")
    role_id: int = Field(foreign_key="roles.id", default=3, description="角色ID")

    # github
    github_id: Optional[int] = Field(description="github用户ID", default=None)
    github_name: Optional[str] = Field(description="github用户名", default=None)

    
    # 角色
    role: "Roles" = Relationship(back_populates="users")
    avatar_id: Optional[str] = Field(description="用户头像", default=None)
    # avatar: Optional["Files"] = Relationship(back_populates="user_avatar")

    # 帖子
    posts: list["Posts"] = Relationship(back_populates="user")
    files: list["Files"] = Relationship(back_populates="user")

    def to_resp(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "has_password": bool(self.hashed_password),
            "avatar": f"/file/avatar/{self.id}" # if self.avatar_id else None,
        }


class Roles(SQLModel, table=True):
    """
    |id|name|label|
    |--|----|-----|
    | 0|guest|游客|
    | 1|disable|禁用|
    | 2|subscribe|订阅者|
    | 3|user|普通用户|
    | 4|admin|管理员|
    | 5|super|超管|

    ---

    ```sql
    # 生成数据
    insert into roles (id,name,label) values (0,'guest','游客'),(1,'disable','禁用'),(2,'subscribe','订阅者'),(3,'user','普通用户'),(4,'admin','管理员'),(5,'super','超管');
    ```
    """

    id: int = Field(primary_key=True, index=True, description="角色ID")
    name: str = Field(description="角色名称")
    label: str = Field(description="角色标签")
    users: list[Users] = Relationship(back_populates="role")


RECIPE_GROUP_STATUS = ["草稿", "发布", "删除"]


class Posts(SQLModel, table=True):  # 帖子.
    __tablename__ = "posts"  # type: ignore

    id: str = Field(default=None, primary_key=True, index=True, description="帖子ID")
    title: str = Field(description="帖子标题")
    content: str = Field(description="帖子内容")
    created: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated: datetime = Field(default_factory=datetime.now, description="更新时间")
    uid: str = Field(foreign_key="users.id", description="用户ID")
    status: int = Field(default=0, description="状态 0:未发布 1:已发布 -1:已隐藏")
    private: bool = Field(default=False, description="是否私有")
    # 用户
    user: Users = Relationship(back_populates="posts")

    def to_resp(self, all_contents=False):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content if all_contents else self.content[:20],
            "created": self.created,
            "updated": self.updated,
            "status": self.status,
            "private": self.private,
            "user": {
                "id": self.user.id,
                "name": self.user.name,
            },
        }


class Files(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True, index=True, description="文件ID")
    name: str = Field(description="文件名")
    size: int = Field(description="文件大小")
    path: str = Field(description="文件路径")
    type: str = Field(description="文件类型")
    etag: str = Field(description="文件etag")
    created: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated: datetime = Field(default_factory=datetime.now, description="更新时间")
    uid: str = Field(foreign_key="users.id", description="用户ID")

    user: Users = Relationship(back_populates="files")
    hidden: bool = Field(default=False, description="是否隐藏")
    # user_avatar: Optional["Users"] = Relationship(back_populates="avatar")

    def to_resp(self):
        return {
            "id": self.id,
            "name": self.name,
            "size": self.size,
            "type": self.type,
            "created": self.created,
            "updated": self.updated,
            "user": {
                "id": self.user.id,
                "name": self.user.name,
            },
        }
