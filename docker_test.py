import docker

# 상수 정의
DOCKER_START_PORT = 9000
DOCKER_END_PORT = 9999

# Docker 클라이언트 초기화
client = docker.from_env()

def create_and_run_container(container_name, port_mappings):
    try:
        # Docker 컨테이너 생성 및 실행
        container = client.containers.run(
            "ubuntu",               # 이미지 이름
            detach=True,            # 백그라운드에서 실행
            tty=True,               # 터미널 연결
            name=container_name,    # 컨테이너 이름
            ports=port_mappings     # 포트 포워딩
        )
        print(f'컨테이너가 성공적으로 생성되었습니다. ID: {container.id}')
        return container.id
    except docker.errors.APIError as e:
        print(f'Docker API 오류 발생: {str(e)}')
    except Exception as e:
        print(f'오류 발생: {str(e)}')

def get_container_info(container_id):
    try:
        # 컨테이너 객체를 가져오기
        container = client.containers.get(container_id)
        # 컨테이너 정보 조회
        info = {
            'ID': container.id,
            'Image': container.image.tags,
            'Status': container.status,
            'Ports': container.attrs['NetworkSettings']['Ports'],
            'Command': container.attrs['Config']['Cmd'],
            'Created': container.attrs['Created']
        }
        print(f'컨테이너 정보: {info}')
    except docker.errors.NotFound:
        print('지정된 컨테이너를 찾을 수 없습니다.')
    except docker.errors.APIError as e:
        print(f'Docker API 오류 발생: {str(e)}')
    except Exception as e:
        print(f'오류 발생: {str(e)}')

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

if __name__ == '__main__':
    container_name = 'my_container4'
    
    # 여러 개의 포트 매핑 예시
    available_ports = find_available_ports(count=5)  # 예를 들어 3개의 포트를 찾음
    print(available_ports)
    
    # 포트 매핑 설정
    port_mappings = {
        '22/tcp': available_ports[0],  # 포트 22를 available_ports[0]에 매핑
        '445/tcp': available_ports[1]  # 포트 445를 available_ports[1]에 매핑
    }
    create_and_run_container(container_name, port_mappings)
