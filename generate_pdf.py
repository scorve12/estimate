#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
견적서 PDF 생성기
JSON 파일로부터 HTML 템플릿을 사용하여 견적서를 PDF로 변환합니다.
"""

import json
import os
from pathlib import Path
from jinja2 import Template
from weasyprint import HTML


class EstimatePDFGenerator:
    """견적서 PDF 생성 클래스"""

    def __init__(self):
        """초기화"""
        self.templates = {}

    def load_template(self, template_name):
        """템플릿 로드 (캐싱)"""
        if template_name not in self.templates:
            template_path = f'template/{template_name}.html'
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"템플릿 파일을 찾을 수 없습니다: {template_path}")

            with open(template_path, 'r', encoding='utf-8') as f:
                self.templates[template_name] = Template(f.read())

        return self.templates[template_name]

    def load_json(self, json_path):
        """JSON 파일 로드"""
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def generate_items_html(self, items):
        """품목 리스트를 HTML 테이블 행으로 변환"""
        rows = []
        for item in items:
            row = f"""
                    <tr>
                        <td>{item.get('name', '')}</td>
                        <td>{item.get('quantity', '')}</td>
                        <td>{item.get('price', '')}</td>
                        <td>{item.get('total', '')}</td>
                    </tr>"""
            rows.append(row)
        return '\n'.join(rows)

    def calculate_item_total(self, item):
        """품목의 total 자동 계산 (quantity × price)"""
        try:
            quantity = int(str(item.get('quantity', 0)))
            price_str = str(item.get('price', '0')).replace(',', '')
            price = int(price_str)
            total = quantity * price
            return f"{total:,}"
        except (ValueError, TypeError):
            return "0"

    def calculate_totals(self, items, tax_rate=0.1):
        """품목 금액 합계 및 세금 자동 계산"""
        # 각 품목의 total 계산 및 합산
        supply_price = 0
        total_tax = 0
        total_quantity = 0

        for item in items:
            # total이 없으면 자동 계산
            if 'total' not in item or not item['total']:
                item['total'] = self.calculate_item_total(item)

            # total 값을 숫자로 변환 (콤마 제거)
            total_str = str(item.get('total', '0')).replace(',', '')
            try:
                item_total = int(total_str)
                supply_price += item_total

                # 각 품목의 세액 계산
                item_tax = int(item_total * tax_rate)
                item['tax_amount'] = f"{item_tax:,}"
                total_tax += item_tax
            except ValueError:
                supply_price += 0
                item['tax_amount'] = "0"

            # 수량 합계
            try:
                total_quantity += int(str(item.get('quantity', 0)))
            except ValueError:
                pass

        # 부가세 계산 (10%)
        tax_amount = int(supply_price * tax_rate)

        # 총 금액
        total_amount = supply_price + tax_amount

        # 천 단위 콤마 포맷
        return {
            'supply_price': f"{supply_price:,}",
            'tax_amount': f"{tax_amount:,}",
            'total_tax_amount': f"{total_tax:,}",
            'total_amount': f"{total_amount:,}",
            'total_quantity': total_quantity
        }

    def generate_pdf(self, json_path, output_path=None, template_override=None, doc_title='견 적 서'):
        """JSON 파일로부터 PDF 생성"""
        # 데이터 로드
        data = self.load_json(json_path)

        # 템플릿 이름 가져오기
        if template_override:
            template_name = template_override
        else:
            template_name = 'clean_gradient'  # 기본 템플릿

        # 템플릿 로드
        template = self.load_template(template_name)

        # 출력 파일명 결정: {JSON파일명}_{템플릿명}_{서류종류}.pdf
        json_filename = Path(json_path).stem
        if output_path is None:
            # doc_title에서 공백 제거하여 파일명으로 사용
            doc_title_filename = doc_title.replace(' ', '')
            output_path = f"output/{json_filename}_{template_name}_{doc_title_filename}.pdf"

        # output 디렉토리 생성
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # 템플릿에 전달할 데이터 준비
        receiver = data.get('receiver', {})
        supplier = data.get('supplier', {})
        items = data.get('items', [])

        # 금액 자동 계산 (JSON에 없는 경우)
        tax_rate = data.get('tax', 10) / 100  # JSON의 tax 값을 비율로 변환 (10 -> 0.1)
        calculated = self.calculate_totals(items, tax_rate)
        supply_price = data.get('supply_price', calculated['supply_price'])
        tax_amount = data.get('tax_amount', calculated['tax_amount'])
        total_amount = data.get('total_amount', calculated['total_amount'])

        # items에 total_str 추가
        for item in items:
            if 'total_str' not in item:
                item['total_str'] = item.get('total', '0')

        template_data = {
            # 기본 정보
            'title': doc_title,  # 문서 제목 (함수 파라미터로 전달)
            'doc_number': data.get('doc_number', ''),
            'date': data.get('date', ''),
            'tax': data.get('tax', 10),  # 세율 (%)
            'total_amount': total_amount,
            'supply_price': supply_price,
            'tax_amount': tax_amount,
            'total_tax_amount': calculated.get('total_tax_amount', tax_amount),
            'total_quantity': calculated.get('total_quantity', 0),
            # _str 변수들 (템플릿 호환성)
            'subtotal_str': supply_price,
            'tax_amount_str': tax_amount,
            'grand_total_str': total_amount,
            # estimate1, estimate3 형식 (개별 필드)
            'receiver_name': receiver.get('name', ''),
            'receiver_ceo': receiver.get('ceo', ''),
            'supplier_name': supplier.get('name', ''),
            'supplier_ceo': supplier.get('ceo', ''),
            'supplier_reg_id': supplier.get('reg_id', ''),
            'supplier_address': supplier.get('address', ''),
            'supplier_contact': supplier.get('contact', ''),
            'items_rows': self.generate_items_html(items),
            # estimate2 형식 (객체 전체)
            'receiver': receiver,
            'supplier': supplier,
            'items': items
        }

        # HTML 생성
        html_content = template.render(**template_data)

        # PDF로 직접 변환 (HTML 파일 저장 안 함)
        html = HTML(string=html_content)
        html.write_pdf(output_path)
        print(f"✓ PDF 생성 완료: {output_path} (템플릿: {template_name})")

        return output_path


def get_available_templates():
    """사용 가능한 템플릿 목록 가져오기"""
    template_dir = Path('template')
    if not template_dir.exists():
        return []

    templates = []
    for template_file in template_dir.glob('*.html'):
        templates.append(template_file.stem)
    return sorted(templates)


def select_template():
    """템플릿 선택 메뉴"""
    templates = get_available_templates()

    if not templates:
        print("오류: 사용 가능한 템플릿이 없습니다.")
        return None

    print("\n========================================")
    print("  견적서 템플릿 선택")
    print("========================================")
    print("\n사용 가능한 템플릿:")
    print()

    for i, template in enumerate(templates, 1):
        print(f"  {i}. {template}")

    print(f"  0. 모든 템플릿으로 생성 (기본값)")
    print()

    while True:
        try:
            choice = input("템플릿 번호를 선택하세요 (0-{}): ".format(len(templates)))

            if choice.strip() == '':
                return 'all'

            choice_num = int(choice)

            if choice_num == 0:
                return 'all'  # 모든 템플릿으로 생성
            elif 1 <= choice_num <= len(templates):
                selected = templates[choice_num - 1]
                print(f"\n✓ '{selected}' 템플릿을 선택했습니다.\n")
                return selected
            else:
                print(f"오류: 0-{len(templates)} 사이의 숫자를 입력하세요.")
        except ValueError:
            print("오류: 숫자를 입력하세요.")
        except KeyboardInterrupt:
            print("\n\n작업이 취소되었습니다.")
            return None


def main():
    """메인 함수"""
    try:
        generator = EstimatePDFGenerator()
    except FileNotFoundError as e:
        print(f"오류: {e}")
        return

    # 템플릿 선택
    selected_template = select_template()

    # data 디렉토리의 모든 JSON 파일 처리
    data_dir = Path('data')

    if not data_dir.exists():
        print("오류: data 디렉토리가 존재하지 않습니다.")
        return

    json_files = list(data_dir.glob('*.json'))

    if not json_files:
        print("오류: data 디렉토리에 JSON 파일이 없습니다.")
        return

    # 문서 타입 목록 (견적서, 거래명세서)
    doc_types = ['견 적 서', '거 래 명 세 서']

    # 모든 템플릿으로 생성하는 경우
    if selected_template == 'all':
        available_templates = get_available_templates()
        print(f"총 {len(json_files)}개의 데이터를 {len(available_templates)}개 템플릿으로, 2가지 서류 형식(견적서, 거래명세서)으로 처리합니다.\n")

        for json_file in json_files:
            for template in available_templates:
                for doc_type in doc_types:
                    try:
                        generator.generate_pdf(str(json_file), template_override=template, doc_title=doc_type)
                    except Exception as e:
                        print(f"✗ 오류 발생 ({json_file.name} - {template} - {doc_type}): {e}")
                        import traceback
                        traceback.print_exc()
    else:
        # 특정 템플릿만 선택한 경우
        print(f"총 {len(json_files)}개의 데이터를 2가지 서류 형식(견적서, 거래명세서)으로 처리합니다.\n")

        for json_file in json_files:
            for doc_type in doc_types:
                try:
                    generator.generate_pdf(str(json_file), template_override=selected_template, doc_title=doc_type)
                except Exception as e:
                    print(f"✗ 오류 발생 ({json_file.name} - {doc_type}): {e}")
                    import traceback
                    traceback.print_exc()

    print(f"\n모든 PDF 파일이 output 디렉토리에 생성되었습니다.")


if __name__ == '__main__':
    main()
