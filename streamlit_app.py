"""
Streamlit Cloud Entrypoint Wrapper
이 파일은 Streamlit Cloud가 자동으로 감지하는 표준 entrypoint입니다.
src/ui/app.py의 모든 내용을 import하여 동일한 기능을 제공합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
# Streamlit Cloud에서도 정상 작동하도록 상대 경로 사용
project_root = Path(__file__).parent
project_root_str = str(project_root)

if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)

# src.ui.app 모듈의 모든 내용을 import
# 이렇게 하면 src/ui/app.py의 모든 코드가 실행됩니다
try:
    from src.ui.app import *
except ImportError as e:
    # Import 오류 발생 시 명확한 오류 메시지 표시
    import streamlit as st
    st.error(f"❌ 모듈 import 오류: {str(e)}")
    st.info("💡 Streamlit Cloud 로그를 확인하여 자세한 오류 정보를 확인하세요.")
    raise

