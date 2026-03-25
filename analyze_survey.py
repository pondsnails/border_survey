import pandas as pd
import datetime

# --- Configuration ---
INPUT_CSV = 'survey_data.csv'  # Expected input file name
OUTPUT_CSV_TABLE = 'border_analysis.csv'
OUTPUT_COMMENTS = 'comments.txt'

# Department to School Mapping
DEPT_SCHOOL_MAP = {
    '数学系': '理学院', '物理学系': '理学院', '化学系': '理学院', '地球惑星科学系': '理学院',
    '機械系': '工学院', 'システム制御系': '工学院', '電気電子系': '工学院', '情報通信系': '工学院', '経営工学系': '工学院',
    '材料系': '物質理工学院', '応用化学系': '物質理工学院',
    '数理・計算科学系': '情報理工学院', '情報工学系': '情報理工学院',
    '生命理工学系': '生命理工学院',
    '建築学系': '環境・社会理工学院', '土木・環境工学系': '環境・社会理工学院', '融合理工学系': '環境・社会理工学院'
}

# List of all departments in order
ALL_DEPTS = list(DEPT_SCHOOL_MAP.keys())

def analyze_data(df):
    results = {dept: {'in_pass_min': None, 'in_fail_max': None, 
                      'out_pass_min': None, 'out_fail_max': None, 
                      'out_pass_count': 0} for dept in ALL_DEPTS}

    valid_response_count = 0

    for index, row in df.iterrows():
        try:
            score = int(float(row['系所属点（3100点満点）']))
        except (ValueError, TypeError):
            continue

        origin_school = str(row['所属学院（1年次）']).strip()
        final_dept = str(row['実際に所属が決定した系']).strip()
        
        preferences = []
        for i in range(1, 7):
            col_name = f'第{i}志望'
            if col_name in row and pd.notna(row[col_name]):
                dept_name = str(row[col_name]).strip()
                if dept_name: # Ensure not empty string
                    preferences.append(dept_name)
        
        # --- レコード全体のバリデーション（不正データは行ごと破棄） ---
        is_valid_record = True
        outside_count = 0

        for i, dept in enumerate(preferences):
            if dept not in DEPT_SCHOOL_MAP:
                is_valid_record = False # 辞書にない不明な系が含まれていたら破棄
                break
                
            if DEPT_SCHOOL_MAP[dept] != origin_school:
                outside_count += 1
                if i > 0 or outside_count > 1:
                    # 学院外が第2志望以降にある、または2つ以上ある場合はルール違反
                    is_valid_record = False
                    break
                    
        if not is_valid_record:
            continue # この学生のデータは信用できないため全体をスキップ

        valid_response_count += 1

        try:
            final_idx = preferences.index(final_dept)
        except ValueError:
            final_idx = -1

        # --- 合否データの記録 ---
        for i, dept in enumerate(preferences):
            is_inside = (DEPT_SCHOOL_MAP[dept] == origin_school)
            
            if final_idx != -1 and i == final_idx:
                # PASS
                key = 'in_pass_min' if is_inside else 'out_pass_min'
                current_val = results[dept][key]
                if current_val is None or score < current_val:
                    results[dept][key] = score
                
                if not is_inside:
                    results[dept]['out_pass_count'] += 1
                break # 配属決定以降の志望順位は判定しない
                
            else:
                # FAIL
                if final_idx == -1 or final_idx > i:
                    key = 'in_fail_max' if is_inside else 'out_fail_max'
                    current_val = results[dept][key]
                    if current_val is None or score > current_val:
                        results[dept][key] = score

    return results, valid_response_count


def format_results_for_csv(results):
    table_data = []
    # 矛盾フラグ用のカラムを追加
    columns = ['学院', '系', '学院外 ○', '学院外 ×', '学院外人数', '学院内 ○', '学院内 ×', 'ボーダー', 'ステータス']
    
    for dept in ALL_DEPTS:
        r = results[dept]
        
        in_min = r['in_pass_min']
        in_max_fail = r['in_fail_max']
        
        border_str = '-'
        status = '正常'

        if in_min is not None and in_max_fail is not None:
            if in_max_fail >= in_min:
                status = '⚠️矛盾あり(逆転)'
            # ボーダーは「不合格最高点 + 1」から「合格最低点」の間にある
            border_str = f"{in_max_fail + 1} ~ {in_min}"
        elif in_min is not None:
            border_str = f"? ~ {in_min}"
            status = '下限不明'
        elif in_max_fail is not None:
            border_str = f"{in_max_fail + 1} ~ ?"
            status = '上限不明'
        else:
            status = 'データなし'

        school = DEPT_SCHOOL_MAP.get(dept, '')
        
        row_data = [
            school,
            dept,
            r['out_pass_min'] if r['out_pass_min'] is not None else '-',
            r['out_fail_max'] if r['out_fail_max'] is not None else '-',
            r['out_pass_count'], 
            in_min if in_min is not None else '-',
            in_max_fail if in_max_fail is not None else '-',
            border_str,
            status
        ]
        table_data.append(row_data)
        
    return table_data, columns

def export_csv(table_data, headers):
    df_out = pd.DataFrame(table_data, columns=headers)
    df_out.to_csv(OUTPUT_CSV_TABLE, index=False, encoding='utf-8-sig')
    print(f"CSV table saved to {OUTPUT_CSV_TABLE}")

def export_comments(df):
    with open(OUTPUT_COMMENTS, 'w', encoding='utf-8') as f:
        f.write("# コメント・アドバイス集\n\n")
        cols = ['感想・アドバイス', '自由回答欄']
        for col in cols:
            if col in df.columns:
                f.write(f"## {col}\n")
                for item in df[col].dropna():
                    if str(item).strip():
                        f.write(f"- {item}\n")
                f.write("\n")
    print(f"Comments saved to {OUTPUT_COMMENTS}")

def main():
    try:
        df = pd.read_csv(INPUT_CSV)
        print("Data loaded successfully.")
    except FileNotFoundError:
        print(f"Error: {INPUT_CSV} not found.")
        return

    results, count = analyze_data(df)
    table_data, headers = format_results_for_csv(results)
    export_csv(table_data, headers)
    export_comments(df)

if __name__ == "__main__":
    main()
