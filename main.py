import os
from dotenv import load_dotenv
from src.components.data_loader import load_data
from src.llm_processing.entity_extraction import EntityExtractor
from src.llm_processing.relation_extraction import RelationExtractor
from src.llm_processing.knowledge_base import KnowledgeBaseManager
from src.graph.neo4j_client import Neo4jClient

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

def main():
    # 연결 정보 출력하여 확인
    print(f"NEO4J_URI: {NEO4J_URI}")
    print(f"NEO4J_USER: {NEO4J_USER}")
    print(f"NEO4J_PASSWORD: {NEO4J_PASSWORD}")
    
    # 초기화
    knowledge_manager = KnowledgeBaseManager(ANTHROPIC_API_KEY)
    entity_extractor = EntityExtractor(knowledge_manager)
    relation_extractor = RelationExtractor(knowledge_manager)
    neo4j_client = Neo4jClient(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

    # 데이터 로드
    documents = load_data("data/news_articles.txt")
    
    for doc in documents:
        # 1. 도메인 분석 및 온톨로지 구조 설계
        ontology = entity_extractor.analyze_domain(doc)
        if not ontology:
            print("도메인 분석 결과가 빈 딕셔너리입니다.")
            continue
        print(f"도메인 분석 결과: {ontology}")
        
        # 2. 엔터티 추출
        entity_result = entity_extractor.extract_entities(doc, ontology)
        entities = entity_result.get('entities', [])
        print(f"추출된 엔터티: {entities}")
        
        # 3. 관계 추출
        relations = relation_extractor.extract_relations(doc, entities, ontology)
        print(f"추출된 관계: {relations}")
        
        # 4. Neo4j에 저장
        for entity in entities:
            neo4j_client.create_node(
                entity["type"],
                {"name": entity["value"], **entity["metadata"]}
            )
        
        for relation in relations:
            neo4j_client.create_relationship(
                relation["source"]["type"],
                relation["source"]["value"],
                relation["target"]["type"],
                relation["target"]["value"],
                relation["relation"]
            )

    # 저장된 데이터 확인
    print("\n=== 저장된 노드 ===")
    nodes = neo4j_client.query_all_nodes()
    for node in nodes:
        print(node)

    print("\n=== 저장된 관계 ===")
    relationships = neo4j_client.query_all_relationships()
    for source, relation, target in relationships:
        print(f"{source} -[{relation}]-> {target}")

    neo4j_client.close()

if __name__ == "__main__":
    main()