from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship


class Users(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, index=True, description="用户ID")
    name: str = Field(description="用户名称")
    email: Optional[str] = Field(description="用户邮箱")
    phone: Optional[str] = Field(description="用户电话")
    hashed_password: Optional[str] = Field(description="用户密码")
    role_id: int = Field(foreign_key="roles.id", default=3, description="角色ID")

    role: "Roles" = Relationship(back_populates="users")
    tokens: list["Tokens"] = Relationship(back_populates="user")
    recipes: list["Recipes"] = Relationship(back_populates="user")

    def to_resp(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": (
                self.role.name if self.role else None
            ),  # Get the role name from the related Role object.
            "has_password": bool(self.hashed_password),  # Convert to boolean.
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
    """

    id: int = Field(primary_key=True, index=True, description="角色ID")
    name: str = Field(description="角色名称")
    label: str = Field(description="角色标签")
    users: list[Users] = Relationship(back_populates="role")


class Tokens(SQLModel, table=True):

    id: int = Field(default=None, primary_key=True, index=True, description="令牌ID")
    token: str = Field(description="令牌值")
    uid: int = Field(foreign_key="users.id", description="用户ID")
    expires: datetime = Field(description="过期时间")
    created: datetime = Field(default_factory=datetime.now, description="创建时间")
    ip: Optional[str] = Field(default=None, description="IP地址")
    user_agent: Optional[str] = Field(default=None, description="用户代理")
    desc: Optional[str] = Field(default=None, description="描述")

    user: Users = Relationship(back_populates="tokens")


class RecipeGroups(SQLModel, table=True):
    __tablename__ = "recipe_groups"  # type: ignore
    id: int = Field(
        default=None, primary_key=True, index=True, description="菜谱分类ID"
    )
    name: str = Field(description="菜谱分类名称")
    desc: Optional[str] = Field(default=None, description="菜谱分类描述")
    created: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated: datetime = Field(default_factory=datetime.now, description="更新时间")
    uid: int = Field(foreign_key="users.id", description="用户ID")  # 创建者ID.
    status: int = Field(default=0, description="状态")  # 0:草稿, 1:发布, 2:删除.
    private: bool = Field(default=False, description="是否私有")  # 私有分类.

    recipes: list["Recipes"] = Relationship(back_populates="group")  # 关联菜谱.


class Recipes(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, index=True, description="菜谱ID")
    name: str = Field(description="菜谱名称")
    desc: Optional[str] = Field(default=None, description="菜谱描述")
    created: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated: datetime = Field(default_factory=datetime.now, description="更新时间")
    uid: int = Field(foreign_key="users.id", description="用户ID")
    status: int = Field(
        default=0, description="状态"
    )  # 0:草稿, 1:发布, 2:删除, 3:审核中, 4:审核不通过.
    group_id: int = Field(
        foreign_key="recipe_groups.id", description="菜谱分类ID"
    )  # 关联菜谱分类.
    content: str = Field(description="菜谱内容")  # Markdown 格式.
    cover: Optional[str] = Field(default=None, description="封面图片")  # 图片URL.
    materials: Optional[str] = Field(default=None, description="材料")  # JSON 格式.
    private: bool = Field(default=False, description="是否私有")

    user: Users = Relationship(back_populates="recipes")
    group: RecipeGroups = Relationship(back_populates="recipes")  # 关联菜谱分类.
