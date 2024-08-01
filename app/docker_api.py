import docker
import os
import binascii

# 상수 정의
DOCKER_START_PORT = 9000
DOCKER_END_PORT = 9999

# Docker 클라이언트 초기화
client = docker.from_env()

def create_and_run_container(container_name, port_mappings):
    unique_container_name = f"{container_name}_{binascii.hexlify(os.urandom(24)).decode()}"
    try:
        # Docker 컨테이너 생성 및 실행
        container = client.containers.run(
            "ubuntu",               # 이미지 이름
            detach=True,            # 백그라운드에서 실행
            tty=True,               # 터미널 연결
            name=unique_container_name,    # 컨테이너 이름
            ports=port_mappings     # 포트 포워딩
        )
        return {'success': True, 'container_id': container.id}  # 성공 시 컨테이너 ID 반환
    except docker.errors.APIError as e:
        return {'success': False, 'error': f'Docker API 오류 발생: {str(e)}'}
    except Exception as e:
        return {'success': False, 'error': f'오류 발생: {str(e)}'}


def get_container_info_by_id(container_id):
    try:
        # 컨테이너 객체를 가져오기
        container = client.containers.get(container_id)
        # 컨테이너 정보 조회
        info = {
            'ID': container.id,
            'Ports': container.attrs['NetworkSettings']['Ports']
        }
        return info
    except docker.errors.NotFound:
        return {'ID': container_id, 'Ports': 'Not found'}
    except docker.errors.APIError as e:
        return {'ID': container_id, 'Ports': f'Docker API 오류 발생: {str(e)}'}
    except Exception as e:
        return {'ID': container_id, 'Ports': f'오류 발생: {str(e)}'}

def get_used_ports():
    """현재 사용 중인 포트를 반환합니다."""
    used_ports = set()

    # 모든 실행 중인 컨테이너를 가져옵니다.
    for container in client.containers.list():
        for port_binding in container.attrs['HostConfig']['PortBindings'].values():
            for binding in port_binding:
                used_ports.add(binding['HostPort'])
                
    return used_ports

def find_available_ports(start=DOCKER_START_PORT, end=DOCKER_END_PORT, count=1):
    """사용 가능한 포트를 찾습니다."""
    used_ports = get_used_ports()
    available_ports = []

    for port in range(start, end + 1):
        if str(port) not in used_ports:
            available_ports.append(port)
            if len(available_ports) == count:
                return available_ports

    raise RuntimeError("No available ports in the specified range.")

