import os
import pandas as pd
from datetime import datetime
import pytz

class MetricsAnalyser:
    # BIG5 관련 컬럼 매핑
    big5_columns = {
        'E1': 'Ⅰ-1_E',
        'E2': 'Ⅰ-6_E (reverse)',
        'A1': 'Ⅰ-7_A',  # 우호성
            'A2': 'Ⅰ-2_A (reverse)',  # 우호성
        'C1': 'Ⅰ-3_C',
        'C2': 'Ⅰ-8_C (reverse)',
        'N1': 'Ⅰ-9_N',  # 신경성
            'N2': 'Ⅰ-4_N (reverse)',  # 신경성
        'O1': 'Ⅰ-5_O',
        'O2': 'Ⅰ-10_O(reverse)'
    }

    # RIASEC 관련 컬럼 매핑
    riasec_columns = {
        'R': ['Ⅱ-1_R', 'Ⅱ-2_R', 'Ⅱ-3_R', 'Ⅱ-4_R', 'Ⅱ-5_R'],
        'I': ['Ⅱ-6_I', 'Ⅱ-7_I', 'Ⅱ-8_I', 'Ⅱ-9_I', 'Ⅱ-10_I'],
        'A': ['Ⅱ-11_A', 'Ⅱ-12_A', 'Ⅱ-13_A', 'Ⅱ-14_A', 'Ⅱ-15_A'],
        'S': ['Ⅱ-16_S', 'Ⅱ-17_S', 'Ⅱ-18_S', 'Ⅱ-19_S', 'Ⅱ-20_S'],
        'E': ['Ⅱ-21_E', 'Ⅱ-22_E', 'Ⅱ-23_E', 'Ⅱ-24_E', 'Ⅱ-25_E'],
        'C': ['Ⅱ-26_C', 'Ⅱ-27_C', 'Ⅱ-28_C', 'Ⅱ-29_C', 'Ⅱ-30_C']
    }

    # 직업 가치관 관련 컬럼 매핑
    values_columns = {
        'A': ['Ⅲ-1_A', 'Ⅲ-2_A', 'Ⅲ-3_A'],  # 능력발휘 (Achievement)
        'I': ['Ⅲ-4_I', 'Ⅲ-5_I', 'Ⅲ-6_I'],  # 자율성 (Independence)
        'REC': ['Ⅲ-7_Rec', 'Ⅲ-8_Rec', 'Ⅲ-9_Rec'],  # 보상욕구 (Recognition)
        'REL': ['Ⅲ-10_Rel', 'Ⅲ-11_Rel', 'Ⅲ-12_Rel'],  # 대인관계 (Relationships)
        'S': ['Ⅲ-13_S', 'Ⅲ-14_S', 'Ⅲ-15_S'],  # 사회적 인정 (Support)
        'W': ['Ⅲ-16_W', 'Ⅲ-17_W', 'Ⅲ-18_W']  # 워라벨 (Working Conditions)
    }

    # AI 활용능력 관련 컬럼 매핑
    ai_columns = {
        'CU': ['Ⅳ-1_CU', 'Ⅳ-2_CU', 'Ⅳ-3_CU', 'Ⅳ-4_CU', 'Ⅳ-5_CU'],  # 인지적 이해 (Cognitive Understanding)
        'PS': ['Ⅳ-6_PS', 'Ⅳ-7_PS', 'Ⅳ-8_PS', 'Ⅳ-9_PS', 'Ⅳ-10_PS'],  # 프롬프트 숙련도 (Prompt Skill)
        'CE': ['Ⅳ-11_CE', 'Ⅳ-12_CE', 'Ⅳ-13_CE', 'Ⅳ-14_CE', 'Ⅳ-15_CE'],  # 검증 역량 (Critical Evaluation)
        'AO': ['Ⅳ-16_AO', 'Ⅳ-17_AO', 'Ⅳ-18_AO', 'Ⅳ-19_AO', 'Ⅳ-20_AO'],  # 도구 적용력 (Attitudinal Openness)
        'SA': ['Ⅳ-21_SA', 'Ⅳ-22_SA', 'Ⅳ-23_SA', 'Ⅳ-24_SA', 'Ⅳ-25_SA'],  # 자기 학습력 (Self-Efficacy & Adaptability)
        'CA': ['Ⅳ-26_CA', 'Ⅳ-27_CA', 'Ⅳ-28_CA', 'Ⅳ-29_CA', 'Ⅳ-30_CA'],  # 협업 능력 (Collaborative Ability)
        'ER': ['Ⅳ-31_ER', 'Ⅳ-32_ER', 'Ⅳ-33_ER', 'Ⅳ-34_ER', 'Ⅳ-35_ER']   # 윤리적 책임 (Ethical Responsibility)
    }

    # 비즈니스·소프트 스킬 관련 컬럼 매핑
    skills_columns = {
        'AT': ['Ⅴ-1_AT', 'Ⅴ-2_AT', 'Ⅴ-3_AT'],  # 분석적 사고 (Analytical Thinking)
        'PS': ['Ⅴ-4_PS', 'Ⅴ-5_PS', 'Ⅴ-6_PS'],  # 문제해결 능력 (Problem-solving Skills)
        'CR': ['Ⅴ-7_CR', 'Ⅴ-8_CR', 'Ⅴ-9_CR'],  # 창의력 (Creativity)
        'CM': ['Ⅴ-10_CO', 'Ⅴ-11_CO', 'Ⅴ-12_CO'],  # 커뮤니케이션 (Communication)
        'CC': ['Ⅴ-13_CC', 'Ⅴ-14_CC', 'Ⅴ-15_CC'],  # 협업역량 (Collaboration Capabilities)
        'LD': ['Ⅴ-16_LE', 'Ⅴ-17_LE', 'Ⅴ-18_LE'],  # 리더십 (Leadership)
        'SL': ['Ⅴ-19_SL', 'Ⅴ-20_SL', 'Ⅴ-21_SL'],  # 자기주도학습 (Self-paced Learning)
        'AD': ['Ⅴ-22_AD', 'Ⅴ-23_AD', 'Ⅴ-24_AD'],  # 적응력 (Adaptability)
        'RS': ['Ⅴ-25_RE', 'Ⅴ-26_RE', 'Ⅴ-27_RE'],  # 회복력 (Resilience)
        'EM': ['Ⅴ-28_EM', 'Ⅴ-29_EM', 'Ⅴ-30_EM'],  # 공감 능력 (Empathy)
        'IN': ['Ⅴ-31_IN', 'Ⅴ-32_IN', 'Ⅴ-33_IN'],  # 주도성 (Initiative)
        'DC': ['Ⅴ-34_DC', 'Ⅴ-35_DC', 'Ⅴ-36_DC']   # 디지털 역량 (Digital Capabilities)
    }

    def __init__(self):
        # 절대 경로 사용
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.raw_data_dir = os.path.join(current_dir, 'data', '01_raw_data')
        self.processed_data_dir = os.path.join(current_dir, 'data', '02_metrics_data')
        
        print(f"초기화 - 원본 데이터 디렉토리: {self.raw_data_dir}")
        print(f"초기화 - 처리된 데이터 디렉토리: {self.processed_data_dir}")
        
        # 입력 데이터 디렉토리
        self.university_dir = os.path.join(self.raw_data_dir, '01_university')
        self.workers_dir = os.path.join(self.raw_data_dir, '02_workers')
        self.student_dir = os.path.join(self.raw_data_dir, '03_student')
        
        # 출력 디렉토리가 없으면 생성
        try:
            os.makedirs(self.processed_data_dir, exist_ok=True)
            print(f"출력 디렉토리 생성/확인 완료: {self.processed_data_dir}")
        except Exception as e:
            print(f"출력 디렉토리 생성 중 오류 발생: {e}")
    
    def process_data(self):
        """각 대상별 데이터를 처리하고 지표를 계산하는 메인 함수"""
        print("데이터 처리를 시작합니다...")
        
        # 한국 시간대 설정
        kr_tz = pytz.timezone('Asia/Seoul')
        current_date = datetime.now(kr_tz)
        
        # 일별 넘버링 초기화
        self.daily_counter = 1
        
        # 대학생 데이터 처리
        university_files = self._get_csv_files(self.university_dir)
        print(f"처리할 파일 목록: {university_files}")
        
        for file in university_files:
            print(f"\n파일 처리 중: {file}")
            try:
                # 한글 인코딩 문제 해결을 위해 'utf-8-sig' 인코딩 사용
                data = pd.read_csv(file, encoding='utf-8-sig')
                print("UTF-8-SIG 인코딩으로 파일을 성공적으로 읽었습니다.")
            except UnicodeDecodeError:
                # utf-8-sig로 안되면 cp949 시도
                try:
                    data = pd.read_csv(file, encoding='cp949')
                    print("CP949 인코딩으로 파일을 성공적으로 읽었습니다.")
                except Exception as e:
                    print(f"파일 읽기 오류 (CP949): {file}, 오류: {e}")
                    continue
            except Exception as e:
                print(f"파일 처리 오류: {file}, 오류: {e}")
                continue

            # 컬럼명 확인 및 출력
            print("\n=== 데이터 컬럼 목록 ===")
            for i, col in enumerate(data.columns):
                print(f"{i}. 컬럼명: {col}")
            print("=== 컬럼 목록 끝 ===")

            # BIG5 관련 컬럼 매핑
            big5_columns = {
                'E1': '로-1_E',
                'E2': '로-6_E (reverse)',
                'A1': '로-7_A',  # 우호성
            'A2': '로-2_A (reverse)',  # 우호성
                'C1': '로-3_C',
                'C2': '로-8_C (reverse)',
                'N1': '로-9_N',  # 신경성
            'N2': '로-4_N (reverse)',  # 신경성
                'O1': '로-5_O',
                'O2': '로-10_O(reverse)'
            }

            # 각 응답자별로 처리
            for _, row in data.iterrows():
                # 제출 날짜 추출 및 포맷팅
                submitted_at = pd.to_datetime(row['Submitted at'])
                date_str = submitted_at.strftime('%Y%m%d')
                
                # 파일명 생성
                counter_str = f"{self.daily_counter:04d}"
                source_type = 'university'  # 01_university 폴더에서 가져온 경우
                name = row['name'].encode('cp949').decode('cp949')
                
                filename = f"{date_str}_{counter_str}_{source_type}_{name}_metrics_data.txt"
                print(f"처리 중인 데이터: {name}, 제출일: {date_str}, 번호: {counter_str}")
                
                # BIG5 요인 분석 결과 계산
                big5_scores = self.calculate_big5_scores(row)
                
                # 결과 저장
                self.save_results(big5_scores, filename)
                
                # 카운터 증가
                self.daily_counter += 1
        
        # 직장인 및 학생 데이터 처리 로직 추가 예정
    
    def calculate_skills_scores(self, row):
        """비즈니스·소프트 스킬 점수 계산"""
        # 비즈니스·소프트 스킬 점수 계산
        skills_scores = {}

        for factor, columns in self.skills_columns.items():
            # 각 요인별 점수 계산 (3개 항목의 평균 * 20)
            factor_score = sum(float(row[col]) for col in columns) / 3 * 20
            skills_scores[factor] = factor_score

        return skills_scores

    def calculate_ai_scores(self, row):
        """AI 활용능력 점수 계산"""
        # AI 활용능력 점수 계산
        ai_scores = {}
        ai_averages = {
            'CU': 79.3,  # 인지적 이해 (Cognitive Understanding)
            'PS': 62.5,  # 프롬프트 숙련도 (Prompt Skill)
            'CE': 62.5,  # 검증 역량 (Critical Evaluation)
            'AO': 62.5,  # 도구 적용력 (Attitudinal Openness)
            'SA': 54.0,  # 자기 학습력 (Self-Efficacy & Adaptability)
            'CA': 62.5,  # 협업 능력 (Collaborative Ability)
            'ER': 62.5   # 윤리적 책임 (Ethical Responsibility)
        }

        for factor, columns in self.ai_columns.items():
            # 각 요인별 점수 계산 (5개 항목의 평균 * 20)
            factor_score = sum(float(row[col]) for col in columns) / 5 * 20
            ai_scores[factor] = factor_score

        return ai_scores, ai_averages

    def calculate_values_scores(self, row):
        """직업 가치관 점수 계산"""
        # 직업 가치관 점수 계산
        values_scores = {}
        values_averages = {
            'A': 72.5,    # 능력발휘 (Achievement)
            'I': 41.8,    # 자율성 (Independence)
            'REC': 33.3,  # 보상욕구 (Recognition)
            'REL': 46.1,  # 대인관계 (Relationships)
            'S': 56.0,    # 사회적 인정 (Support)
            'W': 44.5     # 워라벨 (Working Conditions)
        }

        for factor, columns in self.values_columns.items():
            # 각 요인별 점수 계산 (3개 항목의 평균 * 20)
            factor_score = sum(float(row[col]) for col in columns) / 3 * 20
            values_scores[factor] = factor_score

        return values_scores, values_averages

    def calculate_riasec_scores(self, row):
        """RIASEC 요인 분석 점수 계산"""
        # RIASEC 점수 계산
        riasec_scores = {}
        riasec_averages = {
            'R': 45.5,
            'I': 57.8,
            'A': 56.5,
            'S': 58.5,
            'E': 59.0,
            'C': 53.0
        }

        for factor, columns in self.riasec_columns.items():
            # 각 요인별 점수 계산 (5개 항목의 평균 * 20)
            factor_score = sum(float(row[col]) for col in columns) / 5 * 20
            riasec_scores[factor] = factor_score

        return riasec_scores, riasec_averages

    def calculate_big5_scores(self, row):
        """BIG5 요인 분석 점수 계산"""
        # BIG5 점수 계산
        score_1e = ((float(row[self.big5_columns['E1']]) + (8 - float(row[self.big5_columns['E2']]))) / 2) * (100 / 7)
        score_1a = ((float(row[self.big5_columns['A1']]) + (8 - float(row[self.big5_columns['A2']]))) / 2) * (100 / 7)
        score_1c = ((float(row[self.big5_columns['C1']]) + (8 - float(row[self.big5_columns['C2']]))) / 2) * (100 / 7)
        score_1n = ((float(row[self.big5_columns['N1']]) + (8 - float(row[self.big5_columns['N2']]))) / 2) * (100 / 7)
        score_1o = ((float(row[self.big5_columns['O1']]) + (8 - float(row[self.big5_columns['O2']]))) / 2) * (100 / 7)
        
        # 평균값 정의
        averages = {
            'E': 57.3,
            'A': 70.5,  # 우호성
            'C': 73.3,
            'N': 63.8,  # 신경성
            'O': 73.0
        }

        # RIASEC 점수 계산
        riasec_scores, riasec_averages = self.calculate_riasec_scores(row)

        # 직업 가치관 점수 계산
        values_scores, values_averages = self.calculate_values_scores(row)

        # AI 활용능력 점수 계산
        ai_scores, ai_averages = self.calculate_ai_scores(row)

        # 비즈니스·소프트 스킬 점수 계산
        skills_scores = self.calculate_skills_scores(row)
        
        # 결과 포맷팅
        results = [
            "이름: {}".format(row['name']),
            "생년: {}".format(row['birth']),
            "성별: {}".format(row['gender']),
            "학교명: {}".format(row['univ_name']),
            "전공: {}".format(row['univ_major']),
            "학년: {}".format(row['univ_grade']),
            "국가: {}".format(row["Respondent's country"]),
            "",
            "Ⅰ. 개인성향 BIG5 요인 분석",
            "",
            "| BIG-5 요인 | {name}님의 점수 | 평균값¹ | Δ Index |",
            "| 개방성 (O) | {:.1f} | {:.1f} | {:.1f} |".format(score_1o, averages['O'], score_1o - averages['O']),
            "| 성실성 (C) | {:.1f} | {:.1f} | {:.1f} |".format(score_1c, averages['C'], score_1c - averages['C']),
            "| 외향성 (E) | {:.1f} | {:.1f} | {:.1f} |".format(score_1e, averages['E'], score_1e - averages['E']),
            "| 우호성 (A) | {:.1f} | {:.1f} | {:.1f} |".format(score_1a, averages['A'], score_1a - averages['A']),
            "| 신경성 (N) | {:.1f} | {:.1f} | {:.1f} |".format(score_1n, averages['N'], score_1n - averages['N']),
            "",
            "> ¹ *Gosling et al.* (2003) TIPI, U.S. college students N = 1,812",
            "",
            "Ⅱ. 진로 관심도 RIASEC 분석",
            "",
            "| RIASEC 요인 | {name}님의 점수 | 평균값² | Δ Index |",
            "| 현실형(Realistic) | {:.1f} | {:.1f} | {:.1f} |".format(riasec_scores['R'], riasec_averages['R'], riasec_scores['R'] - riasec_averages['R']),
            "| 탐구형(Investigative) | {:.1f} | {:.1f} | {:.1f} |".format(riasec_scores['I'], riasec_averages['I'], riasec_scores['I'] - riasec_averages['I']),
            "| 예술형(Artistic) | {:.1f} | {:.1f} | {:.1f} |".format(riasec_scores['A'], riasec_averages['A'], riasec_scores['A'] - riasec_averages['A']),
            "| 사회형(Social) | {:.1f} | {:.1f} | {:.1f} |".format(riasec_scores['S'], riasec_averages['S'], riasec_scores['S'] - riasec_averages['S']),
            "| 진취형(Enterprising) | {:.1f} | {:.1f} | {:.1f} |".format(riasec_scores['E'], riasec_averages['E'], riasec_scores['E'] - riasec_averages['E']),
            "| 관습형(Conventional) | {:.1f} | {:.1f} | {:.1f} |".format(riasec_scores['C'], riasec_averages['C'], riasec_scores['C'] - riasec_averages['C']),
            "",
            "> ² Stoll et al. (2020) 독일 대학생 표본 T1, N = 2,368.",
            "",
            "Ⅲ. 직업 가치관 분석",
            "",
            "| 직업 가치관 요인 | {name}님의 점수 | 평균값³ | Δ Index |",
            "| 능력발휘 (Achievement) | {:.1f} | {:.1f} | {:.1f} |".format(values_scores['A'], values_averages['A'], values_scores['A'] - values_averages['A']),
            "| 자율성 (Independence) | {:.1f} | {:.1f} | {:.1f} |".format(values_scores['I'], values_averages['I'], values_scores['I'] - values_averages['I']),
            "| 보상욕구 (Recognition) | {:.1f} | {:.1f} | {:.1f} |".format(values_scores['REC'], values_averages['REC'], values_scores['REC'] - values_averages['REC']),
            "| 대인관계 (Relationships) | {:.1f} | {:.1f} | {:.1f} |".format(values_scores['REL'], values_averages['REL'], values_scores['REL'] - values_averages['REL']),
            "| 사회적 인정 (Support) | {:.1f} | {:.1f} | {:.1f} |".format(values_scores['S'], values_averages['S'], values_scores['S'] - values_averages['S']),
            "| 워라벨 (Working Conditions) | {:.1f} | {:.1f} | {:.1f} |".format(values_scores['W'], values_averages['W'], values_scores['W'] - values_averages['W']),
            "",
            "> ³ O*NET (미국 직업 정보시스템) WIL-P&P 메인 스터디(미국 고용센터 내담자·주니어 칼리지 학생, N=1,119) 기준",
            "",
            "Ⅳ. AI 활용능력 분석",
            "",
            "| AI 활용능력 요인 | {name}님의 점수 | 평균값⁴ | Δ Index |",
            "| 인지적 이해 (Cognitive Understanding) | {:.1f} | {:.1f} | {:.1f} |".format(ai_scores['CU'], ai_averages['CU'], ai_scores['CU'] - ai_averages['CU']),
            "| 프롬프트 숙련도 (Prompt Skill) | {:.1f} | {:.1f} | {:.1f} |".format(ai_scores['PS'], ai_averages['PS'], ai_scores['PS'] - ai_averages['PS']),
            "| 검증 역량 (Critical Evaluation) | {:.1f} | {:.1f} | {:.1f} |".format(ai_scores['CE'], ai_averages['CE'], ai_scores['CE'] - ai_averages['CE']),
            "| 도구 적용력 (Attitudinal Openness) | {:.1f} | {:.1f} | {:.1f} |".format(ai_scores['AO'], ai_averages['AO'], ai_scores['AO'] - ai_averages['AO']),
            "| 자기 학습력 (Self-Efficacy & Adaptability) | {:.1f} | {:.1f} | {:.1f} |".format(ai_scores['SA'], ai_averages['SA'], ai_scores['SA'] - ai_averages['SA']),
            "| 협업 능력 (Collaborative Ability) | {:.1f} | {:.1f} | {:.1f} |".format(ai_scores['CA'], ai_averages['CA'], ai_scores['CA'] - ai_averages['CA']),
            "| 윤리적 책임 (Ethical Responsibility) | {:.1f} | {:.1f} | {:.1f} |".format(ai_scores['ER'], ai_averages['ER'], ai_scores['ER'] - ai_averages['ER']),
            "",
            "> ⁴ Normative Means:",
            "> -- 인지적 이해: Liu et al. (2025), Generative AI Literacy (N=344)",
            "> -- 기술 역량·비판적 평가·태도 개방성·협업 능력·윤리적 책임감: Nong et al. (2024), AI Literacy Scale (N=302)",
            "> -- 자기효능감·적응력: Akuezuilo et al. (2015), Computer Self-Efficacy (N=129)",
            "",
            "Ⅴ. 비즈니스·소프트 스킬",
            "",
            "| 비즈니스·소프트 스킬 요인 | {name}님의 점수 |",
            "| 분석적 사고 (Analytical Thinking) | {:.1f} |".format(skills_scores['AT']),
            "| 문제해결 능력 (Problem-solving Skills) | {:.1f} |".format(skills_scores['PS']),
            "| 창의력 (Creativity) | {:.1f} |".format(skills_scores['CR']),
            "| 커뮤니케이션 (Communication) | {:.1f} |".format(skills_scores['CM']),
            "| 협업역량 (Collaboration Capabilities) | {:.1f} |".format(skills_scores['CC']),
            "| 리더십 (Leadership) | {:.1f} |".format(skills_scores['LD']),
            "| 자기주도학습 (Self-paced Learning) | {:.1f} |".format(skills_scores['SL']),
            "| 적응력 (Adaptability) | {:.1f} |".format(skills_scores['AD']),
            "| 회복력 (Resilience) | {:.1f} |".format(skills_scores['RS']),
            "| 공감 능력 (Empathy) | {:.1f} |".format(skills_scores['EM']),
            "| 주도성 (Initiative) | {:.1f} |".format(skills_scores['IN']),
            "| 디지털 역량 (Digital Capabilities) | {:.1f} |".format(skills_scores['DC'])
        ]
        
        return '\n'.join(results)
    
    def save_results(self, results, filename):
        """계산된 지표를 파일로 저장"""
        try:
            # 절대 경로 사용
            abs_processed_data_dir = os.path.abspath(self.processed_data_dir)
            print(f"저장 디렉토리: {abs_processed_data_dir}")
            
            # 디렉토리 생성
            os.makedirs(abs_processed_data_dir, exist_ok=True)
            
            # 파일 저장
            output_path = os.path.join(abs_processed_data_dir, filename)
            print(f"저장할 파일 경로: {output_path}")
            print(f"저장할 내용:\n{results}")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(results)
            print(f"결과가 성공적으로 저장되었습니다: {output_path}")
        except Exception as e:
            print(f"결과 저장 중 오류 발생: {e}")
            print(f"현재 작업 디렉토리: {os.getcwd()}")
            print(f"디렉토리 존재 여부: {os.path.exists(abs_processed_data_dir)}")
            print(f"디렉토리 접근 권한: {os.access(abs_processed_data_dir, os.W_OK) if os.path.exists(abs_processed_data_dir) else 'N/A'}")


    def _get_csv_files(self, directory):
        """지정된 디렉토리에서 CSV 파일 목록을 반환"""
        csv_files = []
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if file.endswith('.csv'):
                    csv_files.append(os.path.join(directory, file))
        return csv_files

def main():
    analyser = MetricsAnalyser()
    analyser.process_data()

if __name__ == '__main__':
    main()
