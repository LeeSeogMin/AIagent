from neo4j import GraphDatabase
import os

class Neo4jClient:
    def __init__(self, uri, user, password):
        try:
            self.driver = GraphDatabase.driver(
                uri,
                auth=(user, password),
                max_connection_lifetime=3600,
                max_connection_pool_size=100
            )
            # 연결 테스트
            with self.driver.session() as session:
                print(f"Connecting with URI: {uri}, User: {user}")
                session.run("RETURN 1")
            print("Neo4j 데이터베이스 연결 성공")
        except Exception as e:
            print(f"Neo4j 데이터베이스 연결 실패: {str(e)}")
            raise

    def _sanitize_label(self, label: str) -> str:
        """Neo4j 레이블에 사용할 수 있도록 문자열 정제"""
        return label.replace(' ', '_')

    def create_node(self, label, properties):
        try:
            # 엔터티 이름 정규화
            properties["name"] = self._normalize_entity_name(properties["name"])
            
            # 레이블의 공백을 언더스코어로 변경
            safe_label = self._sanitize_label(label)
            
            with self.driver.session() as session:
                query = f"""
                MERGE (n:{safe_label} {{name: $name}}) 
                RETURN n
                """
                result = session.run(query, name=properties["name"])
                return result.single()
        except Exception as e:
            print(f"노드 생성 실패: {str(e)}")
            raise

    def _normalize_entity_name(self, name: str) -> str:
        """엔터티 이름 정규화
        1. 공백 표준화
        2. 특수문자 처리
        3. 대소문자 통일
        """
        normalized = name.strip()
        normalized = normalized.replace('_', ' ')
        normalized = ' '.join(normalized.split())  # 연속된 공백 제거
        return normalized

    def create_relationship(self, start_label, start_node_name, end_label, end_node_name, relation_type):
        try:
            # 레이블과 관계 타입의 공백을 언더스코어로 변경
            safe_start_label = self._sanitize_label(start_label)
            safe_end_label = self._sanitize_label(end_label)
            safe_relation_type = self._sanitize_label(relation_type)
            
            with self.driver.session() as session:
                query = f"""
                MATCH (a:{safe_start_label} {{name: $start_name}})
                MATCH (b:{safe_end_label} {{name: $end_name}})
                MERGE (a)-[r:{safe_relation_type}]->(b)
                RETURN type(r) as relation_type
                """
                result = session.run(
                    query,
                    start_name=start_node_name,
                    end_name=end_node_name
                )
                return result.single()
        except Exception as e:
            print(f"관계 생성 실패: {str(e)}")
            raise

    def close(self):
        try:
            if self.driver:
                self.driver.close()
                print("Neo4j 연결 종료")
        except Exception as e:
            print(f"Neo4j 연결 종료 실패: {str(e)}")

    def query_all_nodes(self):
        """모든 노드 조회"""
        with self.driver.session() as session:
            result = session.run("MATCH (n) RETURN n")
            return [record["n"] for record in result]

    def query_all_relationships(self):
        """모든 관계 조회"""
        with self.driver.session() as session:
            result = session.run("MATCH (n)-[r]->(m) RETURN n, r, m")
            return [(record["n"], record["r"], record["m"]) for record in result]