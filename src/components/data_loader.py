def load_data(file_path):
    """텍스트 파일에서 데이터를 로드하는 함수."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines() if line.strip()]