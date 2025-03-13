import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import random

# 환경 변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="AI 프롬프트 생성기",
    page_icon="🤖",
    layout="wide"
)

# 스타일 적용
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .description {
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .prompt-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 헤더 섹션
st.markdown('<div class="main-header">AI 프롬프트 생성기</div>', unsafe_allow_html=True)
st.markdown('<div class="description">입력 텍스트를 기반으로 다양한 상황에 활용할 수 있는 프롬프트를 생성합니다.</div>', unsafe_allow_html=True)

# 프롬프트 템플릿 정의
TEMPLATE_DICT = {
    "비즈니스 성장": [
        {
            "title": "비즈니스 아이디어 생성기",
            "template": "\"[업종]에서 AI를 활용하여 최소한의 투자로 시작할 수 있는 온라인 비즈니스 10가지를 나열하세요. 각 아이디어에 대해 수익 모델, 시작 비용, 성장 전략을 포함해주세요.\"",
            "description": "새로운 비즈니스 아이디어를 발굴하고 수익 모델을 구체화하는 데 유용합니다."
        },
        {
            "title": "비즈니스 성장 전략",
            "template": "\"AI와 디지털 마케팅 도구를 활용하여 비즈니스 성장을 촉진하는 포괄적인 전략을 생성해주세요. 고객 확보, 유지, 매출 증대를 위한 구체적인 단계를 포함해주세요.\"",
            "description": "기존 비즈니스의 성장을 가속화하기 위한 전략을 수립하는 데 도움이 됩니다."
        },
        {
            "title": "타겟 고객 분석",
            "template": "\"ChatGPT가 [제품/서비스]의 고객인 것처럼 행동하도록 요청하세요. 다음 질문에 답변해달라고 요청하세요: 1) 구매 결정에 영향을 미치는 주요 요소는 무엇인가요? 2) 어떤 마케팅 메시지가 가장 효과적인가요? 3) 제품/서비스에서 개선되었으면 하는 점은 무엇인가요?\"",
            "description": "고객의 관점에서 제품이나 서비스를 평가하고 개선점을 파악하는 데 유용합니다."
        }
    ],
    "콘텐츠 마케팅": [
        {
            "title": "콘텐츠 기둥 전략",
            "template": "\"내 브랜드와 고객 관심사에 맞는 3-5개의 콘텐츠 기둥(주제)을 정의해주세요. [니치]에서 각 기둥에 대해 10개의 콘텐츠 아이디어를 제안해주세요.\"",
            "description": "일관된 콘텐츠 전략을 수립하고 주요 주제 영역을 정의하는 데 도움이 됩니다."
        },
        {
            "title": "바이럴 콘텐츠 생성기",
            "template": "\"[주제]에 대한 바이럴 소셜 미디어 포스트 5개를 작성해주세요. 각 포스트는 다음을 포함해야 합니다: 1) 주의를 끄는 훅, 2) 가치 있는 인사이트, 3) 개인적인 이야기 요소, 4) 명확한 행동 촉구.\"",
            "description": "소셜 미디어에서 높은 참여를 이끌어내는 콘텐츠를 작성하는 데 유용합니다."
        },
        {
            "title": "다중 훅 생성기",
            "template": "\"[주제]에 대한 15개의 훅을 생성해주세요. 다음 조건을 충족해야 합니다: - 업계의 일반적인 가정에 도전하는 내용 - 구체적인 숫자나 기간 포함 - 클릭베이트 전략을 사용하지 않으면서 호기심 유발 - [이상적인 고객]의 특정 통증점 해결 - 100-200자 이내 각 훅에 대해 심리적으로 설득력 있는 이유를 설명해주세요.\"",
            "description": "독자의 관심을 즉시 사로잡는 다양한 콘텐츠 도입부를 생성하는 데 도움이 됩니다."
        }
    ],
    "소셜 미디어": [
        {
            "title": "니치 및 대상 분석",
            "template": "\"인스타그램에서 가장 수익성이 높은 니치를 식별하고, 관심사, 행동, 콘텐츠 선호도를 포함한 대상 고객의 상세 프로필을 개발해주세요.\"",
            "description": "소셜 미디어 전략을 수립하기 전에 대상 고객을 명확하게 이해하는 데 유용합니다."
        },
        {
            "title": "바이럴 트렌드 식별기",
            "template": "\"소셜 미디어 플랫폼에서 높은 바이럴 가능성을 가진 [니치]의 트렌드 주제와 해시태그를 식별하는 프롬프트를 개발해주세요.\"",
            "description": "현재 트렌드를 활용하여 소셜 미디어 콘텐츠의 도달 범위를 확장하는 데 도움이 됩니다."
        },
        {
            "title": "참여 증대 훅 생성기",
            "template": "\"게시물에 대한 즉각적인 상호작용을 유도하는 5개의 강력한 도입부를 생성해주세요.\"",
            "description": "소셜 미디어 포스트의 참여율을 높이는 효과적인 도입부를 작성하는 데 유용합니다."
        }
    ],
    "개인 생산성": [
        {
            "title": "일일 루틴 자동화",
            "template": "\"모든 반복적인 일일 작업을 식별하고 이를 효율적으로 자동화하기 위한 특정 AI 도구와 워크플로우를 제안해주세요.\"",
            "description": "반복적인 작업을 자동화하여 시간을 절약하고 생산성을 높이는 데 도움이 됩니다."
        },
        {
            "title": "초효율적인 작업 스케줄러",
            "template": "\"우선순위가 높은 작업에 1시간을 할당하고 AI를 사용하여 일상적인 작업의 90%를 자동화하는 일일 일정 템플릿을 개발해주세요.\"",
            "description": "중요한 작업에 집중하고 나머지는 자동화하는 효율적인 일정을 수립하는 데 유용합니다."
        }
    ],
    "학습 및 교육": [
        {
            "title": "기술 숙달 로드맵",
            "template": "\"무료 온라인 리소스를 사용하여 [특정 기술]을 마스터하기 위한 상세한 학습 계획을 제시해주세요. 단계별 튜토리얼, 연습 문제, 이정표를 포함해주세요.\"",
            "description": "새로운 기술을 체계적으로 학습하기 위한 구조화된 계획을 수립하는 데 유용합니다."
        },
        {
            "title": "문법 및 문장 구조 교정",
            "template": "\"내 문장을 교정해주세요: [입력 문장]. 이유를 설명하고 대안을 제시해주세요.\"",
            "description": "언어 학습과 글쓰기 능력 향상에 도움이 됩니다."
        }
    ],
    "창의적 글쓰기": [
        {
            "title": "설득 프레임워크 구축기",
            "template": "\"[제품/서비스]를 마케팅하기 위한 단계별 설득 프레임워크를 개략적으로 설명하는 프롬프트를 생성해주세요. 감정적 트리거와 논리적 호소를 포함해주세요.\"",
            "description": "마케팅 메시지에 설득력을 더하는 구조화된 접근 방식을 개발하는 데 유용합니다."
        },
        {
            "title": "스토리텔링 마스터",
            "template": "\"[브랜드/제품]에 대한 강력한 스토리를 개발해주세요. 다음 요소를 포함해야 합니다: 1) 공감할 수 있는 주인공, 2) 극복해야 할 도전, 3) 변화의 순간, 4) 해결책으로서의 제품/서비스, 5) 영감을 주는 결론.\"",
            "description": "브랜드 메시지에 감정적 연결을 더하는 스토리텔링 기법을 개발하는 데 도움이 됩니다."
        }
    ],
    "문제 해결": [
        {
            "title": "다중 관점 분석",
            "template": "\"[문제/상황]을 다음 관점에서 분석해주세요: 1) 재무적 영향, 2) 고객 경험, 3) 운영 효율성, 4) 장기적 전략, 5) 경쟁 환경. 각 관점에서 주요 고려사항과 잠재적 해결책을 제시해주세요.\"",
            "description": "복잡한 문제를 여러 각도에서 검토하여 포괄적인 이해를 돕습니다."
        },
        {
            "title": "의사결정 매트릭스",
            "template": "\"[결정 사항]에 대한 의사결정 매트릭스를 만들어주세요. 다음을 포함해야 합니다: 1) 가능한 모든 선택지, 2) 각 선택지의 장단점, 3) 평가 기준과 가중치, 4) 각 선택지의 점수, 5) 최종 추천 및 근거.\"",
            "description": "구조화된 방식으로 복잡한 결정을 내리는 데 도움이 됩니다."
        }
    ]
}

# 사이드바 - API 키 입력
with st.sidebar:
    st.markdown('<div class="sub-header">설정</div>', unsafe_allow_html=True)
    api_key = st.text_input("Gemini API 키를 입력하세요", type="password")
    st.markdown("API 키가 없으신가요? [Google AI Studio](https://makersuite.google.com/app/apikey) 에서 발급받으세요.")
    
    st.markdown('<div class="sub-header">프롬프트 유형</div>', unsafe_allow_html=True)
    prompt_types = st.multiselect(
        "생성할 프롬프트 유형을 선택하세요",
        list(TEMPLATE_DICT.keys()),
        default=["비즈니스 성장", "콘텐츠 마케팅", "소셜 미디어"]
    )
    
    num_prompts = st.slider("생성할 프롬프트 수", min_value=3, max_value=10, value=5)

# 메인 섹션 - 텍스트 입력
st.markdown('<div class="sub-header">텍스트 입력</div>', unsafe_allow_html=True)
user_input = st.text_area("프롬프트를 생성할 텍스트를 입력하세요", height=200)

# 예시 텍스트 버튼
if st.button("예시 텍스트 사용"):
    example_text = """
    디지털 마케팅 전략을 개선하여 온라인 비즈니스의 성장을 가속화하고 싶습니다. 
    특히 소셜 미디어 채널을 통한 고객 참여 증대와 전환율 향상에 관심이 있습니다. 
    현재 콘텐츠 마케팅과 이메일 캠페인을 진행 중이지만, 기대한 만큼의 결과를 얻지 못하고 있습니다.
    """
    st.session_state.user_input = example_text
    user_input = example_text

# Gemini API 설정 및 프롬프트 생성 함수
def configure_genai(api_key):
    genai.configure(api_key=api_key)

def get_relevant_templates(prompt_types, num_prompts):
    """선택된 프롬프트 유형에서 템플릿을 가져옵니다."""
    all_templates = []
    for prompt_type in prompt_types:
        all_templates.extend(TEMPLATE_DICT.get(prompt_type, []))
    
    # 요청된 수보다 템플릿이 적으면 모든 템플릿 반환
    if len(all_templates) <= num_prompts:
        return all_templates
    
    # 랜덤하게 템플릿 선택
    return random.sample(all_templates, num_prompts)

def generate_prompts_with_templates(text, prompt_types, num_prompts):
    """템플릿을 기반으로 프롬프트를 생성합니다."""
    templates = get_relevant_templates(prompt_types, num_prompts)
    
    # 템플릿이 없는 경우 빈 결과 반환
    if not templates:
        return "선택한 프롬프트 유형에 대한 템플릿이 없습니다."
    
    result = "## 생성된 프롬프트\n\n"
    for i, template in enumerate(templates, 1):
        result += f"### {i}. {template['title']}\n\n"
        result += f"**프롬프트:**\n{template['template']}\n\n"
        result += f"**설명:**\n{template['description']}\n\n"
        result += "---\n\n"
    
    return result

def generate_prompts_with_ai(text, prompt_types, num_prompts):
    """Gemini API를 사용하여 맞춤형 프롬프트를 생성합니다."""
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # 프롬프트 유형에 따른 시스템 프롬프트 생성
        system_prompt = f"""
        당신은 입력 텍스트를 분석하여 다양한 상황에 활용할 수 있는 프롬프트를 생성하는 전문가입니다.
        다음 텍스트를 분석하고, 선택된 유형({', '.join(prompt_types)})에 맞는 {num_prompts}개의 프롬프트를 생성해주세요.
        
        각 프롬프트는 다음 형식을 따라야 합니다:
        1. 제목: 프롬프트의 목적을 명확히 설명하는 제목
        2. 프롬프트: 실제 사용할 수 있는 프롬프트 텍스트 (큰따옴표로 묶어서 제공)
        3. 설명: 이 프롬프트가 어떤 상황에서 유용한지, 어떤 결과를 얻을 수 있는지 설명
        
        프롬프트는 구체적이고 실용적이어야 하며, 입력 텍스트의 맥락과 관련이 있어야 합니다.
        ChatGPT, Gemini 등 다양한 AI 모델에서 사용할 수 있는 형식으로 작성해주세요.
        
        다음은 좋은 프롬프트의 예시입니다:
        
        ### 1. 타겟 고객 분석
        
        **프롬프트:**
        "디지털 마케팅 캠페인을 위한 이상적인 고객 프로필을 개발해주세요. 다음을 포함해야 합니다: 1) 인구통계학적 특성, 2) 행동 패턴, 3) 통증점과 욕구, 4) 선호하는 커뮤니케이션 채널, 5) 구매 결정에 영향을 미치는 요소."
        
        **설명:**
        이 프롬프트는 마케팅 전략을 수립하기 전에 대상 고객을 명확하게 이해하는 데 도움이 됩니다. 구체적인 고객 프로필을 통해 더 효과적인 메시지와 채널 전략을 개발할 수 있습니다.
        """
        
        response = model.generate_content([system_prompt, text])
        return response.text
    except Exception as e:
        return f"오류가 발생했습니다: {str(e)}"

def generate_prompts(text, prompt_types, num_prompts, use_ai=True):
    """템플릿 또는 AI를 사용하여 프롬프트를 생성합니다."""
    if use_ai:
        return generate_prompts_with_ai(text, prompt_types, num_prompts)
    else:
        return generate_prompts_with_templates(text, prompt_types, num_prompts)

# 프롬프트 생성 옵션
generation_method = st.radio(
    "프롬프트 생성 방식 선택",
    ["AI 기반 맞춤형 프롬프트 생성", "템플릿 기반 프롬프트 생성"],
    index=0
)

# 프롬프트 생성 버튼
if st.button("프롬프트 생성하기"):
    if not api_key and generation_method == "AI 기반 맞춤형 프롬프트 생성":
        st.error("Gemini API 키를 입력해주세요.")
    elif not user_input:
        st.error("텍스트를 입력해주세요.")
    elif not prompt_types:
        st.error("최소 하나 이상의 프롬프트 유형을 선택해주세요.")
    else:
        with st.spinner("프롬프트를 생성 중입니다..."):
            # AI 기반 생성 방식 선택 시 Gemini API 설정
            if generation_method == "AI 기반 맞춤형 프롬프트 생성":
                configure_genai(api_key)
                use_ai = True
            else:
                use_ai = False
            
            # 프롬프트 생성
            generated_prompts = generate_prompts(user_input, prompt_types, num_prompts, use_ai)
            
            # 결과 표시
            st.markdown('<div class="sub-header">생성된 프롬프트</div>', unsafe_allow_html=True)
            st.markdown(generated_prompts)
            
            # 다운로드 버튼
            st.download_button(
                label="프롬프트 다운로드",
                data=generated_prompts,
                file_name="generated_prompts.txt",
                mime="text/plain"
            )

# 사용 방법 섹션
with st.expander("사용 방법"):
    st.markdown("""
    ### 사용 방법
    
    1. **API 키 입력**: 사이드바에 Gemini API 키를 입력합니다. API 키가 없는 경우 [Google AI Studio](https://makersuite.google.com/app/apikey) 에서 발급받을 수 있습니다.
    
    2. **프롬프트 유형 선택**: 생성하고자 하는 프롬프트의 유형을 선택합니다. 여러 유형을 동시에 선택할 수 있습니다.
    
    3. **프롬프트 수 설정**: 생성할 프롬프트의 개수를 설정합니다(3-10개).
    
    4. **텍스트 입력**: 프롬프트를 생성할 기반이 될 텍스트를 입력합니다. 구체적인 내용을 포함할수록 더 관련성 높은 프롬프트가 생성됩니다.
    
    5. **생성 방식 선택**: AI 기반 맞춤형 생성 또는 템플릿 기반 생성 중 선택합니다.
    
    6. **프롬프트 생성**: '프롬프트 생성하기' 버튼을 클릭하여 프롬프트를 생성합니다.
    
    7. **결과 다운로드**: 생성된 프롬프트를 텍스트 파일로 다운로드할 수 있습니다.
    """)

# 푸터
st.markdown("---")
st.markdown("© 2025 AI 프롬프트 생성기 | Powered by Gemini API")
