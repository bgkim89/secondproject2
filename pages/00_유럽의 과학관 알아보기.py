import streamlit as st
import folium
from streamlit_folium import folium_static

st.set_page_config(layout="wide")

st.title("🌍 유럽 주요 과학 박물관 가이드")
st.markdown("유럽에는 흥미로운 과학 박물관들이 많이 있습니다. 이 가이드에서는 주요 과학 박물관들을 살펴보고, 각 박물관의 특징과 교육적 연계성을 알아보겠습니다.")

# 박물관 데이터
museums = {
    "런던 과학 박물관 (Science Museum London)": {
        "lat": 51.4988,
        "lon": -0.1749,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Science_Museum%2C_London.jpg/1280px-Science_Museum%2C_London.jpg",
        "homepage": "https://www.sciencemuseum.org.uk/",
        "established": "1857",
        "size": "약 45,000평방미터 (전시 공간)",
        "visitors": "약 300만 명/년 (코로나19 이전)",
        "fields": ["#산업혁명", "#기술사", "#의학", "#우주과학", "#에너지"],
        "curriculum": [
            "물리학I-역학과 에너지-산업혁명과 기술 발전",
            "화학I-물질의 특성-신소재 개발과 활용",
            "생명과학I-세포와 물질대사-질병의 발생과 예방"
        ]
    },
    "독일 박물관 (Deutsches Museum)": {
        "lat": 48.1299,
        "lon": 11.5833,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Deutsches_Museum_Main_Building_Munich.jpg/1280px-Deutsches_Museum_Main_Building_Munich.jpg",
        "homepage": "https://www.deutsches-museum.de/en/",
        "established": "1903",
        "size": "약 60,000평방미터 (세계 최대 규모의 과학기술 박물관 중 하나)",
        "visitors": "약 150만 명/년 (코로나19 이전)",
        "fields": ["#항공우주", "#전력", "#기계공학", "#정보통신", "#자연과학"],
        "curriculum": [
            "물리학II-전자기와 양자-전기와 자기의 활용",
            "화학II-화학 반응의 세계-금속과 비금속의 성질",
            "지구시스템과학-지구와 우주-우주 탐사의 역사"
        ]
    },
    "파리 과학 산업 박물관 (Cité des sciences et de l'industrie)": {
        "lat": 48.8938,
        "lon": 2.3888,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Citesciencesindustrie_paris.jpg/1280px-Citesciencesindustrie_paris.jpg",
        "homepage": "https://www.cite-sciences.fr/en/",
        "established": "1986",
        "size": "약 150,000평방미터 (유럽 최대 규모의 과학 박물관 중 하나)",
        "visitors": "약 300만 명/년 (코로나19 이전)",
        "fields": ["#환경과학", "#생명과학", "#뇌과학", "#디지털기술", "#천문학"],
        "curriculum": [
            "생명과학I-생태계와 환경-지속 가능한 환경",
            "지구시스템과학-기후 변화와 환경 생태-기후 변화의 원인과 영향",
            "융합과학 탐구-미래 사회와 과학기술-인공지능과 사회"
        ]
    },
    "네덜란드 니모 과학 기술 박물관 (NEMO Science Museum)": {
        "lat": 52.3736,
        "lon": 4.9126,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Nemo_Science_Museum_Amsterdam.jpg/1280px-Nemo_Science_Museum_Amsterdam.jpg",
        "homepage": "https://www.nemosciencemuseum.nl/en/",
        "established": "1997",
        "size": "약 8,000평방미터 (전시 공간)",
        "visitors": "약 60만 명/년",
        "fields": ["#상호작용적전시", "#어린이교육", "#물리학원리", "#화학실험", "#기술혁신"],
        "curriculum": [
            "물리학I-운동과 힘-생활 속의 힘과 운동",
            "화학I-화학 반응-일상생활 속의 화학 반응",
            "과학의 역사와 문화-과학과 예술-과학 기술의 사회적 영향"
        ]
    },
    "취리히 테크노라마 (Technorama)": {
        "lat": 47.5645,
        "lon": 8.7061,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Swiss_Science_Center_Technorama%2C_Winterthur%2C_Switzerland.jpg/1280px-Swiss_Science_Center_Technorama%2C_Winterthur%2C_Switzerland.jpg",
        "homepage": "https://www.technorama.ch/en/",
        "established": "1982",
        "size": "약 6,500평방미터 (전시 공간)",
        "visitors": "약 25만 명/년",
        "fields": ["#물리현상", "#화학반응", "#생물학실험", "#인지과학", "#체험학습"],
        "curriculum": [
            "물리학I-에너지 전환-에너지 보존 법칙",
            "화학I-물질의 상태-물질의 변화와 에너지",
            "생명과학I-생물의 다양성-생명 현상의 탐구"
        ]
    },
    "바르셀로나 코스모카이사 (CosmoCaixa)": {
        "lat": 41.4116,
        "lon": 2.1408,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/CosmoCaixa_Barcelona_02.jpg/1280px-CosmoCaixa_Barcelona_02.jpg",
        "homepage": "https://cosmocaixa.caixaforum.org/en/",
        "established": "2004 (기존 박물관 리모델링)",
        "size": "약 30,000평방미터 (전시 공간)",
        "visitors": "약 80만 명/년",
        "fields": ["#자연사", "#생물다양성", "#우주과학", "#지구과학", "#환경보존"],
        "curriculum": [
            "생명과학I-유전과 진화-생물의 진화",
            "지구과학I-지구의 변화-지구의 역사",
            "기후 변화와 환경 생태-생물 다양성의 중요성"
        ]
    }
}

# 지도 생성
m = folium.Map(location=[49.0, 10.0], zoom_start=4)

for name, info in museums.items():
    popup_html = f"""
    <h4>{name}</h4>
    <img src="{info['image']}" alt="{name}" width="200"><br>
    <p><b>공식 홈페이지:</b> <a href="{info['homepage']}" target="_blank">{info['homepage']}</a></p>
    <p><b>설립 연도:</b> {info['established']}</p>
    <p><b>규모:</b> {info['size']}</p>
    <p><b>연간 방문객 수:</b> {info['visitors']}</p>
    <p><b>주력 분야:</b> {" ".join(info['fields'])}</p>
    <p><b>2025년 고등학교 과학교과 연계:</b></p>
    <ul>
    """
    for item in info['curriculum']:
        popup_html += f"<li>{item}</li>"
    popup_html += "</ul>"

    folium.Marker(
        location=[info['lat'], info['lon']],
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=name
    ).add_to(m)

st.subheader("유럽 주요 과학 박물관 지도")
folium_static(m)

st.subheader("각 박물관 상세 정보")
for name, info in museums.items():
    st.markdown(f"---")
    st.header(name)

    col1, col2 = st.columns([1, 2])

    with col1:
        # use_column_width 대신 use_container_width 사용
        st.image(info['image'], caption=name, use_container_width=True)
        st.markdown(f"**공식 홈페이지:** [{info['homepage']}]({info['homepage']})")

    with col2:
        st.write(f"**설립 연도:** {info['established']}")
        st.write(f"**규모:** {info['size']}")
        st.write(f"**연간 방문객 수:** {info['visitors']}")
        st.write("**주력 분야:**")
        st.write(" ".join(info['fields']))
        st.write("**2025년 고등학교 과학교과 연계:**")
        for item in info['curriculum']:
            st.write(f"- {item}")

st.markdown("---")
st.markdown("본 가이드가 유럽의 과학 박물관을 방문하는 데 도움이 되기를 바랍니다. 즐거운 과학 탐험 되세요! 🔭")
