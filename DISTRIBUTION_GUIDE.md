# 🚀 Vibe-Code Auditor 배포 가이드

## 📦 친구/동료에게 배포하는 방법

### 방법 1: 직접 파일 전달 (추천)

#### 단계 1: 압축 파일 준비
현재 준비된 파일:
```
VibeAuditor-v1.9.0-Windows.tar.gz  (138MB)
```

**또는 Windows 탐색기 사용:**
1. `dist` 폴더 우클릭
2. "압축 파일로 보내기" → "VibeAuditor.zip" 선택
3. 생성된 zip 파일 확인

#### 단계 2: 파일 전달
**전달 방법 옵션:**
- 📧 이메일 (138MB, 용량 제한 확인)
- 💬 Slack, Discord, 카카오톡 (파일 전송)
- ☁️ Google Drive, Dropbox 공유 링크
- 💾 USB 메모리

#### 단계 3: 친구에게 설명할 내용

**받는 사람이 해야 할 일:**

```
1. 압축 파일 다운로드
2. 압축 해제 (우클릭 → "압축 풀기")
3. dist 폴더 안의 VibeAuditor.exe 더블클릭
4. 메뉴 선택:
   - 1번 → CLI 모드 (개발자용)
   - 2번 → UI 모드 (브라우저 자동 실행)
```

**설치 필요 없음!** 바로 실행됩니다.

---

### 방법 2: GitHub Release (권장 - 공개 배포)

#### 단계 1: GitHub Release 생성
1. GitHub 저장소 방문: https://github.com/lingger-lab/Vibe-Code-Auditor
2. 상단 "Releases" 탭 클릭
3. "Create a new release" 버튼 클릭

#### 단계 2: 릴리스 정보 입력
```yaml
Tag: v1.9.0
Title: Vibe-Code Auditor v1.9.0
Description: |
  # 🔍 Vibe-Code Auditor v1.9.0

  AI 기반 코드 품질 분석 플랫폼

  ## 주요 기능
  - 11개 프로그래밍 언어 지원
  - AI 코드 리뷰 (Claude API)
  - Web UI + CLI 인터페이스
  - PDF/HTML/JSON 리포트 생성
  - 비교 모드 (품질 추적)
  - 폴더 트리 뷰어

  ## 설치 방법
  1. 아래 `VibeAuditor-v1.9.0-Windows.zip` 다운로드
  2. 압축 해제
  3. `VibeAuditor.exe` 실행

  ## 요구사항
  - Windows 10 이상
  - Anthropic API Key (AI 분석 사용 시)

  ## 크기
  - 140MB (압축 파일)

  ## 변경사항
  [CHANGELOG.md 참고](https://github.com/lingger-lab/Vibe-Code-Auditor/blob/master/CHANGELOG.md)
```

#### 단계 3: 파일 업로드
- 드래그 앤 드롭으로 `VibeAuditor-v1.9.0-Windows.tar.gz` 업로드
- 또는 zip 파일 업로드

#### 단계 4: Publish Release

**친구에게 공유할 링크:**
```
https://github.com/lingger-lab/Vibe-Code-Auditor/releases/tag/v1.9.0
```

---

### 방법 3: 클라우드 스토리지 (대용량 파일)

#### Google Drive
1. Google Drive 업로드
2. 우클릭 → "공유 가능한 링크 만들기"
3. "링크가 있는 모든 사용자" 선택
4. 링크 복사 후 친구에게 전달

#### Dropbox
1. Dropbox 업로드
2. "공유" 버튼 클릭
3. "링크 만들기" 선택
4. 링크 복사 후 친구에게 전달

---

## 📝 친구에게 보낼 사용 가이드

### 빠른 시작 가이드 (복사해서 전달)

```markdown
# Vibe-Code Auditor 사용법

## 1. 다운로드 및 설치
1. 첨부된 파일 다운로드
2. 압축 해제 (우클릭 → 압축 풀기)
3. 설치 필요 없음!

## 2. 실행 방법

### 방법 A: UI 모드 (추천 - 초보자용)
1. `VibeAuditor.exe` 더블클릭
2. 메뉴에서 `2` 입력 (UI 모드)
3. 브라우저 자동 실행
4. 분석할 프로젝트 폴더 선택
5. "분석 시작" 버튼 클릭

### 방법 B: CLI 모드 (개발자용)
1. `VibeAuditor.exe` 더블클릭
2. 메뉴에서 `1` 입력 (CLI 모드)
3. 명령어 입력:
   ```
   --path C:\your\project --mode deployment
   ```

## 3. 주요 기능

### UI 모드 (웹 인터페이스)
- 📂 빠른 경로 선택 (바탕화면, 문서 폴더)
- 📊 실시간 진행 상황 표시
- 📄 결과 다운로드 (JSON, HTML, PDF)
- 🔄 분석 결과 비교
- 🌳 프로젝트 구조 보기

### CLI 모드 (터미널)
- 빠른 분석 속도
- 스크립트 자동화 가능
- CI/CD 파이프라인 통합

## 4. 지원 언어
Python, JavaScript, TypeScript, Go, Rust, PHP, Ruby, Kotlin, Swift, C#, Java

## 5. API 키 설정 (AI 분석 사용 시)
1. https://console.anthropic.com/ 방문
2. API Key 발급
3. 프로그램 실행 시 입력

## 문제 발생 시
- GitHub Issues: https://github.com/lingger-lab/Vibe-Code-Auditor/issues
- 또는 나에게 연락!
```

---

## 🔒 보안 참고사항

### 배포 시 주의사항
1. ✅ `.env` 파일은 포함하지 **마세요** (API 키 노출 위험)
2. ✅ 실행 파일만 배포 (`dist/` 폴더)
3. ✅ 소스 코드는 별도 제공 (GitHub)

### 친구에게 알려줄 보안 팁
```
⚠️ 중요:
- API 키를 절대 공유하지 마세요
- 신뢰할 수 있는 프로젝트만 분석하세요
- 회사 코드 분석 시 보안 정책 확인
```

---

## 📊 시스템 요구사항

### 최소 요구사항
- **OS**: Windows 10 이상
- **RAM**: 2GB 이상
- **저장공간**: 200MB 여유 공간
- **인터넷**: AI 분석 사용 시 필요

### 권장 요구사항
- **RAM**: 4GB 이상
- **인터넷**: 안정적인 연결

---

## 💡 유용한 팁

### 1. 대용량 프로젝트 분석
- 캐시 사용 옵션 활성화 (99% 속도 향상)
- 정적 분석만 수행 (AI 분석 건너뛰기)

### 2. 팀 협업
- JSON 결과 공유 → 동일한 결과 확인
- PDF 리포트 → 비개발자에게 전달

### 3. 정기적 품질 체크
- 히스토리 뷰어로 추세 확인
- 비교 모드로 개선 효과 측정

---

## 🆘 FAQ (친구가 자주 묻는 질문)

**Q: 설치가 필요한가요?**
A: 아니요! 압축 해제 후 바로 실행됩니다.

**Q: 어떤 언어를 지원하나요?**
A: Python, JavaScript, TypeScript, Go, Rust, PHP, Ruby, Kotlin, Swift, C#, Java

**Q: 무료인가요?**
A: 프로그램은 무료입니다. AI 분석은 Anthropic API 키가 필요합니다.

**Q: 인터넷이 필요한가요?**
A: 정적 분석은 오프라인 가능, AI 분석은 인터넷 필요

**Q: 안전한가요?**
A: 오픈소스입니다! GitHub에서 코드 확인 가능: https://github.com/lingger-lab/Vibe-Code-Auditor

**Q: Mac이나 Linux에서 실행되나요?**
A: 현재는 Windows만 지원합니다. Linux/Mac은 Python 소스코드로 실행 가능합니다.

---

## 📞 지원

문제가 발생하면:
1. GitHub Issues: https://github.com/lingger-lab/Vibe-Code-Auditor/issues
2. 나에게 직접 연락
3. README 문서 참고

---

**만든 이**: Vibe Coding Team
**버전**: 1.9.0
**최종 업데이트**: 2025-12-02
**라이선스**: MIT
