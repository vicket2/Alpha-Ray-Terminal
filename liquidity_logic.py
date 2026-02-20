import requests

def analyze_liquidity_master():
    # 1. 미 재무부 TGA 실시간 데이터 (Daily Treasury Statement)
    tga_api = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/dts/dts_table_1?sort=-record_date&limit=1"
    
    # 2. 연준(Fed) 데이터 시뮬레이션 (2026년 2월 현재 정책 수치 기반)
    # 실제 운영 시 FRED API(WALCL, RRPONTSYD) 연동 가능
    fed_assets = 6610000.0   # 연준 총 자산 (단위: 백만 달러)
    rrp_balance = 2800.0     # 역레포 잔고 (거의 고갈 상태로 가정)
    
    try:
        tga_resp = requests.get(tga_api).json()
        current_tga = float(tga_resp['data'][0]['close_today_bal'])
        date = tga_resp['data'][0]['record_date']
    except:
        return {"error": "API 연결 실패"}

    # 3. [천재적 분석 변수]: 실질 순유동성 (Net Liquidity)
    # 공식: Net Liquidity = Fed Assets - (TGA + RRP)
    net_liquidity = fed_assets - (current_tga + rrp_balance)

    # 4. [미래 예측]: 재무부 베센트(Besent) 장관의 스케줄
    march_target = 850000.0    # 3월 말 목표
    april_target = 1025000.0   # 4월 말 목표 (유동성 블랙홀)
    
    tga_drift = current_tga - march_target # 3월까지 풀려야 할 돈
    drain_velocity = (april_target - march_target) / 30 # 4월 하루평균 흡수량

    # 5. [결론 및 경보]
    status = "NEUTRAL"
    if current_tga > 900000:
        status = "LIQUIDITY_PRESSURE (FIRE_OFF)"
    if net_liquidity < 5650000:
        status = "CRITICAL_DANGER (MARGIN_CALL_RISK)"

    return {
        "date": date,
        "net_liquidity": f"${net_liquidity:,.0f}M",
        "tga_to_release": f"${tga_drift:,.0f}M (3월 호재)",
        "april_blackhole": f"${april_target - march_target:,.0f}M (4월 악재)",
        "status": status,
        "strategy": "3월 18~20일 사이 QLD 73-75달러 도달 시 빚투 전량 청산 권고"
    }

if __name__ == "__main__":
    print(analyze_liquidity_master())
