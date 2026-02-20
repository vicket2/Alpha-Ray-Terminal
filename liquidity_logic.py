import requests
import json
import pandas as pd

class AlphaRaySingularity:
    def __init__(self):
        # 1. 인증 및 엔드포인트 설정
        self.fred_key = "c4fc6d8fa12c167e8252cc35cc59410f"
        self.tga_api = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/dts/dts_table_1?sort=-record_date&limit=1"
        self.fred_base = "https://api.stlouisfed.org/fred/series/observations"
        
        # 2. 감시할 별 3개짜리 핵심 지표 (Macro + Liquidity)
        self.indicators = {
            "Core_PCE": "PCEPILFE",      # 근원 개인소비지출
            "10Y_Yield": "DGS10",        # 미 10년물 국채금리
            "Unemployment": "UNRATE",    # 실업률
            "CPI": "CPIAUCSL",           # 소비자물가
            "RRP": "RRPONTSYD"           # 역레포 잔고 (유동성 완충지대)
        }

    def get_tga(self):
        res = requests.get(self.tga_api).json()
        return float(res['data'][0]['close_today_bal'])

    def get_fred(self, series_id):
        url = f"{self.fred_base}?series_id={series_id}&api_key={self.fred_key}&file_type=json&sort_order=desc&limit=1"
        res = requests.get(url).json()
        try:
            return float(res['observations'][0]['value'])
        except:
            return 0.0

    def run_analysis(self):
        tga = self.get_tga()
        pce = self.get_fred(self.indicators["Core_PCE"])
        yield_10y = self.get_fred(self.indicators["10Y_Yield"])
        
        # [Alpha Exit Score 공식]
        # 유동성이 많고(TGA 하락), 물가가 낮으며(PCE 하락), 금리가 안정될수록(10Y 하락) 점수 상승
        # 현재 기준값(2026.02) 대비 가중치 부여
        liquidity_factor = (921000 - tga) / 1000  # 921B 대비 방류량
        macro_factor = (2.5 - pce) * 20           # PCE 2.5% 목표 대비 압력
        yield_factor = (4.2 - yield_10y) * 10     # 10년물 4.2% 기준 압력
        
        exit_score = liquidity_factor + macro_factor + yield_factor
        
        status = "🔥 DANGER (Exit Now)" if exit_score < -10 else "⚠️ CAUTION" if exit_score < 10 else "✅ HOLD"
        
        return {
            "TGA_Balance": f"${tga/1000:.1f}B",
            "Core_PCE": f"{pce}%",
            "10Y_Yield": f"{yield_10y}%",
            "Alpha_Exit_Score": round(exit_score, 2),
            "Final_Status": status
        }

# 엔진 가동
if __name__ == "__main__":
    engine = AlphaRaySingularity()
    print(json.dumps(engine.run_analysis(), indent=4))
