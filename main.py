class Grid2D:
    """N x N 2차원 패턴/필터 저장 및 좌표 조회/수정 구조"""
    """size와 cells를 가지고 있어서 get(r, c), set(r, c, value)로 좌표 접근이 명확"""

    def __init__(self, data):
        if not isinstance(data, list) or not data or not all(isinstance(row, list) for row in data):
            raise ValueError("2차원 리스트 형태여야 합니다.")
        rows = len(data)
        cols = len(data[0])
        if cols == 0 or not all(len(row) == cols for row in data):
            raise ValueError("모든 행의 열 개수가 같아야 합니다.")
        if rows != cols:
            raise ValueError(f"정사각 격자(N x N)가 아닙니다: {rows}x{cols}")

        self.size = rows
        self.cells = [[float(val) for val in row] for row in data]

    def get(self, row, col):
        return self.cells[row][col]

    def set(self, row, col, value):
        self.cells[row][col] = float(value)


def compute_mac(pattern_grid, filter_grid):
    """두 Grid2D의 동일 위치 원소를 곱해 누적 합산(MAC) 반환"""
    """for r in range(n): for c in range(n): 이중 반복문만 사용해 n * n번 곱셈과 덧셈을 수행하므로,
    외부 라이브러리 없이도 시간 복잡도 $O(N^2)$ 구조를 그대로 보여줌"""
    if pattern_grid.size != filter_grid.size:
        raise ValueError(
            f"크기 불일치: 패턴 {pattern_grid.size}x{pattern_grid.size} vs 필터 {filter_grid.size}x{filter_grid.size}"
        )

    total = 0.0
    n = pattern_grid.size
    for r in range(n):
        for c in range(n):
            total += pattern_grid.get(r, c) * filter_grid.get(r, c)
    return total

EPSILON = 1e-9 #허용 오차 비교

#컴퓨터의 부동소수점(float) 계산은 0.9가 0.8999999999999999처럼 미세하게 어긋날 수 있다.
#score_a == score_b로 엄격히 비교하면 실제로 같은 점수인데도 다르게 판정될 수 있으므로,
#abs(score_a - score_b) < 1e-9이면 동점(UNDECIDED / 판정 불가)으로 처리한다.



def normalize_label(raw_label): #라벨 정규화
    """'expected' 값('+', 'x') 또는 filter 키('cross', 'x')를 'Cross' 또는 'X'로 정규화"""
    #'+', 'cross', 'CROSS'를 모두 'Cross'로, 'x', 'X'를 모두 'X'로 통일.
    """데이터나 입력마다 '+', 'cross', 'X', 'x'처럼 표기가 다를 수 있다.
    내부에서 'Cross'와 'X' 두 가지 표준 라벨로 통일해 두면
    비교하거나 출력할 때 대소문자/기호 차이를 신경 쓰지 않아도 된다"""
    if not isinstance(raw_label, str):
        raise ValueError(f"지원하지 않는 라벨 타입입니다: {raw_label}")

    cleaned = raw_label.strip().lower()
    if cleaned in ("+", "cross"):
        return "Cross"
    if cleaned == "x":
        return "X"
    raise ValueError(f"알 수 없는 라벨입니다: '{raw_label}'")


def judge_scores(score_cross, score_x, epsilon=EPSILON):
    """
    Cross 필터 점수와 X 필터 점수를 허용오차(epsilon) 기준으로 비교해 판정 반환
    - 차이 < epsilon: 동점으로 간주하여 'UNDECIDED'
    - score_cross > score_x: 'Cross'
    - score_x > score_cross: 'X'
    """
    #abs(score_cross - score_x) < 1e-9이면 'UNDECIDED'를 반환하고,
    #evaluate_prediction에서는 'UNDECIDED'일 때 'FAIL'이 되도록 처리.(결과 예시의 size_13_1 동점 규칙과 일치).
    if abs(score_cross - score_x) < epsilon:
        return "UNDECIDED"
    if score_cross > score_x:
        return "Cross"
    return "X"

"""
모드 1에서 3×3 격자(3줄 × 각 줄 숫자 3개)를 한 줄씩 공백으로 구분해 입력받고,
행 수·열 수·숫자 변환이 어긋나면 안내 문구를 띄우고 다시 입력받게 만든다
"""
def evaluate_prediction(predicted_label, expected_label):
    """정규화된 판정 라벨과 기대 라벨을 비교해 'PASS' 또는 'FAIL' 반환"""
    if predicted_label not in ("Cross", "X"):
        return "FAIL"
    return "PASS" if predicted_label == expected_label else "FAIL"

def read_grid_from_console(size, title):
    """size x size 2차원 격자를 한 줄씩 공백 구분으로 입력받고 검증해 Grid2D 반환"""
    # 입력 형식 오류가 발생하면 안내 문구를 띄우고 다시 입력받도록 반복
    # 줄에 숫자가 3개가 아니거나 글자가 섞여 들어오면
    # 입력 형식 오류: 각 줄에 3개의 숫자를 공백으로 구분해 입력하세요.를 출력한 뒤,
    # 해당 격자(필터 A, 필터 B, 패턴)를 처음부터 다시 입력받게 함.
    while True:
        print(f"{title} ({size}줄 입력, 공백 구분)")
        rows = []
        valid = True

        for _ in range(size):
            line = input().strip()
            parts = line.split()

            if len(parts) != size:
                print(f"입력 형식 오류: 각 줄에 {size}개의 숫자를 공백으로 구분해 입력하세요.")
                valid = False
                break

            try:
                parsed_row = [float(token) for token in parts]
            except ValueError:
                print(f"입력 형식 오류: 각 줄에 {size}개의 숫자를 공백으로 구분해 입력하세요.")
                valid = False
                break

            rows.append(parsed_row)

        if valid and len(rows) == size:
            return Grid2D(rows)


def run_mode_1():
    """모드 1: 3x3 필터 A, B 입력 및 패턴(직접 입력 또는 자동 생성) -> MAC 연산 -> 판정 출력"""
    print("\n#---------------------------------------")
    print("# [1] 필터 입력")
    print("#---------------------------------------")
    filter_a = read_grid_from_console(3, "필터 A")
    filter_b = read_grid_from_console(3, "필터 B")
    print("필터 A, B 저장 완료.")

    print("\n#---------------------------------------")
    print("# [2] 패턴 입력 / 자동 생성")
    print("#---------------------------------------")
    while True:
        print("패턴 방식을 선택하세요:")
        print("1. 직접 입력 (3x3)")
        print("2. 십자가(Cross) 자동 생성 (3x3)")
        print("3. X 자동 생성 (3x3)")
        pat_choice = input("선택: ").strip()

        if pat_choice == "1":
            pattern = read_grid_from_console(3, "패턴")
            break
        if pat_choice == "2":
            pattern = generate_pattern_by_size(3, "cross")
            print("3x3 십자가(Cross) 패턴 자동 생성 완료.")
            break
        if pat_choice == "3":
            pattern = generate_pattern_by_size(3, "x")
            print("3x3 X 패턴 자동 생성 완료.")
            break

        print("잘못된 선택입니다. 1, 2, 3 중 하나를 입력하세요.")

    score_a = compute_mac(pattern, filter_a)
    score_b = compute_mac(pattern, filter_b)

    print("\n#---------------------------------------")
    print("# [3] MAC 결과")
    print("#---------------------------------------")
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")

    if abs(score_a - score_b) < EPSILON:
        print(f"판정: 판정 불가 (|A-B| < {EPSILON})")
    elif score_a > score_b:
        print("판정: A")
    else:
        print("판정: B")

    return pattern, filter_a, filter_b


import json
import os
import re


def load_filters(raw_filters):
    """raw_filters 딕셔너리를 {size: {"Cross": Grid2D, "X": Grid2D}} 형태로 변환"""
    #size_5, size_13, size_25 안에 정규화된 라벨(Cross, X)의 Grid2D 필터를 담아둔다.
    if not isinstance(raw_filters, dict):
        raise ValueError("'filters' 항목이 객체(dict) 형식이 아닙니다.")

    filters_by_size = {}
    for size_key, filter_map in raw_filters.items():
        match = re.fullmatch(r"size_(\d+)", str(size_key))
        if not match or not isinstance(filter_map, dict):
            continue

        n = int(match.group(1))
        normalized_map = {}
        for raw_k, raw_grid in filter_map.items():
            label = normalize_label(raw_k)
            grid = Grid2D(raw_grid)
            if grid.size != n:
                raise ValueError(f"{size_key}의 {label} 필터 크기가 {grid.size}x{grid.size}로 {n}x{n}과 다릅니다.")
            normalized_map[label] = grid

        if "Cross" not in normalized_map or "X" not in normalized_map:
            raise ValueError(f"{size_key}에 'Cross'와 'X' 필터가 모두 필요합니다.")

        filters_by_size[n] = normalized_map

    return filters_by_size


def extract_size_from_pattern_key(pattern_key):
    """'size_{N}_{idx}' 형태의 패턴 키에서 N(정수)을 추출"""
    #size_{N}_{idx} 형태의 키에서 N을 뽑아 해당 size_N 필터와 연결한다.
    match = re.fullmatch(r"size_(\d+)_.+", str(pattern_key))
    if not match:
        raise ValueError(f"패턴 키 형식이 'size_{{N}}_{{idx}}'와 다릅니다: '{pattern_key}'")
    return int(match.group(1))


def run_mode_2(json_path="data.json"):
    """모드 2: data.json 로드, 검증, 판정 및 PASS/FAIL 출력 후 결과 리스트 반환"""
    # 모드 2에서는 data.json 파일을 로드하고, 필터와 패턴을 검증한 후,
    # 각 패턴에 대해 MAC 연산을 수행하고 판정을 내림.
    # 결과는 리스트로 반환되며,
    # 각 항목은 case_id, size, status, reason, pattern_grid, filter_cross, filter_x를 포함.
    # JSON 파일이 없거나 깨졌거나, size_N 필터가 없거나,
    # 패턴의 행/열 크기가 N×N과 다를 때 프로그램이 죽지 않고
    # 해당 케이스를 FAIL 처리 + 실패 원인 기록으로 넘김.

    results = []

    if not os.path.exists(json_path):
        print(f"[오류] '{json_path}' 파일을 찾을 수 없습니다.")
        return results

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[오류] '{json_path}' 로드/파싱 실패: {exc}")
        return results

    print("\n#---------------------------------------")
    print("# [1] 필터 로드")
    print("#---------------------------------------")
    try:
        filters_by_size = load_filters(data.get("filters"))
        for n in sorted(filters_by_size.keys()):
            print(f"✓ size_{n} 필터 로드 완료 (Cross, X)")
    except Exception as exc:
        print(f"[경고] 필터 로드 중 문제 발생: {exc}")
        filters_by_size = {}

    patterns = data.get("patterns")
    if not isinstance(patterns, dict):
        print("[오류] 'patterns' 항목이 객체(dict) 형식이 아닙니다.")
        return results

    print("\n#---------------------------------------")
    print("# [2] 패턴 분석 (라벨 정규화 적용)")
    print("#---------------------------------------")
    for case_id, item in patterns.items():
        print(f"-- {case_id} ---")
        try:
            if not isinstance(item, dict):
                raise ValueError("패턴 항목이 객체(dict) 형식이 아닙니다.")
            if "input" not in item or "expected" not in item:
                raise ValueError("'input' 또는 'expected' 필드가 누락되었습니다.")

            expected_label = normalize_label(item["expected"])
            n = extract_size_from_pattern_key(case_id)

            if n not in filters_by_size:
                raise ValueError(f"크기 {n}x{n}에 해당하는 필터(size_{n})가 없습니다.")

            pattern_grid = Grid2D(item["input"])
            if pattern_grid.size != n:
                raise ValueError(
                    f"패턴 크기({pattern_grid.size}x{pattern_grid.size})가 키의 크기({n}x{n})와 일치하지 않습니다."
                )

            filter_cross = filters_by_size[n]["Cross"]
            filter_x = filters_by_size[n]["X"]

            if filter_cross.size != n or filter_x.size != n:
                raise ValueError(f"필터 크기가 {n}x{n}과 일치하지 않습니다.")

            score_cross = compute_mac(pattern_grid, filter_cross)
            score_x = compute_mac(pattern_grid, filter_x)
            pred_label = judge_scores(score_cross, score_x, EPSILON)
            status = evaluate_prediction(pred_label, expected_label)

            reason = ""
            if status == "FAIL":
                if pred_label == "UNDECIDED":
                    reason = "동점(UNDECIDED) 처리 규칙에 따라 FAIL"
                else:
                    reason = f"예측({pred_label})과 기대값({expected_label}) 불일치"

            print(f"Cross 점수: {score_cross}")
            print(f"X 점수: {score_x}")
            if reason:
                print(f"판정: {pred_label} | expected: {expected_label} | {status} ({reason})")
            else:
                print(f"판정: {pred_label} | expected: {expected_label} | {status}")

            results.append({
                "case_id": case_id,
                "size": n,
                "status": status,
                "reason": reason,
                "pattern_grid": pattern_grid,
                "filter_cross": filter_cross,
                "filter_x": filter_x,
            })

        except Exception as exc:
            reason = f"스키마/크기/데이터 오류: {exc}"
            print(f"판정: FAIL | 사유: {reason}")
            results.append({
                "case_id": case_id,
                "size": None,
                "status": "FAIL",
                "reason": reason,
                "pattern_grid": None,
                "filter_cross": None,
                "filter_x": None,
            })

    return results

import time


def measure_mac_avg_ms(pattern_grid, filter_grid, repeats=10):
    """I/O를 제외하고 compute_mac 호출 구간만 repeats회 반복 측정해 평균 시간(ms) 반환"""
    # 파일 읽기나 print() 출력 시간은 빼고,
    # compute_mac(pattern, filt) 호출 구간만 time.perf_counter()로 측정한 뒤
    # 10회 평균을 밀리초(ms) 단위로 구함
    start = time.perf_counter()
    for _ in range(repeats):
        compute_mac(pattern_grid, filter_grid)
    elapsed_sec = time.perf_counter() - start
    return (elapsed_sec / repeats) * 1000.0


def build_default_grid(size, kind="cross"):
    """측정용 기본 N x N 격자 생성 (3x3 등 data.json에 없는 크기 보완용)"""
    """
    모드 2에서는 data.json에 5×5, 13×13, 25×25 필터가 있지만,
    요구사항에 따라 3×3까지 포함해서 3×3, 5×5, 13×13, 25×25 표를 출력함.
    (data.json에 없는 3×3은 기본 십자가/X 패턴·필터 쌍으로 측정용 격자를 생성해 둠.)
    """
    # kind는 "cross" 또는 "x"로, 가운데 행/열 또는 대각선에 1.0을 배치하고 나머지는 0.0으로 채움
    # size는 홀수여야 하며, 가운데 행/열 또는 대각선에 1.0을 배치하고 나머지는 0.0으로 채움
    # 예: size=5, kind="cross" -> 가운데 행과 열에 1.0, 나머지 0.0
    # 예: size=5, kind="x" -> 두 대각선에 1.0, 나머지 0.0
    # size가 홀수가 아니면 ValueError를 발생시킴

    mid = size // 2
    cells = [[0.0 for _ in range(size)] for _ in range(size)]
    for r in range(size):
        for c in range(size):
            if kind == "cross":
                if r == mid or c == mid:
                    cells[r][c] = 1.0
            else:
                if r == c or (r + c) == (size - 1):
                    cells[r][c] = 1.0
    return Grid2D(cells)


def print_performance_table(filters_by_size=None, extra_pair_3x3=None, repeats=10):
    """3x3, 5x5, 13x13, 25x25 크기별 평균 MAC 시간(ms) 및 연산 횟수(N^2) 표 출력"""
    if filters_by_size is None:
        filters_by_size = {}

    target_sizes = [3, 5, 13, 25]
    print("\n#---------------------------------------")
    print(f"# [3] 성능 분석 (평균/{repeats}회)")
    print("#---------------------------------------")
    print(f"{'크기':<10} {'평균 시간(ms)':<16} {'연산 횟수'}")
    print("-" * 42)

    for n in target_sizes:
        if n == 3 and extra_pair_3x3 is not None:
            pat_grid, filt_grid = extra_pair_3x3
        elif n in filters_by_size and "Cross" in filters_by_size[n] and "X" in filters_by_size[n]:
            pat_grid = build_default_grid(n, "cross")
            filt_grid = filters_by_size[n]["X"]
        else:
            pat_grid = build_default_grid(n, "cross")
            filt_grid = build_default_grid(n, "x")

        avg_ms = measure_mac_avg_ms(pat_grid, filt_grid, repeats=repeats)
        op_count = n * n
        print(f"{n}×{n:<8} {avg_ms:<16.3f} {op_count}")

def generate_cross_pattern(size, active_val=1.0, bg_val=0.0):
    """크기 N을 입력받아 N x N 십자가(Cross) 패턴(Grid2D) 생성"""
    if not isinstance(size, int) or size <= 0:
        raise ValueError("패턴 크기 N은 1 이상의 정수여야 합니다.")

    mid = size // 2
    cells = []
    for r in range(size):
        row = []
        for c in range(size):
            if size % 2 == 1:
                is_cross = (r == mid or c == mid)
            else:
                is_cross = (r in (mid - 1, mid) or c in (mid - 1, mid))
            row.append(float(active_val if is_cross else bg_val))
        cells.append(row)
    return Grid2D(cells)


def generate_x_pattern(size, active_val=1.0, bg_val=0.0):
    """크기 N을 입력받아 N x N X 패턴(Grid2D) 생성"""
    if not isinstance(size, int) or size <= 0:
        raise ValueError("패턴 크기 N은 1 이상의 정수여야 합니다.")

    cells = []
    for r in range(size):
        row = []
        for c in range(size):
            is_x = (r == c) or ((r + c) == (size - 1))
            row.append(float(active_val if is_x else bg_val))
        cells.append(row)
    return Grid2D(cells)

def generate_pattern_by_size(size, kind="cross"):
    """크기 N과 종류('cross' 또는 'x')를 입력받아 N x N 패턴(Grid2D) 자동 생성"""
    if not isinstance(size, int) or size <= 0:
        raise ValueError("패턴 크기 N은 1 이상의 정수여야 합니다.")

    normalized = str(kind).strip().lower()
    if normalized in ("+", "cross"):
        return generate_cross_pattern(size)
    if normalized == "x":
        return generate_x_pattern(size)
    raise ValueError(f"지원하지 않는 패턴 종류입니다: '{kind}'")


class FlatGrid1D:
    """N x N 2차원 격자를 길이 N^2인 1차원 리스트로 변환해 저장하는 구조"""

    def __init__(self, data):
        grid2d = data if isinstance(data, Grid2D) else Grid2D(data)
        self.size = grid2d.size
        self.flat_cells = [0.0] * (self.size * self.size)
        for r in range(self.size):
            row_offset = r * self.size
            for c in range(self.size):
                self.flat_cells[row_offset + c] = grid2d.get(r, c)

    @classmethod
    def from_grid2d(cls, grid2d):
        return cls(grid2d)

    def get_1d(self, idx):
        return self.flat_cells[idx]

    def set_1d(self, idx, value):
        self.flat_cells[idx] = float(value)

    def get_2d(self, row, col):
        return self.flat_cells[row * self.size + col]

    def set_2d(self, row, col, value):
        self.flat_cells[row * self.size + col] = float(value)


def compute_mac_flat(pattern_flat, filter_flat):
    """길이 N^2인 1차원 배열 두 개를 단일 반복문으로 곱해 누적 합산(MAC) 반환"""
    if pattern_flat.size != filter_flat.size:
        raise ValueError(
            f"크기 불일치: 패턴 {pattern_flat.size}x{pattern_flat.size} vs 필터 {filter_flat.size}x{filter_flat.size}"
        )

    total = 0.0
    p_cells = pattern_flat.flat_cells
    f_cells = filter_flat.flat_cells
    length = len(p_cells)
    for i in range(length):
        total += p_cells[i] * f_cells[i]
    return total


def compare_mac_optimization(pattern_grid, filter_grid, repeats=10):
    """동일 입력·동일 반복 횟수로 2D(기존) vs 1D(최적화) 평균 MAC 시간(ms) 비교"""
    pattern_flat = FlatGrid1D.from_grid2d(pattern_grid)
    filter_flat = FlatGrid1D.from_grid2d(filter_grid)

    start_2d = time.perf_counter()
    for _ in range(repeats):
        score_2d = compute_mac(pattern_grid, filter_grid)
    avg_2d_ms = ((time.perf_counter() - start_2d) / repeats) * 1000.0

    start_1d = time.perf_counter()
    for _ in range(repeats):
        score_1d = compute_mac_flat(pattern_flat, filter_flat)
    avg_1d_ms = ((time.perf_counter() - start_1d) / repeats) * 1000.0

    return {
        "score_2d": score_2d,
        "score_1d": score_1d,
        "avg_2d_ms": avg_2d_ms,
        "avg_1d_ms": avg_1d_ms,
    }


def print_optimization_comparison(filters_by_size=None, extra_pair_3x3=None, repeats=10):
    """크기별(3x3, 5x5, 13x13, 25x25) 2D vs 1D(길이 N^2) 성능 비교 표 출력"""
    if filters_by_size is None:
        filters_by_size = {}

    target_sizes = [3, 5, 13, 25]
    print("\n#---------------------------------------")
    print(f"# [최적화 비교] 2D vs 1D(길이 N^2) (평균/{repeats}회)")
    print("#---------------------------------------")
    print(f"{'크기':<8} {'2D 평균(ms)':<14} {'1D 평균(ms)':<14} {'차이(ms)'}")
    print("-" * 52)

    for n in target_sizes:
        if n == 3 and extra_pair_3x3 is not None:
            pat_grid, filt_grid = extra_pair_3x3
        elif n in filters_by_size and "Cross" in filters_by_size[n] and "X" in filters_by_size[n]:
            pat_grid = generate_cross_pattern(n)
            filt_grid = filters_by_size[n]["X"]
        else:
            pat_grid = generate_cross_pattern(n)
            filt_grid = generate_x_pattern(n)

        comp = compare_mac_optimization(pat_grid, filt_grid, repeats=repeats)
        diff_ms = comp["avg_2d_ms"] - comp["avg_1d_ms"]
        print(
            f"{n}×{n:<6} {comp['avg_2d_ms']:<14.4f} {comp['avg_1d_ms']:<14.4f} {diff_ms:+.4f}"
        )

def print_summary(results):     #결과 요약 출력
    """전체 테스트 수, 통과 수, 실패 수 및 실패 케이스 목록/사유 출력"""
    # 전체 테스트 수 / 통과 수 / 실패 수를 출력하고,
    # 실패 케이스가 있으면 케이스 식별자: 실패 사유 형태로 모아서 보여줌.
    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "PASS")
    failed_items = [r for r in results if r.get("status") != "PASS"]
    failed = len(failed_items)

    print("\n#---------------------------------------")
    print("# [4] 결과 요약")
    print("#---------------------------------------")
    print(f"총 테스트: {total}개")
    print(f"통과: {passed}개")
    print(f"실패: {failed}개")

    if failed_items:
        print("\n실패 케이스:")
        for item in failed_items:
            case_id = item.get("case_id", "알 수 없음")
            reason = item.get("reason", "사유 없음")
            print(f"- {case_id}: {reason}")


def main():
    """Mini NPU Simulator 메인 루프"""
    # 사용자에게 모드 선택을 안내하고, 모드 1 또는 모드 2를 실행 후 결과 출력
    # 모드 1: 필터 A/B 입력 → 저장 확인 → 패턴 입력 → MAC 연산·판정 → 3×3 성능 분석 출력
    # 모드 2: 필터 로드 → 패턴 로드/검증/판정/PASS-FAIL 출력 → 성능 분석(3×3, 5×5, 13×13, 25×25) 출력 → 결과 요약 출력
    # 모드 선택이 잘못되면 안내 문구를 띄우고 다시 선택하도록 반복
    # 모드 1과 모드 2 모두 종료 후 프로그램 종료

    while True:
        print("\n=== Mini NPU Simulator ===")
        print("\n[모드 선택]")
        print("1. 사용자 입력 (3x3)")
        print("2. data.json 분석")
        choice = input("선택: ").strip()

        if choice == "1":
            pattern, filter_a, filter_b = run_mode_1()
            avg_ms = measure_mac_avg_ms(pattern, filter_a, repeats=10)
            print(f"연산 시간(평균/10회): {avg_ms:.3f} ms")
            print_performance_table(extra_pair_3x3=(pattern, filter_a), repeats=10)
            print_optimization_comparison(extra_pair_3x3=(pattern, filter_a), repeats=10)
            break

        if choice == "2":
            json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                filters_by_size = load_filters(raw_data.get("filters"))
            except Exception:
                filters_by_size = {}

            results = run_mode_2(json_path)
            print_performance_table(filters_by_size=filters_by_size, repeats=10)
            print_optimization_comparison(filters_by_size=filters_by_size, repeats=10)
            print_summary(results)
            break

        print("잘못된 선택입니다. 1 또는 2를 입력하세요.")


if __name__ == "__main__":
    main()