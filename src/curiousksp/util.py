import krpc


def _check_connection():
    try:
        with krpc.connect(name="curious::_check_connection") as c:
            return True
    except ConnectionRefusedError as e:
        print(f"Error: {e.strerror}")
        return False
