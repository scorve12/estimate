# 견적서 PDF 생성기

JSON 형식의 견적서 데이터를 HTML 템플릿을 통해 PDF 파일로 자동 변환하는 Python 프로그램입니다.

## 기능

- JSON 파일에서 견적서 데이터 읽기
- HTML 템플릿 기반으로 한글이 완벽하게 지원되는 PDF 생성
- data 디렉토리의 모든 JSON 파일을 한 번에 처리
- 깔끔하고 전문적인 견적서 레이아웃
- 템플릿 커스터마이징 가능

## 설치 방법

### 1. 필수 패키지 설치

```bash
pip install -r requirements.txt
```

**Ubuntu/Debian의 경우 추가 시스템 패키지 필요:**
```bash
sudo apt-get install python3-dev python3-pip python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

**macOS의 경우:**
```bash
brew install cairo pango gdk-pixbuf libffi
```

## 사용 방법

### 1. JSON 파일 준비

`data` 디렉토리에 견적서 JSON 파일을 준비합니다.

JSON 파일 형식:
```json
{
  "doc_number": "20251113-01",
  "date": "2025년 11월 13일",
  "total_amount": "970,000",
  "supply_price": "881,818",
  "tax_amount": "88,182",
  "receiver": {
    "name": "조선대학교 산학협력단",
    "manager": "나우진"
  },
  "supplier": {
    "name": "쉼표",
    "ceo": "나광엽",
    "reg_id": "508-09-72976",
    "address": "광주광역시 광산구 소촌로 152번길 53-17",
    "contact": "010-4223-9227"
  },
  "items": [
    {
      "name": "홍보용 포스터 디자인 제작",
      "quantity": 1,
      "price": "881,818",
      "total": "881,818"
    }
  ]
}
```

### 2. PDF 생성

모든 JSON 파일을 PDF로 변환:
```bash
python generate_pdf.py
```

특정 파일만 변환하려면 Python 스크립트를 수정하거나 직접 호출:
```python
from generate_pdf import EstimatePDFGenerator

generator = EstimatePDFGenerator()
generator.generate_pdf('data/wbs1.json', 'output/custom_name.pdf')
```

### 3. 결과 확인

생성된 PDF 파일은 `output` 디렉토리에 저장됩니다.

## 디렉토리 구조

```
estimate/
├── data/                  # JSON 견적서 파일 디렉토리
│   ├── wbs1.json
│   ├── wbs2.json
│   └── ...
├── template/              # HTML 템플릿 디렉토리
│   └── estimate.html      # 견적서 HTML 템플릿
├── output/                # 생성된 PDF 파일 디렉토리 (자동 생성)
│   ├── wbs1.pdf
│   ├── wbs2.pdf
│   └── ...
├── generate_pdf.py        # 메인 스크립트
├── requirements.txt       # 필수 패키지 목록
└── README.md             # 이 파일
```

## 템플릿 커스터마이징

`template/estimate.html` 파일을 수정하여 견적서 디자인을 자유롭게 변경할 수 있습니다.

템플릿에서 사용 가능한 변수:
- `{{ doc_number }}` - 문서 번호
- `{{ date }}` - 작성 날짜
- `{{ total_amount }}` - 총 금액
- `{{ supply_price }}` - 공급가액
- `{{ tax_amount }}` - 부가세
- `{{ receiver_name }}` - 수신자 회사명
- `{{ receiver_manager }}` - 수신자 담당자
- `{{ supplier_name }}` - 공급자 회사명
- `{{ supplier_ceo }}` - 공급자 대표자
- `{{ supplier_reg_id }}` - 사업자등록번호
- `{{ supplier_address }}` - 공급자 주소
- `{{ supplier_contact }}` - 공급자 연락처
- `{{ items_rows }}` - 품목 테이블 행 (자동 생성)

## JSON 필드 설명

- `doc_number`: 문서 번호
- `date`: 작성 날짜
- `total_amount`: 총 금액 (VAT 포함)
- `supply_price`: 공급가액
- `tax_amount`: 부가세
- `receiver`: 수신자 정보
  - `name`: 회사명
  - `manager`: 담당자명
- `supplier`: 공급자 정보
  - `name`: 회사명
  - `ceo`: 대표자명
  - `reg_id`: 사업자등록번호
  - `address`: 주소
  - `contact`: 연락처
- `items`: 품목 목록
  - `name`: 품목명
  - `quantity`: 수량
  - `price`: 단가
  - `total`: 금액

## 문제 해결

### 설치 오류가 발생할 때

WeasyPrint는 시스템 라이브러리에 의존합니다. 설치 오류가 발생하면 시스템 패키지를 먼저 설치하세요.

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3-dev python3-pip python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
pip install -r requirements.txt
```

**macOS:**
```bash
brew install cairo pango gdk-pixbuf libffi
pip install -r requirements.txt
```

**Windows:**
WeasyPrint는 GTK+ 라이브러리가 필요합니다. 다음 링크에서 GTK+ 설치:
https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

### 모듈을 찾을 수 없다는 오류가 날 때

```bash
pip install -r requirements.txt
```

## 기술 스택

- **WeasyPrint**: HTML을 PDF로 변환
- **Jinja2**: HTML 템플릿 엔진
- **Python 3**: 메인 프로그래밍 언어

## 라이선스

MIT License
