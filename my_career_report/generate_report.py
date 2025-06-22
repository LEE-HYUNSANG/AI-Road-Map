# File: generate_report.py
import os
import re
import yaml
import sys
import glob

from utils.loader import load_data
from utils.renderer import render_html
from utils.exporter import html_to_pdf
from utils.fontconfig import set_korean_font
from utils.rounder import round_floats
from charts.chartjs_data import generate_chartjs_data
import json
import subprocess
import shutil

BASE_DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(BASE_DIR, 'config.yaml')
DATA_PATH = os.path.join(BASE_DIR, 'data/sample_input.json')
FIX_PATH = os.path.join(BASE_DIR, 'data/fix/fix_input.json')

# 매핑 테이블: 한글+영문/한글명/영문코드 → 표준 코드
BIG5_MAP = {
    'E': 'E', '외향성': 'E', '외향성 (E)': 'E', 'Extraversion': 'E',
    'A': 'A', '친화성': 'A', '우호성': 'A', '친화성 (A)': 'A', 'Agreeableness': 'A',
    'C': 'C', '성실성': 'C', '성실성 (C)': 'C', 'Conscientiousness': 'C',
    'N': 'N', '신경성': 'N', '정서적 안정성': 'N', '신경성 (N)': 'N', '정서적 안정성 (N)': 'N', 'Neuroticism': 'N',
    'O': 'O', '개방성': 'O', '개방성 (O)': 'O', 'Openness': 'O',
}
RIASEC_MAP = {
    'R': 'R', '현실형': 'R', '현실형(Realistic)': 'R', '현실형 (R)': 'R', 'Realistic': 'R',
    'I': 'I', '탐구형': 'I', '탐구형(Investigative)': 'I', '탐구형 (I)': 'I', 'Investigative': 'I',
    'A': 'A', '예술형': 'A', '예술형(Artistic)': 'A', '예술형 (A)': 'A', 'Artistic': 'A',
    'S': 'S', '사회형': 'S', '사회형(Social)': 'S', '사회형 (S)': 'S', 'Social': 'S',
    'E': 'E', '진취형': 'E', '진취형(Enterprising)': 'E', '진취형 (E)': 'E', 'Enterprising': 'E',
    'C': 'C', '관습형': 'C', '관습형(Conventional)': 'C', '관습형 (C)': 'C', 'Conventional': 'C',
}
VALUES_MAP = {
    'A': 'A', '능력발휘': 'A', '능력발휘 (A)': 'A', 'Achievement': 'A',
    'I': 'I', '자율성': 'I', '자율성 (I)': 'I', 'Independence': 'I',
    'Rec': 'Rec', '보상욕구': 'Rec', '보상': 'Rec', '보상 (Rec)': 'Rec', 'Recognition': 'Rec',
    'Rel': 'Rel', '대인관계': 'Rel', '안정성': 'Rel', '안정성 (Rel)': 'Rel', 'Relationships': 'Rel',
    'S': 'S', '사회적 인정': 'S', '사회적 인정 (S)': 'S', 'Support': 'S',
    'W': 'W', '워라밸': 'W', '워라밸 (W)': 'W', 'Working Conditions': 'W',
}
AI_MAP = {
    'EU': 'EU', '인지적 이해': 'EU', '인지적 이해 (Cognitive Understanding)': 'EU', 'AI 이해 (EU)': 'EU',
    'TS': 'TS', '프롬프트 숙련도': 'TS', '프롬프트 (TS)': 'TS', 'Prompt Skill': 'TS',
    'CE': 'CE', '검증 역량': 'CE', '검증 (CE)': 'CE', 'Critical Evaluation': 'CE',
    'AO': 'AO', '도구 적용력': 'AO', '도구 적용 (AO)': 'AO', 'Attitudinal Openness': 'AO',
    'SE': 'SE', '자기 학습력': 'SE', '학습 (SE)': 'SE', 'Self-Efficacy & Adaptability': 'SE',
    'CB': 'CB', '협업 능력': 'CB', '협업 (CB)': 'CB', 'Collaborative Ability': 'CB',
    'ER': 'ER', '윤리적 책임': 'ER', '윤리 (ER)': 'ER', 'Ethical Responsibility': 'ER',
}
# soft는 한글명 기준 그대로 사용

def collapse_keys(obj):
    """Recursively strip Korean labels like '외향성 (E)' -> 'E'."""
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            m = re.search(r'\(([^)]+)\)\s*$', k)
            new_key = m.group(1) if m else k
            new_obj[new_key] = collapse_keys(v)
        return new_obj
    if isinstance(obj, list):
        return [collapse_keys(v) for v in obj]
    return obj


def check_node() -> None:
    """Ensure the Node.js executable is available."""
    if shutil.which('node') is None:
        raise RuntimeError(
            "Node.js executable not found. Please install Node.js."
        )

def find_metrics_file(name):
    # 이름이 포함된 metrics_data.txt 파일 자동 탐색
    metrics_dir = os.path.join(BASE_DIR, 'data', '02_metrics_data')
    pattern = f"*{name}*_metrics_data.txt"
    files = glob.glob(os.path.join(metrics_dir, pattern))
    if not files:
        raise FileNotFoundError(f"metrics_data.txt 파일을 찾을 수 없습니다: {pattern}")
    return files[0]

def extract_code_from_label(label, mapping):
    # 괄호 안 영문코드 우선 추출
    m = re.search(r'\\(([A-Z]{1,3})\\)', label)
    if m:
        code = m.group(1)
        if code in mapping:
            return code
    # 한글명, 영문명 전체 매칭
    for k in mapping:
        if k in label:
            return mapping[k]
    return None

def parse_metrics_txt(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    result = {}
    big5 = {}; big5_norm = {}; big5_delta = {}
    riasec = {}; riasec_norm = {}; riasec_delta = {}
    values = {}; values_norm = {}; values_delta = {}
    ai = {}; ai_norm = {}; ai_delta = {}
    soft = {}; soft_scores = []
    section = None
    for i, line in enumerate(lines):
        if line.startswith('Ⅰ. 개인성향'):
            section = 'big5'
        elif line.startswith('Ⅱ. 진로 관심도'):
            section = 'riasec'
        elif line.startswith('Ⅲ. 직업 가치관'):
            section = 'values'
        elif line.startswith('Ⅳ. AI 활용능력'):
            section = 'ai'
        elif line.startswith('Ⅴ. 비즈니스·소프트 스킬'):
            section = 'soft'
        elif section and line.startswith('|'):
            parts = [p.strip() for p in line.strip('|').split('|')]
            # Skip header-like rows containing only hyphens
            if all(set(p) <= {'-'} for p in parts):
                continue
            if section == 'big5' and len(parts) == 4:
                k = extract_code_from_label(parts[0], BIG5_MAP)
                if k:
                    try:
                        big5[k] = float(parts[1])
                        big5_norm[k] = float(parts[2])
                        big5_delta[k] = float(parts[3])
                    except ValueError:
                        continue
            elif section == 'riasec' and len(parts) == 4:
                k = extract_code_from_label(parts[0], RIASEC_MAP)
                if k:
                    try:
                        riasec[k] = float(parts[1])
                        riasec_norm[k] = float(parts[2])
                        riasec_delta[k] = float(parts[3])
                    except ValueError:
                        continue
            elif section == 'values' and len(parts) == 4:
                k = extract_code_from_label(parts[0], VALUES_MAP)
                if k:
                    try:
                        values[k] = float(parts[1])
                        values_norm[k] = float(parts[2])
                        values_delta[k] = float(parts[3])
                    except ValueError:
                        continue
            elif section == 'ai' and len(parts) == 4:
                k = extract_code_from_label(parts[0], AI_MAP)
                if k:
                    try:
                        ai[k] = float(parts[1])
                        ai_norm[k] = float(parts[2])
                        ai_delta[k] = float(parts[3])
                    except ValueError:
                        continue
            elif section == 'soft' and len(parts) == 2:
                soft_name = parts[0].split('(')[0].strip()
                try:
                    score = float(parts[1])
                except ValueError:
                    continue
                soft[soft_name] = score
                soft_scores.append({'name': soft_name, 'score': score})
    result['big5'] = big5
    result['big5_norm'] = big5_norm
    result['big5_delta'] = big5_delta
    result['riasec'] = riasec
    result['riasec_norm'] = riasec_norm
    result['riasec_delta'] = riasec_delta
    result['values'] = values
    result['values_norm'] = values_norm
    result['values_delta'] = values_delta
    result['ai'] = ai
    result['ai_norm'] = ai_norm
    result['ai_delta'] = ai_delta
    result['soft'] = soft
    result['soft_scores'] = soft_scores
    return result

def map_insight_tip_section(section_dict, mapping):
    # fix_input.json의 insight/tip에서 한글+영문 키를 표준 코드로 변환
    out = {}
    for k, v in section_dict.items():
        code = extract_code_from_label(k, mapping)
        if code:
            out[code] = v
    return out

def main():
    set_korean_font()
    if len(sys.argv) > 1:
        data_filename = sys.argv[1]
        data_path = os.path.join(BASE_DIR, 'data', data_filename)
    else:
        data_path = DATA_PATH
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    data = load_data(data_path)
    name = data.get('name')
    metrics_file = find_metrics_file(name)
    metrics = parse_metrics_txt(metrics_file)
    fix_path = os.path.join(BASE_DIR, 'data', 'fix', 'fix_input.json')
    with open(fix_path, 'r', encoding='utf-8') as f:
        fix = json.load(f)
    # metrics에서 영역별로 분리하여 data에 삽입
    for key in ['big5', 'big5_norm', 'big5_delta', 'riasec', 'riasec_norm', 'riasec_delta', 'values', 'values_norm', 'values_delta', 'ai', 'ai_norm', 'ai_delta', 'soft', 'soft_scores']:
        if key in metrics:
            data[key] = metrics[key]
    # insight/tip 매핑
    # insight/tip 매핑
    data['insight'] = {}
    if 'insight' in fix:
        data['insight'].update(map_insight_tip_section(fix['insight'], BIG5_MAP))
        if 'riasec' in fix['insight']:
            data['insight']['riasec'] = map_insight_tip_section(
                fix['insight']['riasec'], RIASEC_MAP
            )
        if 'values' in fix['insight']:
            data['insight']['values'] = map_insight_tip_section(
                fix['insight']['values'], VALUES_MAP
            )
        if 'ai' in fix['insight']:
            data['insight']['ai'] = map_insight_tip_section(
                fix['insight']['ai'], AI_MAP
            )
        if 'soft' in fix['insight']:
            data['insight']['soft'] = fix['insight']['soft']

    data['tip'] = {}
    if 'tip' in fix:
        data['tip'].update(map_insight_tip_section(fix['tip'], BIG5_MAP))
        if 'riasec' in fix['tip']:
            data['tip']['riasec'] = map_insight_tip_section(
                fix['tip']['riasec'], RIASEC_MAP
            )
        if 'values' in fix['tip']:
            data['tip']['values'] = map_insight_tip_section(
                fix['tip']['values'], VALUES_MAP
            )
        if 'ai' in fix['tip']:
            data['tip']['ai'] = map_insight_tip_section(
                fix['tip']['ai'], AI_MAP
            )
        if 'soft' in fix['tip']:
            data['tip']['soft'] = fix['tip']['soft']
    # 누락된 표준 키를 None/빈값으로 보장 (big5, riasec, values, ai)
    for k in ['E','A','C','N','O']:
        for field in ['big5', 'big5_norm', 'big5_delta']:
            if field not in data:
                data[field] = {}
            if k not in data[field]:
                data[field][k] = None
    for k in ['R','I','A','S','E','C']:
        for field in ['riasec', 'riasec_norm', 'riasec_delta']:
            if field not in data:
                data[field] = {}
            if k not in data[field]:
                data[field][k] = None
    for k in ['A','I','Rec','Rel','S','W']:
        for field in ['values', 'values_norm', 'values_delta']:
            if field not in data:
                data[field] = {}
            if k not in data[field]:
                data[field][k] = None
    for k in ['EU','TS','CE','AO','SE','CB','ER']:
        for field in ['ai', 'ai_norm', 'ai_delta']:
            if field not in data:
                data[field] = {}
            if k not in data[field]:
                data[field][k] = None
    # soft 리스트도 빈 리스트로 보장
    if 'soft_scores' not in data or not isinstance(data['soft_scores'], list):
        data['soft_scores'] = []
    if isinstance(data.get('soft'), dict):
        data['soft'] = [{'name': k, 'score': v} for k, v in data['soft'].items()]
    data = collapse_keys(data)
    data = round_floats(data, 1)
    os.makedirs(os.path.join(BASE_DIR, 'dist'), exist_ok=True)
    check_node()
    node_modules = os.path.join(BASE_DIR, 'node_modules')
    datalabels_pkg = os.path.join(node_modules, 'chartjs-plugin-datalabels')
    if not os.path.exists(datalabels_pkg):
        raise RuntimeError(
            "Node dependencies not found. Please run 'npm install' in the "
            "my_career_report directory before generating the report."
        )
    chartjs_src = os.path.join(BASE_DIR, 'node_modules', 'chart.js', 'dist', 'chart.umd.js')
    chartjs_dest = os.path.join(os.path.dirname(cfg['output']['html']), 'chart.js')
    shutil.copy2(chartjs_src, chartjs_dest)
    cfg['scripts'] = {'chartjs': chartjs_dest}
    chart_dir = cfg['charts']['images']
    os.makedirs(chart_dir, exist_ok=True)
    chart_data_tmp = os.path.join(chart_dir, 'chartjs_input.json')
    data_for_js = data.copy()
    if isinstance(data_for_js.get('soft'), dict):
        data_for_js['soft'] = [
            {"name": n, "score": s}
            for n, s in zip(
                data_for_js['soft'].get('labels', []),
                data_for_js['soft'].get('scores', [])
            )
        ]
    with open(chart_data_tmp, 'w', encoding='utf-8') as f:
        json.dump(data_for_js, f, ensure_ascii=False)
    node_script = os.path.join(BASE_DIR, 'charts', 'render_chartjs_images.js')
    try:
        subprocess.run(['node', node_script, chart_data_tmp, chart_dir], check=True)
        print(f"Chart images saved to {chart_dir}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Warning: chart rendering failed: {e}. Continuing without charts.")
    data_for_chart = data.copy()
    if isinstance(data_for_chart.get('soft'), dict):
        data_for_chart['soft'] = [
            {'name': k, 'score': v} for k, v in data_for_chart['soft'].items()
        ]
    generate_chartjs_data(data_for_chart, cfg['charts']['data'])
    cfg['charts']['images'] = {
        'big5': os.path.join(chart_dir, 'big5.png'),
        'riasec': os.path.join(chart_dir, 'riasec.png'),
        'values': os.path.join(chart_dir, 'values.png'),
        'ai': os.path.join(chart_dir, 'ai.png'),
        'soft': os.path.join(chart_dir, 'soft.png'),
    }
    html_path = render_html(data, cfg)
    pdf_path = html_to_pdf(html_path, cfg['output']['pdf'])
    print(f'Successfully generated PDF report at {pdf_path}')


if __name__ == '__main__':
    main()
