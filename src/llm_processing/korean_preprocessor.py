from konlpy.tag import Okt
# PyKoSpacing을 사용하려면 설치 필요: pip install git+https://github.com/haven-jeon/PyKoSpacing.git
# from pykospacing import Spacing

class KoreanPreprocessor:
    def __init__(self):
        self.okt = Okt()
        # self.spacing = Spacing() 

    def extract_keywords(self, text):
        """
        텍스트에서 명사, 동사, 형용자를 추출하는 함수
        
        Args:
            text (str): 처리할 텍스트
            
        Returns:
            list: 추출된 키워드 리스트
        """
        # 명사, 동사, 형용사 추출
        nouns = self.okt.nouns(text)
        verbs = [word for word, pos in self.okt.pos(text) if pos == 'Verb']  # 동사 추출
        adjectives = [word for word, pos in self.okt.pos(text) if pos == 'Adjective']  # 형용사 추출
        
        # 중복 제거 및 병합
        keywords = list(set(nouns + verbs + adjectives))
        
        # 한 글자 키워드 제거
        keywords = [word for word in keywords if len(word) > 1]
        
        return keywords

    def normalize_text(self, text):
        """
        텍스트 정규화 함수
        
        Args:
            text (str): 정규화할 텍스트
            
        Returns:
            str: 정규화된 텍스트
        """
        # 텍스트 정규화
        return self.okt.normalize(text) 

    # def correct_spacing(self, text):
    #     """띄어쓰기 교정 함수"""
    #     return self.spacing(text)
    #     return text  # 띄어쓰기 교정기 사용 시 주석 해제

    def remove_stopwords(self, words):
        """불용어 제거 함수"""
        stopwords = {'은', '는', '이', '가', '에', '에게', '에서', '부터'}
        return [word for word in words if word not in stopwords] 



# from soynlp.word import WordExtractor
# from soynlp.tokenizer import LTokenizer

# class KoreanPreprocessor:
#     def __init__(self):
#         self.word_extractor = WordExtractor()
#         self.ltokenizer = LTokenizer()

#     def extract_keywords(self, text):
#         """
#         텍스트에서 명사와 핵심 키워드를 추출하는 함수

#         Args:
#             text (str): 처리할 텍스트

#         Returns:
#             list: 추출된 키워드 리스트
#         """
#         self.word_extractor.train([text])  # 주어진 텍스트로 학습
#         words = self.word_extractor.extract()
#         keywords = [word for word in words if len(word) > 1]  # 한 글자 키워드 제거
#         return keywords

#     def normalize_text(self, text):
#         """
#         텍스트 정규화 함수 (Soynlp는 별도의 정규화 기능을 제공하지 않으므로, 
#         기본적인 텍스트 정제 기능을 사용합니다.)

#         Args:
#             text (str): 정규화할 텍스트

#         Returns:
#             str: 정규화된 텍스트
#         """
#         text = text.strip()  # 앞뒤 공백 제거
#         return text

#     def correct_spacing(self, text):
#         """띄어쓰기 교정 함수 (Soynlp는 띄어쓰기 교정 기능을 제공하지 않습니다.)"""
#         return text

#     def remove_stopwords(self, words):
#         """불용어 제거 함수"""
#         stopwords = {'은', '는', '이', '가', '에', '에게', '에서', '부터'}
#         return [word for word in words if word not in stopwords]
