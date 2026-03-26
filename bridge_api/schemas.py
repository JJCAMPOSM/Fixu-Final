from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, EmailStr


class UserRole(str, Enum):
    ADMIN = "admin"
    AGENT = "agent"
    REQUESTER = "requester"


class TicketStatus(str, Enum):
    OPEN = "open"
    PENDING = "pending"
    SOLVED = "solved"
    CLOSED = "closed"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# ============ User Models ============
class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole
    avatar: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    avatar: Optional[str] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Ticket Models ============
class TicketBase(BaseModel):
    title: str = Field(..., max_length=200)
    body: str
    status: TicketStatus = TicketStatus.OPEN
    priority: TicketPriority = TicketPriority.MEDIUM


class TicketCreate(TicketBase):
    requester_id: int
    team_id: Optional[int] = None
    assignee_team_member_id: Optional[int] = None
    category_id: Optional[int] = None


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    team_id: Optional[int] = None
    assignee_team_member_id: Optional[int] = None
    category_id: Optional[int] = None


class TicketResponse(TicketBase):
    id: int
    requester_id: int
    team_id: Optional[int]
    assignee_team_member_id: Optional[int]
    category_id: Optional[int]
    rating: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TicketDetailResponse(TicketResponse):
    requester: Optional["RequesterResponse"] = None
    team: Optional["TeamResponse"] = None
    category: Optional["CategoryResponse"] = None
    comments: List["CommentResponse"] = []


# ============ Team Models ============
class TeamBase(BaseModel):
    name: str = Field(..., max_length=120)


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: Optional[str] = None


class TeamResponse(TeamBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TeamMemberBase(BaseModel):
    user_id: int
    team_id: int


class TeamMemberResponse(TeamMemberBase):
    id: int
    user: Optional[UserResponse] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Requester Models ============
class RequesterBase(BaseModel):
    name: str = Field(..., max_length=120)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)


class RequesterCreate(RequesterBase):
    pass


class RequesterUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class RequesterResponse(RequesterBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Category Models ============
class CategoryBase(BaseModel):
    name: str = Field(..., max_length=120)
    description: Optional[str] = None
    color: str = Field(default="#6366f1", max_length=7)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Comment Models ============
class CommentBase(BaseModel):
    body: str
    private: bool = False


class CommentCreate(CommentBase):
    ticket_id: int
    team_member_id: int


class CommentResponse(CommentBase):
    id: int
    ticket_id: int
    team_member_id: int
    team_member: Optional[TeamMemberResponse] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Sync Models ============
class SyncRequest(BaseModel):
    entity: str  # users, tickets, teams, requesters, categories
    action: str  # create, update, delete
    data: dict
    source: str  # laravel o flask


class SyncResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    synced_at: datetime = Field(default_factory=datetime.utcnow)


# ============ Webhook Models ============
class WebhookPayload(BaseModel):
    event: str
    entity: str
    entity_id: int
    data: dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Forward references
TicketDetailResponse.model_rebuild()
