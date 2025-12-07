from fastapi import HTTPException, status


def bad_request(message: str):
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"error": message}
    )


def unsupported_file(message: str):
    return HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail={"error": message}
    )

