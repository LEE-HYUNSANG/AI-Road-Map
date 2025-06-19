# AI 진로 진단 리포트 생성기

이 저장소는 예시 데이터를 활용해 개인의 성향과 역량을 분석하고, HTML과 PDF 형태의 보고서를 자동으로 만들어 줍니다. 파이썬과 Node.js만 설치되어 있으면 누구나 간단히 실행해 볼 수 있습니다.

## 설치 방법

1. Python 3.11 이상과 Node.js 환경을 준비합니다.
2. `my_career_report` 폴더로 이동해 다음 명령을 실행하세요.

```bash
pip install -r requirements.txt
npm install --silent
```

처음 한 번만 실행하면 필요한 패키지가 모두 설치됩니다.

## 환경 점검

아래 명령을 실행해 Node와 Python이 정상적으로 설치되었는지 확인합니다.

```bash
node -v
npm ls --depth=0
python --version
```

## 리포트 생성

아래 명령을 실행하면 `dist` 폴더에 `report.html`과 `report.pdf`가 생성됩니다.

```bash
python generate_report.py
```

또는 스크립트와 패키지 설치를 한 번에 수행하려면:

```bash
bash run_report.sh
```

`report.html`에서 차트와 내용을 확인할 수 있으며, 동일한 내용이 `report.pdf`에도 포함됩니다.

## 참고 사항

- **그래프 이미지**
  - PDF 파일은 자바스크립트를 실행하지 못하므로, 보고서 생성 과정에서 Chart.js로 그래프 이미지를 미리 만들어 포함합니다.
  - `my_career_report/charts/output` 폴더의 PNG 파일은 `generate_report.py` 실행 시 자동으로 생성되며 `.gitignore`에 의해 버전 관리 대상에서 제외됩니다.
  - `npm install` 후 `python generate_report.py` 명령을 실행하면 필요한 이미지를 함께 생성합니다.
- **한글 폰트**
  - 시스템에 `Noto Sans CJK`나 `NanumSquare` 계열 폰트가 설치되어 있어야 한글이 올바르게 표시됩니다.
- **데이터 수정**
  - `data/sample_input.json` 파일을 원하는 값으로 수정해 나만의 리포트를 만들어 보세요.

간단한 예제로 시작했지만, 실제 기획 문서 제작이나 다른 데이터와 연동해 확장하는 등 다양한 방법으로 활용할 수 있습니다.
