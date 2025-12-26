from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class InboundReq(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    item_code: str
    item_name: Optional[str] = None
    brand: Optional[str] = None
    spec: Optional[str] = None
    location: str
    lot: str
    quantity: int = Field(gt=0)

class OutboundReq(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    item_code: str
    item_name: Optional[str] = None
    lot: str
    quantity: int = Field(gt=0)
    location: Optional[str] = None  # 선택(없으면 여러 로케이션 합산 차감)
    remark: Optional[str] = None

class MoveReq(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    item_code: str
    item_name: Optional[str] = None
    lot: str
    quantity: int = Field(gt=0)
    # 프론트에서 from_location / to_location 혹은 location_from / location_to 무엇이 와도 받도록 alias 처리
    from_location: str = Field(alias="from_location")
    to_location: str = Field(alias="to_location")
    remark: Optional[str] = None

    # alias 추가 지원 (pydantic v2: validation_alias)
    # FastAPI에서 들어오는 JSON 키가 location_from/location_to인 경우를 위해 아래를 추가로 허용
    # (populate_by_name=True + custom validators 없이도, 아래처럼 두 개 필드를 추가로 두면 깔끔)
