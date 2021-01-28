import krpc


# TODO: this is no longer used, delete when sure that it serves no purpose whatsoever anymore
def _check_connection():
    try:
        with krpc.connect(name="curious::_check_connection") as c:
            return True
    except ConnectionRefusedError as e:
        print(f"Error: {e.strerror}")
        return False
