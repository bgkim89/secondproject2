import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch

# gwpy는 LIGO/Virgo 데이터를 다루는 데 매우 유용합니다.
# pip install gwpy h5py matplotlib
try:
    from gwpy.timeseries import TimeSeries
    from gwpy.segments import Segment
    from gwpy.plot import Plot
except ImportError:
    st.error("`gwpy` 라이브러리가 설치되어 있지 않습니다. `pip install gwpy h5py matplotlib`을 실행하거나 `requirements.txt`에 추가했는지 확인해주세요.")
    st.stop()

# Streamlit 앱 설정
st.set_page_config(layout="wide")
st.title("LIGO 중력파 데이터 시각화 (GWOSC 데이터 기반)")
st.write("이 앱은 GWOSC(Gravitational-Wave Open Science Center)에서 특정 중력파 이벤트 또는 사용자가 지정한 시간 구간의 데이터를 가져와 시각화합니다.")
st.warning("1년치 데이터를 직접 로드하는 것은 매우 무거울 수 있습니다. 여기서는 특정 이벤트 또는 짧은 시간 구간의 데이터를 시각화합니다.")

---

## 1. 데이터 선택 옵션

데이터를 로드하는 방식을 선택할 수 있습니다.

data_source_option = st.radio(
    "어떤 방식으로 데이터를 가져오시겠습니까?",
    ("특정 중력파 이벤트 선택", "직접 시간 구간 지정"),
    help="1년치 데이터는 너무 방대하여 직접 로드하기 어렵습니다."
)

if data_source_option == "특정 중력파 이벤트 선택":
    st.subheader("A. 중력파 이벤트 선택")
    event_name = st.selectbox(
        "시각화할 중력파 이벤트를 선택하세요:",
        ["GW150914 (최초 탐지)", "GW170817 (중성자별 충돌)", "GW190412 (블랙홀-블랙홀)"],
        index=0 # 기본값 설정
    )

    detector = st.selectbox(
        "탐지기를 선택하세요:",
        ["H1 (Hanford)", "L1 (Livingston)"],
        index=0 # 기본값 설정
    )

    duration = st.slider(
        "이벤트 전후로 가져올 데이터 기간 (초):",
        min_value=1,
        max_value=128, # 너무 길면 로딩 시간이 오래 걸릴 수 있습니다.
        value=32,
        step=1,
        help="이벤트 시점을 중심으로 이 시간만큼의 데이터를 가져옵니다. 너무 길게 설정하면 앱이 느려질 수 있습니다."
    )

    # 이벤트별 UTC 시작 시간 (GWOSC에서 확인된 대략적인 시간)
    event_times = {
        "GW150914 (최초 탐지)": 1126259446, # UTC seconds
        "GW170817 (중성자별 충돌)": 1187008882, # UTC seconds
        "GW190412 (블랙홀-블랙홀)": 1239082262, # UTC seconds
    }
    
    # 선택된 이벤트의 중심 시간
    center_time = event_times[event_name]
    segment = Segment(center_time - duration / 2, center_time + duration / 2)

    if st.button(f"{event_name} ({detector}) 데이터 로드 및 시각화"):
        load_and_visualize(detector.split(' ')[0], segment)

else: # 직접 시간 구간 지정
    st.subheader("B. 시간 구간 직접 지정")
    st.info("시작 시간은 GPS 시간(Epoch)을 사용합니다. 예를 들어, 2015년 9월 14일 09:50:45 UTC는 1126259445 입니다.")

    gps_time_input = st.text_input(
        "데이터 시작 GPS 시간 (초):",
        value="1126259445", # GW150914 이벤트 근처
        help="GWOSC 데이터는 GPS 시간을 기준으로 합니다. GWOSC 웹사이트에서 특정 시간의 GPS 시간을 확인할 수 있습니다."
    )
    custom_duration = st.slider(
        "데이터 기간 (초):",
        min_value=1,
        max_value=600, # 최대 10분 정도로 제한 (스트림릿 클라우드 성능 고려)
        value=60,
        step=1,
        help="가져올 데이터의 총 기간입니다. 너무 길게 설정하면 앱이 느려질 수 있습니다."
    )
    detector_custom = st.selectbox(
        "탐지기를 선택하세요:",
        ["H1", "L1"],
        index=0
    )

    try:
        start_gps_time = int(gps_time_input)
        custom_segment = Segment(start_gps_time, start_gps_time + custom_duration)
        if st.button(f"지정된 시간 ({detector_custom}) 데이터 로드 및 시각화"):
            load_and_visualize(detector_custom, custom_segment)
    except ValueError:
        st.error("유효한 GPS 시간을 입력해주세요.")


---

## 2. 데이터 로드 및 시각화 함수

def load_and_visualize(detector, segment):
    st.info(f"{detector} 데이터 로드 중 (시작: {segment.start}, 기간: {segment.duration}초)... 잠시 기다려주세요. 이 과정은 네트워크 상태에 따라 시간이 걸릴 수 있습니다.")
    try:
        # GWOSC에서 데이터 스트레인(strain)을 가져옵니다.
        # 이 과정은 네트워크 상태에 따라 시간이 걸릴 수 있습니다.
        strain = TimeSeries.fetch_open_data(detector, segment.active[0].start, segment.active[0].duration, cache=True)

        st.success(f"{detector} 데이터 로드 완료! 총 {len(strain)} 샘플, {strain.duration:.2f} 초 데이터.")

        # 1. 시간 영역 파형 시각화
        st.subheader(f"{detector} - 시간 영역 파형")
        fig_waveform = strain.plot(figsize=(10, 4), color='teal', title=f"{detector} Strain Data")
        fig_waveform.set_xlabel("Time (s)")
        fig_waveform.set_ylabel("Strain")
        st.pyplot(fig_waveform)

        # 2. 파워 스펙트럼 밀도 (PSD) 시각화
        st.subheader(f"{detector} - 파워 스펙트럼 밀도 (PSD)")
        # PSD 계산을 위한 FFT 길이 및 오버랩 설정
        fftlength = min(4, strain.duration / 2) # 데이터 길이에 따라 조정
        if fftlength < 1: # 데이터가 너무 짧으면 PSD 계산 어려움
            st.warning("데이터 길이가 너무 짧아 PSD를 정확히 계산하기 어렵습니다. 더 긴 기간을 선택해주세요.")
            return

        psd = strain.psd(fftlength=fftlength, overlap=fftlength/2, window='hann')
        fig_psd = psd.plot(figsize=(10, 4), color='purple', title=f"{detector} Power Spectral Density")
        fig_psd.set_xlabel("Frequency (Hz)")
        fig_psd.set_ylabel("ASD (Hz$^{-1/2}$)")
        fig_psd.set_xscale("log")
        fig_psd.set_yscale("log")
        st.pyplot(fig_psd)

        # 3. 스펙트로그램 시각화 (시간-주파수 플롯)
        st.subheader(f"{detector} - 스펙트로그램")
        # 스펙트로그램 계산 및 플롯
        specgram_fft_length = min(1, strain.duration / 4) # 스펙트로그램 FFT 길이
        if specgram_fft_length < 0.1: # 너무 짧으면 계산 어려움
             st.warning("데이터 길이가 너무 짧아 스펙트로그램을 정확히 계산하기 어렵습니다. 더 긴 기간을 선택해주세요.")
             return
             
        specgram = strain.spectrogram(fftlength=specgram_fft_length, overlap=0.5, window='hann', frequency_resolution=1)
        # vmax 값을 조정하여 시각화 범위를 최적화할 수 있습니다.
        plot_spec = specgram.plot(figsize=(10, 6), cmap='viridis', vmin=1e-24, vmax=1e-20)
        plot_spec.colorbar(label='Strain (Hz$^{-1/2}$)')
        plot_spec.axes[0].set_yscale('log')
        plot_spec.axes[0].set_ylim(20, 1024) # 중력파 신호가 주로 나타나는 주파수 범위
        plot_spec.axes[0].set_title(f"{detector} Spectrogram")
        st.pyplot(plot_spec)

    except Exception as e:
        st.error(f"데이터를 로드하거나 처리하는 중 오류가 발생했습니다: {e}")
        st.info("GWOSC에서 데이터를 가져오는 데 시간이 걸리거나 네트워크 문제일 수 있습니다. 선택한 기간이 너무 길거나, 해당 시간에 데이터가 없을 수도 있습니다.")
        st.info("특정 이벤트의 정확한 시간 범위는 GWOSC 웹사이트에서 확인해주세요.")
