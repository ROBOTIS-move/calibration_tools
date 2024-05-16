

### Review 체크 리스트
* PR 제목 확인 
  > * RCfix에서 release으로의 PR과 같은 내용인지 확인
  > * '[RCfix {버전} to develop] {CHANGELOG.rst 한줄 요약}' 한글
  > * 예시: [RCfix 0.12.0-rc2 to develop] 로보티즈 도슨트 서비스 음성 파일 삭제

* PR 내용 확인
  > * ChangeLog가 잘 작성되어 있는지 확인 

* 자신의 업데이트 사항을 체크
  > * 개발에 참여한 사람이 자동으로 Reviewer로 지정
  > * Reviewer는 본인의 개발내용이 잘 적용되어 있는지 확인

* Conflict 해결
  > * Conflict가 발생했다면 본인이 수정한 내용에 대해 Conflict 해결

* 코드 리뷰 체크 리스트
  > * 자세한 내용: https://www.notion.so/robotis-move/5747695207b748dca39c17a964adf30c
  > * 변수, 함수, 클래스 등의 이름의 의도성
  > * 조건 캡술화
  > * 객체 생성의 유의미성
  > * 일관적인, 서술적인 이름을 사용
  > * 함수는 하나의 역할
  > * 클래스 단일 책임 원칙
  > * 옳바른 예외처리 사용
  > * 코딩 스타일 가이드 준수 (C++, Python, ROS, CUDA 등)

* Doxygen 리뷰 체크 리스트:
  > * 자세한 내용: https://www.notion.so/robotis-move/Doxygen-6266dc44abaa42519a15669d7f1d556a
  > * 팀원을 위한 작성
  > * 모국어로 작성
  > * 최신으로 유지
  > * 헤더파일 손상 최소화
  > * 중복 주석 최소화
  > * 파일, 클래스, 구조체, 멤버변수, 멤버함수, 일반함수에 사용
  > * 통일성 유지
  > * 불필요한 주석 자제
  > * But: 목적은 팀원을 위한 작업이므로 모든 사항을 지나치게 지킬 필요는 없다!
