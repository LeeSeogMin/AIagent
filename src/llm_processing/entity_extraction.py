import anthropic
import json
from langchain.prompts import PromptTemplate
from typing import List, Dict
from .knowledge_base import KnowledgeBaseManager

from .korean_preprocessor import KoreanPreprocessor

class EntityExtractor:
    def __init__(self, knowledge_manager: KnowledgeBaseManager):
        self.knowledge_manager = knowledge_manager
        
    def analyze_domain(self, text: str) -> Dict:
        prompt = PromptTemplate(
            input_variables=["text"],
            template="""다음 텍스트의 도메인을 분석하고 적절한 온톨로지 구조를 제안해주세요.

텍스트: {text}

다음 형식으로 JSON 응답을 작성해주세요:
{{
    "domain": "도메인명",
    "entity_types": ["엔터티타입1", "엔터티타입2"],
    "relation_types": ["관계타입1", "관계타입2"],
    "rules": {{
        "엔터티타입1": ["가능한관계1", "가능한관계2"]
    }}
}}"""
        )
        
        response = self.knowledge_manager.client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt.format(text=text)}
            ]
        )
        return self._parse_json_response(response.content)
        
    def extract_entities(self, text: str, ontology: Dict) -> List[Dict]:
        prompt = PromptTemplate(
            input_variables=["text", "ontology"],
            template="""온톨로지 구조에 따라 엔터티를 추출해주세요.

온톨로지 구조:
{ontology}

텍스트: {text}

다음 JSON 형식으로 엔터티를 추출해주세요:
{{
    "entities": [
        {{
            "type": "엔터티타입",
            "value": "엔터티값",
            "metadata": {{
                "confidence": 0.95,
                "source": "텍스트 위치"
            }}
        }}
    ]
}}"""
        )
        
        response = self.knowledge_manager.client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt.format(text=text, ontology=ontology)}
            ]
        )
        return self._parse_json_response(response.content)

    def _parse_json_response(self, response: str) -> Dict:
        """LLM 응답을 파싱하여 JSON으로 변환"""
        try:
            # TextBlock 리스트인 경우 첫 번째 TextBlock의 text 속성을 사용
            if isinstance(response, list) and hasattr(response[0], 'text'):
                response = response[0].text

            # 응답에서 JSON 부분만 추출
            response = response.strip()
            # JSON 시작/끝 위치 찾기
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                return json.loads(json_str)
            else:
                print(f"JSON 형식을 찾을 수 없음: {response}")
                return {}
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}\n응답: {response}")
            return {}
        except Exception as e:
            print(f"응답 처리 오류: {e}\n응답: {response}")
            return {}