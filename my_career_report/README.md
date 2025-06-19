# my_career_report

초보 기획자를 위한 간단한 보고서 생성 도구입니다. 데이터 파일과 Jinja2 템플릿을 활용해 자동으로 경력 리포트를 만들어 줍니다.

## 폴더 구조

- `config.yaml` – 결과물 위치와 차트 설정
- `data/` – 샘플 입력 데이터
- `charts/` – 차트 렌더링 모듈
- `templates/` – Jinja2 템플릿과 CSS
- `utils/` – HTML 생성과 PDF 변환을 돕는 도구

## 설치와 실행

```bash
pip install -r requirements.txt
npm install --silent
python generate_report.py
```

위 명령을 실행하면 `dist/report.html`과 `dist/report.pdf`가 생성됩니다.

`chartjs-plugin-datalabels` 오류가 보인다면 `my_career_report` 폴더에서 `npm install`을 다시 실행해 Node.js 패키지를 설치해 주세요.

### chartjs-node-canvas 관련

`chartjs-node-canvas`는 [`canvas`](https://github.com/Automattic/node-canvas) 모듈을 사용합니다. 이 모듈을 빌드하려면 Linux에서는 **Cairo**와 **Pango**가, Windows에서는 **Windows Build Tools**가 필요합니다. [node-canvas 설치 가이드](https://github.com/Automattic/node-canvas#installation)를 참고해 환경을 준비하세요.

### 한글 폰트

차트의 한글 레이블이 올바르게 보이려면 시스템에 **Noto Sans CJK** 폰트가 있어야 합니다. 폰트가 없으면 `generate_report.py`가 `NanumGothic`이나 `Malgun Gothic` 등 다른 한글 폰트로 대체합니다.

### WeasyPrint 의존성

WeasyPrint는 **cairo**와 **Pango** 같은 외부 라이브러리를 사용합니다. Linux에서는 `apt-get install libpangocairo-1.0-0 libcairo2`와 같이 패키지 관리자로 설치할 수 있습니다. Windows라면 [WeasyPrint 문서](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation)를 참고하여 번들 패키지를 설치하세요. 실행 중 `libgobject-2.0-0` 오류가 나오면 이 라이브러리가 빠진 것이므로, 공식 바이너리나 MSYS2 패키지를 설치하면 해결됩니다.

## 지속적 통합

`.github/workflows/ci.yml` 워크플로는 의존성을 설치하고 매 푸시마다 `generate_report.py`를 실행합니다. 생성된 PDF는 워크플로 아티팩트로 업로드됩니다.

## Chart.js 데이터

`generate_report.py`는 Chart.js 그래프를 그리기 위해 Node 스크립트를 호출하며, 웹 버전에서 사용할 데이터를 `charts/output/chart_data.json`에 JSON 형식으로 저장합니다. 또한 PDF에서 사용될 PNG 차트 이미지가 같은 폴더(`charts/output/`)에 생성됩니다.
