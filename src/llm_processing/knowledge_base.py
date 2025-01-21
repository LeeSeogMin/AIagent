from dataclasses import dataclass
from typing import List, Dict, Optional
from groq import Groq

@dataclass
class OntologyStructure:
    entity_types: List[str]
    relation_types: List[str]
    rules: Dict[str, List[str]]  # 엔터티 타입별 관계 규칙

@dataclass
class KnowledgeGraph:
    entities: List[Dict]
    relations: List[Dict]
    ontology: OntologyStructure

class KnowledgeBaseManager:
    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key)
        
    def initialize_expert_knowledge(self) -> str:
        return """당신은 온톨로지와 지식 그래프 전문가입니다.
        
        전문가로서의 역할:
        1. 텍스트 분석을 통한 도메인 이해
        2. 도메인별 적절한 온톨로지 구조 설계
        3. 일관된 지식 그래프 구축
        4. 데이터 품질 보장
        
        작업 과정:
        1. 텍스트의 도메인 특성 파악
        2. 도메인에 맞는 엔터티/관계 타입 정의
        3. 온톨로지 규칙에 따른 데이터 추출
        4. 추출된 데이터의 일관성 검증
        
        응답은 항상 정의된 형식을 따라주세요.""" 