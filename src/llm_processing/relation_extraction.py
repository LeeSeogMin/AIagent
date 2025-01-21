import anthropic
from langchain.prompts import PromptTemplate
import json
from typing import List, Dict
from .knowledge_base import KnowledgeBaseManager

class RelationExtractor:
    def __init__(self, knowledge_manager: KnowledgeBaseManager):
        self.knowledge_manager = knowledge_manager
        
    def extract_relations(self, text: str, entities: List[Dict], ontology: Dict) -> List[Dict]:
        # 긴 텍스트를 더 작은 청크로 분할
        chunks = self._split_text(text, max_length=1000)
        all_relations = []
        
        for chunk in chunks:
            prompt = PromptTemplate(
                input_variables=["text", "entities", "ontology"],
                template="""온톨로지 규칙에 따라 다음 텍스트 조각에서 엔터티 간의 관계를 추출해주세요.
                응답은 반드시 완전한 JSON 형식이어야 합니다.
                
                텍스트: {text}
                엔터티 목록: {entities}
                온톨로지: {ontology}
                
                다음 JSON 형식으로 관계를 추출해주세요:
                {{
                    "relations": [
                        {{
                            "source": {{"type": "엔터티타입", "value": "엔터티값"}},
                            "target": {{"type": "엔터티타입", "value": "엔터티값"}},
                            "relation": "관계타입"
                        }}
                    ]
                }}
                """
            )
            
            response = self.knowledge_manager.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt.format(text=chunk, entities=entities, ontology=ontology)}
                ]
            )
            relations = self._parse_json_response(response.content)
            all_relations.extend(relations)
        
        return all_relations

    def _split_text(self, text: str, max_length: int) -> List[str]:
        """텍스트를 더 작은 청크로 분할"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > max_length:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
            
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks

    def _parse_json_response(self, response: str) -> List[Dict]:
        """LLM 응답을 파싱하여 JSON으로 변환"""
        try:
            # TextBlock 리스트인 경우 첫 번째 TextBlock의 text 속성을 사용
            if isinstance(response, list) and hasattr(response[0], 'text'):
                response = response[0].text

            response = response.strip()
            
            # JSON 블록 추출
            start = response.find('{')
            end = response.rfind('}') + 1
            if start == -1 or end == 0:
                print(f"JSON 형식을 찾을 수 없음: {response}")
                return []
            
            json_str = response[start:end]
            result = json.loads(json_str)
            
            # relations 키가 없는 경우 다른 키를 확인
            if 'relations' not in result:
                print(f"relations 키를 찾을 수 없음. 전체 응답: {result}")
                if isinstance(result, dict) and any(isinstance(v, list) for v in result.values()):
                    # 리스트 값을 가진 첫 번째 키를 사용
                    for key, value in result.items():
                        if isinstance(value, list):
                            return value
            return result.get('relations', [])
            
        except Exception as e:
            print(f"응답 처리 오류: {e}\n응답: {response}")
            return []

    def _find_last_complete_object(self, json_str: str) -> str:
        """마지막으로 완전한 JSON 객체를 찾음"""
        stack = []
        last_complete_end = -1
        
        for i, char in enumerate(json_str):
            if char == '{':
                stack.append(i)
            elif char == '}' and stack:
                start = stack.pop()
                if not stack:  # 최상위 객체가 완성됨
                    last_complete_end = i + 1
                
        if last_complete_end != -1:
            return json_str[:last_complete_end]
        return ""

    def _fix_quotes(self, json_str: str) -> str:
        """따옴표 관련 문제 수정"""
        # 1. 홀수 개의 따옴표 처리
        if json_str.count('"') % 2 != 0:
            json_str += '"'
        
        # 2. 잘린 문자열 복구
        lines = json_str.split('\n')
        fixed_lines = []
        for line in lines:
            if line.count('"') % 2 != 0:  # 라인의 따옴표가 홀수개
                if line.rstrip().endswith('"'):
                    line = line.rstrip()[:-1]  # 마지막 따옴표 제거
                else:
                    line = line.rstrip() + '"'  # 따옴표 추가
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)