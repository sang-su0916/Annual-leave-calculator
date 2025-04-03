import streamlit as st
import pandas as pd
from datetime import datetime, date

st.set_page_config(page_title="연차 계산기", layout="wide")

def calculate_years_of_service(hire_year, current_year, fiscal_start_month):
    """입사년도와 현재년도를 기준으로 근무년수 계산"""
    current_month = datetime.now().month
    
    # 현재 회계연도 계산
    if current_month >= fiscal_start_month:
        fiscal_year = current_year
    else:
        fiscal_year = current_year - 1
    
    # 회계연도 기준 근무년수 계산
    if fiscal_start_month == 1:
        # 회계연도가 1월부터면 단순 계산
        years_of_service = fiscal_year - hire_year
    else:
        # 회계연도가 1월이 아닌 경우
        hire_month = 1  # 입사월 정보가 없으므로 기본값 1월로 설정
        
        if hire_month < fiscal_start_month:
            # 입사월이 회계연도 시작 전이면
            years_of_service = fiscal_year - hire_year
        else:
            # 입사월이 회계연도 시작 후이면
            years_of_service = fiscal_year - hire_year - 1
    
    return max(0, years_of_service)

def calculate_vacation_days(years_of_service, first_year=True):
    """근무년수에 따른 연차 일수 계산"""
    if years_of_service < 1:
        # 1년 미만 근무자는 근무 개월 수에 비례하여 연차 부여
        if first_year:
            # 현재 연도에 입사한 경우, 실제 근무 개월 수 계산
            months_worked = datetime.now().month
            return min(11, months_worked)
        else:
            # 과거 데이터를 위한 계산일 경우 11일로 고정
            return 11
    elif years_of_service < 3:
        # 1~2년 근무자
        return 15
    else:
        # 3년 이상 근무자: 15일 + 추가 일수 (최대 25일)
        additional_days = min(10, (years_of_service - 1) // 2)
        return 15 + additional_days

def main():
    st.title("🗓️ 연차 휴가 계산기")
    st.subheader("근로기준법에 따른 연차 계산")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("기본 정보 입력")
        hire_year = st.number_input("입사년도", min_value=1980, max_value=datetime.now().year, 
                                   value=2020, step=1, format="%d")
        
        fiscal_start_month = st.selectbox(
            "회계연도 시작 월", 
            options=list(range(1, 13)),
            format_func=lambda x: f"{x}월",
            index=0
        )
        
        current_date = datetime.now()
        current_year = current_date.year
        
        st.info(f"현재 날짜: {current_date.strftime('%Y년 %m월 %d일')}")
        
        if fiscal_start_month == 1:
            st.success(f"회계연도: {current_year}년 1월 1일 ~ {current_year}년 12월 31일")
        else:
            # 현재 회계연도 계산
            if current_date.month >= fiscal_start_month:
                fiscal_year_start = current_year
                fiscal_year_end = current_year + 1
            else:
                fiscal_year_start = current_year - 1
                fiscal_year_end = current_year
                
            st.success(f"회계연도: {fiscal_year_start}년 {fiscal_start_month}월 1일 ~ {fiscal_year_end}년 {fiscal_start_month-1 if fiscal_start_month > 1 else 12}월 {(date(fiscal_year_end, fiscal_start_month, 1) if fiscal_start_month > 1 else date(fiscal_year_end, 12, 1)).replace(day=1).replace(day=1) - date.timedelta(days=1).day}일")
    
    # 근무년수 계산
    years_of_service = calculate_years_of_service(hire_year, current_year, fiscal_start_month)
    
    # 연차 일수 계산
    vacation_days = calculate_vacation_days(years_of_service)
    
    with col2:
        st.subheader("📊 연차 계산 결과")
        
        result_df = pd.DataFrame({
            "항목": ["입사년도", "현재년도", "회계연도 시작월", "근무년수", "연차 일수"],
            "값": [hire_year, current_year, f"{fiscal_start_month}월", years_of_service, vacation_days]
        })
        
        st.dataframe(result_df, hide_index=True, use_container_width=True)
    
    # 최근 3년 연차 정보 계산
    st.subheader("📅 최근 3년 연차 정보")
    
    years_data = []
    total_vacation_days = 0
    
    for i in range(3):
        year = current_year - i
        past_years_of_service = calculate_years_of_service(hire_year, year, fiscal_start_month)
        past_vacation_days = calculate_vacation_days(past_years_of_service, first_year=(i==0))
        
        if past_years_of_service >= 0:  # 입사 이후만 계산
            years_data.append({
                "연도": year,
                "근무년수": past_years_of_service,
                "연차일수": past_vacation_days
            })
            total_vacation_days += past_vacation_days
    
    years_df = pd.DataFrame(years_data)
    st.dataframe(years_df, hide_index=True, use_container_width=True)
    
    st.metric("최근 3년 누적 연차일수", f"{total_vacation_days}일")
    
    # 추가 설명
    st.subheader("📝 연차 계산 안내")
    st.markdown("""
    **연차휴가 계산 방법 (근로기준법 기준)**
    
    * 1년 미만 근무: 근무 개월 수에 비례하여 최대 11일
    * 1년 이상 ~ 3년 미만 근무: 15일
    * 3년 이상 근무: 2년마다 1일씩 추가 (최대 25일)
    
    **회계연도와 입사연도의 관계**
    
    회계연도 시작월에 따라 근무년수와 연차일수가 달라질 수 있습니다. 
    회사의 회계연도 시작월을 정확히 입력하면 보다 정확한 연차 계산이 가능합니다.
    """)

if __name__ == "__main__":
    main()
