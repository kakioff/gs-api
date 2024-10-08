from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, Relationship

from utils import RSAEncrypt


class Users(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, index=True, description="用户ID")
    name: str = Field(description="用户名称")
    email: Optional[str] = Field(description="用户邮箱")
    phone: Optional[str] = Field(description="用户电话")
    hashed_password: Optional[str] = Field(description="用户密码")
    role_id: int = Field(foreign_key="roles.id", default=3, description="角色ID")
    # 角色
    role: "Roles" = Relationship(back_populates="users")

    tokens: list["Tokens"] = Relationship(back_populates="user")

    # region 菜谱相关
    # recipes: list["Recipes"] = Relationship(back_populates="user")
    # 菜谱评论
    # recipe_comments: list["RecipeComments"] = Relationship(back_populates="user")
    # 菜谱被提及评论
    # recipe_replied_comments: list["RecipeComments"] = Relationship(
    #     back_populates="reply_to_user"
    # )
    # endregion
    # 帖子
    posts: list["Posts"] = Relationship(back_populates="user")

    def to_resp(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role, #(
                #self.role.name if self.role else None
            #),  # Get the role name from the related Role object.
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


RECIPE_GROUP_STATUS = ["草稿", "发布", "删除"]


# class RecipeGroups(SQLModel, table=True):
#     __tablename__ = "recipe_groups"  # type: ignore

#     id: int = Field(
#         default=None, primary_key=True, index=True, description="菜谱分类ID"
#     )
#     name: str = Field(description="菜谱分类名称")
#     desc: Optional[str] = Field(default=None, description="菜谱分类描述")
#     created: datetime = Field(default_factory=datetime.now, description="创建时间")
#     updated: datetime = Field(default_factory=datetime.now, description="更新时间")
#     uid: int = Field(foreign_key="users.id", description="用户ID")  # 创建者ID.
#     status: int = Field(default=0, description="状态")  # 0:草稿, 1:发布, 2:删除.
#     private: bool = Field(default=False, description="是否私有")  # 私有分类.

#     recipes: list["Recipes"] = Relationship(back_populates="group")  # 关联菜谱.


# RECIPE_STATUS = ["草稿", "发布", "删除", "审核中", "审核不通过"]


# class Recipes(SQLModel, table=True):
#     id: int = Field(default=None, primary_key=True, index=True, description="菜谱ID")
#     name: str = Field(description="菜谱名称")
#     desc: Optional[str] = Field(default=None, description="菜谱描述")
#     created: datetime = Field(default_factory=datetime.now, description="创建时间")
#     updated: datetime = Field(default_factory=datetime.now, description="更新时间")
#     uid: int = Field(foreign_key="users.id", description="用户ID")
#     status: int = Field(
#         default=0, description="状态"
#     )  # 0:草稿, 1:发布, 2:删除, 3:审核中, 4:审核不通过.
#     group_id: int = Field(
#         foreign_key="recipe_groups.id", description="菜谱分类ID"
#     )  # 关联菜谱分类.
#     content: str = Field(description="菜谱内容")  # Markdown 格式.
#     cover: Optional[str] = Field(default=None, description="封面图片")  # 图片URL.
#     materials: Optional[str] = Field(default=None, description="材料")  # JSON 格式.
#     private: bool = Field(default=False, description="是否私有")

#     user: Users = Relationship(back_populates="recipes")
#     group: RecipeGroups = Relationship(back_populates="recipes")  # 关联菜谱分类.
#     # setps: list["RecipeSteps"] = Relationship(back_populates="recipe")
#     # comments: list["RecipeComments"] = Relationship(
#     #     back_populates="recipe"
#     # )  # 关联评论.

#     def to_resp(self):
#         return {
#             "id": self.id,
#             "name": self.name,
#             "desc": self.desc,
#             "created": self.created.strftime("%Y-%m-%d %H:%M:%S"),  # 格式化时间.
#             "updated": self.updated.strftime("%Y-%m-%d %H:%M:%S"),  # 格式化时间.
#             "username": self.user.name,
#             "status": RECIPE_STATUS[self.status],
#             "group": self.group.name if self.group else None,
#             "cover": self.cover,
#         }

# class RecipeIngredient(SQLModel, table=True):
#     __tablename__ = "recipe_ingredient"  # type: ignore
#     id: int = Field(default=None, primary_key=True, index=True, description="ID")
#     recipe_id: int = Field(foreign_key="recipes.id", description="菜谱ID")
#     name: str = Field(description="材料名称")  # 材料名称.
#     # 数量
#     quantity: Optional[str] = Field(default=None, description="数量")  # 数量.
#     unit: Optional[str] = Field(default=None, description="单位")  # 单位.
#     desc: Optional[str] = Field(default=None, description="材料描述")


# class RecipeSteps(SQLModel, table=True):  # 菜谱步骤.
#     __tablename__ = "recipe_steps"  # type: ignore

#     id: int = Field(
#         default=None, primary_key=True, index=True, description="步骤ID"
#     )  # 步骤ID.
#     recipe_id: int = Field(foreign_key="recipes.id", description="菜谱ID")
#     desc: str = Field(description="步骤描述")
#     order: int = Field(description="步骤顺序")
#     img: Optional[str] = Field(default=None, description="步骤图片")


# class RecipeComments(SQLModel, table=True):  # 菜谱评论.
#     __tablename__ = "recipe_comments"  # type: ignore

#     id: int = Field(default=None, primary_key=True, index=True, description="评论ID")
#     recipe_id: int = Field(foreign_key="recipes.id", description="菜谱ID")
#     content: str = Field(description="评论内容")
#     created: datetime = Field(default_factory=datetime.now, description="创建时间")
#     updated: datetime = Field(default_factory=datetime.now, description="更新时间")
#     uid: int = Field(foreign_key="users.id", description="用户ID")
#     status: int = Field(default=0, description="状态")
#     private: bool = Field(default=False, description="是否私有")
#     reply_to: Optional[int] = Field(
#         foreign_key="recipe_comments.id", description="回复评论ID"
#     )
#     reply_to_uid: Optional[int] = Field(
#         foreign_key="users.id", description="回复用户ID"
#     )
#     # 创建人
#     # user: Users = Relationship(back_populates="recipe_comments")
#     # 菜谱
#     # recipe: Recipes = Relationship(back_populates="comments")
#     # 回复评论
#     # reply_to_comment: Optional["RecipeComments"] = Relationship(
#     #     back_populates="replys"
#     # )
#     # 被回复的评论
#     # replys: list["RecipeComments"] = Relationship(
#     #     back_populates="reply_to_comment",
#     # )
#     # 回复用户
#     # reply_to_user: Optional[Users] = Relationship(
#     #     back_populates="recipe_replied_comments"
#     # )


class Posts(SQLModel, table=True):  # 帖子.
    __tablename__ = "posts"  # type: ignore

    id: int = Field(default=None, primary_key=True, index=True, description="帖子ID")
    title: str = Field(description="帖子标题")
    content: str = Field(description="帖子内容")
    created: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated: datetime = Field(default_factory=datetime.now, description="更新时间")
    uid: int = Field(foreign_key="users.id", description="用户ID")
    status: int = Field(default=0, description="状态 0:未发布 1:已发布 0:已隐藏")
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
            "user": self.user.name
        }