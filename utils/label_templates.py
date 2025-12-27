from dataclasses import dataclass

@dataclass
class LabelTemplate:
    name: str
    page_w_mm: float
    page_h_mm: float
    cols: int
    rows: int
    label_w_mm: float
    label_h_mm: float
    margin_left_mm: float
    margin_top_mm: float
    gap_x_mm: float
    gap_y_mm: float

# NOTE:
# 프린터/드라이버에 따라 실제 출력 오차가 있을 수 있어요.
# margin/gap 값을 미세 조정하면 정확히 맞출 수 있습니다.

LS_3108 = LabelTemplate(
    name="LS-3108",
    page_w_mm=210.0, page_h_mm=297.0,
    cols=2, rows=7,
    label_w_mm=99.1, label_h_mm=38.1,
    margin_left_mm=6.0, margin_top_mm=10.0,
    gap_x_mm=0.0, gap_y_mm=0.0
)

LS_3118 = LabelTemplate(
    name="LS-3118",
    page_w_mm=210.0, page_h_mm=297.0,
    cols=1, rows=4,
    label_w_mm=99.1, label_h_mm=140.0,
    margin_left_mm=55.5, margin_top_mm=8.5,
    gap_x_mm=0.0, gap_y_mm=0.0
)

TEMPLATES = {"LS-3108": LS_3108, "LS-3118": LS_3118}
