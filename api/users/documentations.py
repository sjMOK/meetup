from rest_framework import serializers

from .serializers import UserTypeSerializer


not_found_response = '"detail": "Not found."'


logout_view_operation_description = '''
쿠키로 넘긴 sessionid의 유저 로그아웃
sessionid에 대응되는 세션 데이터 서버에서 삭제 후 쿠키 삭제, csrftoken은 쿠키에서 삭제하지 않음
성공시 200 응답, 쿠키에 sessionid가 존재하지 않아도 200 응답(이 경우 서버에서 아무 작업도 하지 않음)
'''


login_view_operation_description = '''
body data의 username과 password에 일치하는 유저 로그인
유저의 세션 데이터 생성 후 해당 세션의 id를 쿠키에 담아서 response 반환 - 헤더의 Set-Cookie sessionid 확인
username과 password에 일치하는 유저 없을 시 400 에러(No matching user.)
쿠키에 이미 발급 받은 세션 담아서 보낼 경우 해당 세션의 만료 기한 연장 후 반환
'''

change_password_operation_description = '''
user 비밀번호 변경 요청
body의 current_password와 user의 현재 비밀번호가 일치해야 하며 현재 비밀번호와 변경하고자 하는 비밀번호가 달라야함
'''

user_create_operation_description = '''
user 생성 요청
body의 필드가 잘못된 형식일 경우 해당 필드 이름이 key, 이유가 value인 메세지와 함께 400 반환
'''

user_partial_update_operation_description = '''
user 데이터 변경 요청
변경할 필드만 body에 담으면 됨
body의 필드가 잘못된 형식일 경우 해당 필드 이름이 key, 이유가 value인 메세지와 함께 400 반환
일반 유저의 경우 name(이름), email(이메일)만 변경 가능, admin 유저의 경우 username(학번/교번), user_type(타입)도 변경 가능
'''

class UserResponse(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    name = serializers.CharField()
    email = serializers.CharField()
    user_type = UserTypeSerializer()


class UserListResponse(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = UserResponse(many=True)
